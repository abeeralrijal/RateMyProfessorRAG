"""End-to-end grounded query: retrieve relevant chunks, then ask Groq's LLM to
answer using only those chunks. Source attribution is computed programmatically
from the retrieved chunks, not left to the model to add on its own.
"""
import os

from dotenv import load_dotenv
from groq import Groq

from retrieval import retrieve

load_dotenv()

MODEL_NAME = "openai/gpt-oss-20b"  # meta-llama/llama-4-scout-17b-16e-instruct is no longer served by Groq
TOP_K = 5
MAX_DISTANCE = 0.65  # chunks weaker than this are treated as "not relevant enough"

SYSTEM_PROMPT = (
    "You are a housing information assistant for Howard University students. "
    "Answer the user's question using ONLY the information in the numbered context "
    "passages below. Do not use any outside knowledge, even if you are confident it is "
    "correct, and do not guess or speculate beyond what is written in the passages. "
    "Mention which passage number(s) support your answer. "
    "If the passages do not contain enough information to answer the question, respond "
    "with exactly: \"I don't have enough information on that.\" and nothing else."
)

_client = None


def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


def build_context(hits: list[dict]) -> str:
    return "\n\n".join(f"[{i}] Source: {h['source']}\n{h['text']}" for i, h in enumerate(hits, start=1))


def ask(question: str) -> dict:
    hits = retrieve(question, k=TOP_K)
    relevant = [h for h in hits if h["distance"] <= MAX_DISTANCE]

    if not relevant:
        # no chunk was a good enough match — refuse without ever calling the LLM,
        # so an out-of-scope question can't produce a plausible-sounding guess.
        return {"answer": "I don't have enough information on that.", "sources": [], "retrieved": hits}

    user_message = f"Context:\n\n{build_context(relevant)}\n\nQuestion: {question}"
    response = get_client().chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
    )
    answer = response.choices[0].message.content.strip()

    if answer.startswith("I don't have enough information"):
        # the model read the context and decided it doesn't answer the question,
        # so there is nothing to attribute even though chunks were retrieved
        return {"answer": answer, "sources": [], "retrieved": relevant}

    sources = []
    for h in relevant:
        if h["source"] not in sources:
            sources.append(h["source"])

    return {"answer": answer, "sources": sources, "retrieved": relevant}


if __name__ == "__main__":
    test_questions = [
        "What time does the first weekday Clover at the Parks shuttle depart, and from which stop?",
        "What do tenants say about who manages Clover at the Parks and about the leasing manager there?",
        "According to Howard's off-campus housing FAQ, what should a student do if someone asks them to send money before seeing the apartment or meeting the landlord?",
        "What is the airspeed velocity of an unladen swallow?",
    ]
    for q in test_questions:
        result = ask(q)
        print(f"\nQ: {q}")
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")
