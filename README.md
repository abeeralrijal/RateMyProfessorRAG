# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

Off-campus housing information for students at Howard University — covering available housing options, leasing requirements, and other logistics students face when looking for a place to live near campus. This knowledge is valuable because official university channels point students to a short, curated list of partner listings and don't surface the lived experience of actually renting near campus: how responsive a landlord is, whether a building is safe or well-maintained, or what hidden costs and requirements come up during leasing. This system pulls together tenant reviews from different housing and review websites so students can see that on-the-ground context in one place before choosing where to live.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Howard Off-Campus Partners FAQ | Official housing FAQ page | https://howard.offcampuspartners.com/resources/article/5524-frequently-asked-questions |
| 2 | The Lanes at Union Market — Google Maps reviews | Scraped tenant reviews | https://maps.app.goo.gl/gCeygqGkUtPsWzaG8 |
| 3 | Clover at The Parks — Google Maps reviews | Scraped tenant reviews | https://maps.app.goo.gl/MgDBBtSYtM8wjmuNA |
| 4 | Vie Towers — Google Maps reviews | Scraped tenant reviews | https://maps.app.goo.gl/DDBBFPmxp6Hbh5Pt5 |
| 5 | Trellis House Apartments — Google Maps reviews | Scraped tenant reviews | https://maps.app.goo.gl/qq3GdLDvdx2BRx3D7 |
| 6 | Howard Student Affairs — housing tips article | University article | https://studentaffairs.howard.edu/articles/6-tips-finding-campus-housing |
| 7 | The Lanes property info sheet | University PDF | https://auxiliary.howard.edu/sites/auxiliary.howard.edu/files/2024-10/the%20lanes%20v2.pdf |
| 8 | Howard Real Estate Development & Capital Asset Management (REDCAM) | University real estate page | https://realestate.howard.edu/media/2396 |

Reviews for entries 2–5 were scraped directly from each property's Google Maps listing to capture first-hand tenant experiences not covered by official university sources.




---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:** I checked the actual review lengths across all four properties. The median review is about 225 characters and roughly half of all reviews are under 200 characters, but some run past 1,000 characters and a few go over 4,000. The FAQ and tips PDFs are made of longer paragraphs, usually a few hundred characters each. A 500 character chunk keeps most short reviews whole in a single chunk, so a one or two sentence review stays a complete thought instead of getting cut in half. Longer reviews and PDF paragraphs get split into two or more chunks. I split on sentence boundaries instead of a raw character cutoff, so a chunk never ends mid-sentence. The 100 character overlap means a fact sitting right at a chunk boundary still shows up in the neighboring chunk.

Before chunking, `ingest.py` loads and cleans the raw documents: it drops Google review entries with no written text (star ratings only), strips leading/trailing navigation and footer boilerplate from the PDF pages (e.g. "Back to Home", "Categories", "Was this article helpful?"), and parses the tabular shuttle schedule PDF into full sentences instead of leaving it as a raw table dump.

**Final chunk count:** 464 chunks across 279 cleaned documents (260 reviews, 13 schedule entries, 6 article pages).

---

## Sample Chunks

<!-- Paste 5 representative chunks from your document collection after running your ingestion pipeline.
     For each chunk, note which source document it came from.
     These must be actual text — not screenshots. -->

| # | Source document | Chunk text |
|---|----------------|------------|
| 1 | Google Maps reviews — Clover at The Parks | "I've lived at Clover at the Parks for almost three years, since the community was newly built, and my experience has only gotten better over time. Since Greystar took over management, living here has been wonderful. A special thank you to Chez the leasing manager, who has been incredibly responsive, professional, and helpful whenever I've needed assistance." |
| 2 | Google Maps reviews — Vie Towers | "I met a young man today, who goes by the name of Hezzy. He was very kind and helpful." |
| 3 | The Lanes at Union Market Shuttle Schedule (parsed from lanes_schedule.pdf) | "Weekday (Monday through Friday) The Lanes at Union Market Shuttle departures from Lanes APT: 6:00 AM, 7:00 AM, 8:00 AM, 9:00 AM, 10:00 AM, 11:00 AM, 12:00 PM, 1:00 PM, 2:00 PM, 3:00 PM, 4:00 PM, 5:00 PM, 6:00 PM, 7:00 PM, 8:00 PM, 9:00 PM, 10:00 PM, 11:00 PM. The shuttle leaves every 60 minutes. The first departure is 6:00 AM and the last departure is 11:00 PM." |
| 4 | Howard University Student Affairs — Off-Campus Housing Resources FAQ | "Frequently Asked Questions I'm interested in a property. How do I apply? You must independently contact or visit the property to apply. The application process may include filling out a lease application, providing a security deposit and/or application fee, and undergoing a credit check to be approved for the apartment. In some instances, a co-signer may be required. Do I have to sign up for a 12-month lease? Leases normally occur in 12-, 9-, 6-, and sometimes 3-month intervals." |
| 5 | Howard University Student Affairs — 6 Tips for Finding Off-Campus Housing | "If you decide to live with others, please ensure that all individuals involved are on the same page regarding living preferences. Are you early birds? Night owls? How often do you like to entertain guests? Remember, don't be afraid to ask questions! This will be a home that you all will share for the duration of the lease. If you need additional help, please view this list of questions to ask potential roommates." |

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2, run locally through sentence-transformers, with chunks stored in a persistent ChromaDB collection (cosine distance).

**Production tradeoff reflection:** If cost was not a constraint, I would consider a larger API-hosted model like OpenAI's text-embedding-3-large for better accuracy on casual, domain-specific review language, at the cost of per-request pricing, network latency, and sending data off the local machine.

---

## Retrieval Test Results

<!-- Run these 3 queries through your retrieval system and record the top returned chunks.
     For at least 2 of the 3, explain why the returned chunks are relevant to the query.
     Results must be text — not screenshots. -->

**Query 1:** What time does the first weekday Clover at the Parks shuttle depart, and from which stop?

Top returned chunks:
- (distance 0.106, Clover at the Parks Shuttle Schedule) "Weekday (Monday through Friday) Clover at the Parks Shuttle departures from Clover @ Park: 6:00 AM, 7:00 AM, ... The first departure is 6:00 AM and the last departure is 11:00 PM."
- (distance 0.136, Clover at the Parks Shuttle Schedule) the matching weekend schedule for the same stop
- (distance 0.172, Clover at the Parks Shuttle Schedule) the weekday schedule for the Georgia Ave & Howard Pl stop

Relevance explanation: The top result directly answers the question (6:00 AM from Clover @ Park) and nothing else in the corpus talks about shuttle departure times in this phrasing, so the embedding model matched it with very high confidence (distance well under 0.5). The next results are the same shuttle's other stops and day types, which is expected since they share almost identical sentence structure and vocabulary.

---

**Query 2:** What do tenants say about who manages Clover at the Parks and about the leasing manager there?

Top returned chunks:
- (distance 0.320, Google Maps reviews — Clover at The Parks) "Since Greystar took over management, living here has been wonderful. A special thank you to Chez the leasing manager, who has been incredibly responsive, professional, and helpful..."
- (distance 0.381, Google Maps reviews — Clover at The Parks) a review praising "the leasing staff" and a named staff member for a smooth apartment transfer
- (distance 0.404, Google Maps reviews — Clover at The Parks) a review saying "management truly cares about residents"

Relevance explanation: All three top chunks are Clover reviews that specifically talk about management or leasing staff, which is exactly what the query asks about. The single best match names both the management company (Greystar) and the leasing manager (Chez), giving a directly verifiable answer.

---

**Query 3:** According to Howard's off-campus housing FAQ, what should a student do if someone asks them to send money before seeing the apartment or meeting the landlord?

Top returned chunks:
- (distance 0.422, Howard University Student Affairs — 6 Tips for Finding Off-Campus Housing) a generic sign-off paragraph ("We hope these tips are helpful!... contact the Office of Off-Campus Housing...")
- (distance 0.441, Howard University Student Affairs — 6 Tips for Finding Off-Campus Housing) a disclaimer paragraph about the university not screening properties or landlords
- (distance 0.477, Google Maps reviews — Vie Towers) an unrelated review about slow maintenance response

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

```
You are a housing information assistant for Howard University students. Answer the user's
question using ONLY the information in the numbered context passages below. Do not use any
outside knowledge, even if you are confident it is correct, and do not guess or speculate
beyond what is written in the passages. Mention which passage number(s) support your answer.
If the passages do not contain enough information to answer the question, respond with
exactly: "I don't have enough information on that." and nothing else.
```

This is paired with two structural choices in `query.py`, not just the instruction text:
1. **Relevance filtering before generation.** Retrieval returns the top 5 chunks, but only chunks with a cosine distance of 0.65 or lower are ever passed to the LLM as context. If none of the top 5 chunks clear that bar, the system returns the refusal message directly and never calls the LLM at all, so a truly out-of-scope question cannot produce a plausible-sounding guess.
2. **Programmatic source attribution.** The source list shown to the user is built by the code from the metadata of the chunks that were actually sent to the model, not from anything the model writes. If the model still responds with the refusal sentence (because it read the passages and decided they don't answer the question), the code detects that exact string and clears the source list, so a refusal is never shown next to sources that were not actually used.

**How source attribution is surfaced in the response:** `ask()` returns a `sources` list built from the retrieved chunks' `source` metadata (deduplicated, in relevance order). The interface displays this under "Retrieved from" beneath the answer. The model is also asked to reference passage numbers inline in its answer text, but the `sources` list the user sees does not depend on the model doing that correctly.

---

## Example Responses

<!-- Provide at least 2 grounded responses (query + response + source attribution)
     and 1 out-of-scope query showing your system's refusal.
     All entries must be text — not screenshots. -->

**Grounded response 1**

Query: What time does the first weekday Clover at the Parks shuttle depart, and from which stop?

Response: "The first weekday Clover at the Parks shuttle departs at 6:00 AM from the Clover @ Park stop [1][5]."

Source attribution: Clover at the Parks Shuttle Schedule

---

**Grounded response 2**

Query: What do tenants say about who manages Clover at the Parks and about the leasing manager there?

Response: "Tenants say that Greystar is the company that manages Clover at the Parks (passage 1). They praise the leasing manager, Chez, as 'incredibly responsive, professional, and helpful whenever I've needed assistance' (passage 1). Other reviews note that the leasing staff is friendly and helpful, with a particular shout-out to 'P' for making an apartment transfer smooth and stress-free (passage 2). Overall, tenants describe the management team as caring about residents and the staff as attentive and exceptional (passages 3 and 5)."

Source attribution: Google Maps reviews — Clover at The Parks

---

**Out-of-scope query**

Query: What is the airspeed velocity of an unladen swallow?

System response (refusal): "I don't have enough information on that." (Sources: none — no retrieved chunk cleared the relevance threshold, so the system refused without ever calling the LLM.)

---

## Query Interface

<!-- Describe your query interface: what are the input fields, what does the output look like?
     Then provide a complete sample interaction transcript showing a real exchange. -->

**Input fields:** A single text box ("Your question") and an "Ask" button, built with Streamlit (`app.py`, run with `streamlit run app.py`).

**Output format:** Two sections below the input: "Answer" (the grounded response text) and "Retrieved from" (a bulleted list of the source document names the answer was actually drawn from, or a note that nothing was retrieved if the system refused).

---

**Sample Interaction Transcript**

<!-- Show a complete query → response exchange as it actually appears in your interface.
     Must be text — not a screenshot. -->

> **User:** What do tenants say about who manages Clover at the Parks and about the leasing manager there?

> **System:**
> **Answer:** Tenants say that Greystar is the company that manages Clover at the Parks (passage 1). They praise the leasing manager, Chez, as "incredibly responsive, professional, and helpful whenever I've needed assistance" (passage 1). Other reviews note that the leasing staff is friendly and helpful, with a particular shout-out to "P" for making an apartment transfer smooth and stress-free (passage 2). Overall, tenants describe the management team as caring about residents and the staff as attentive and exceptional (passages 3 and 5).
>
> **Retrieved from:**
> - Google Maps reviews — Clover at The Parks

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** According to Howard's off-campus housing FAQ, what should a student do if someone asks them to send money before seeing the apartment or meeting the landlord?

**Output:** The top 5 retrieved chunks were a generic closing paragraph from the tips article, a disclaimer about the university not screening landlords, and two unrelated apartment reviews. The chunk that actually contains the answer ("If you're asked to send money without seeing the apartments... SAY NO and report the scam to the Federal Trade Commission") ranked 8th, at distance 0.519, outside the top-5 the retrieval function returns.

**Root cause:** This traces back to chunking, not embedding. The chunk that holds the answer starts with a heading and a general lead-in sentence ("6. Beware of Renters Scams... please beware of rental scams by looking for the signs of phantom rentals... and landlords that manage to get false listings onto reputable websites") before it ever gets to the specific actionable instruction about sending money. Because my chunker packs sentences up to 500 characters, that lead-in sentence and the actionable sentence ended up in the same chunk, and the embedding represents the chunk as a whole. The generic scam-awareness framing pulled the chunk's embedding away from the specific "send money before seeing the apartment" phrasing in the query, while other chunks that just happen to share surface-level words with the query (like "questions" and "off-campus housing" in the sign-off paragraph) ranked higher.

**Change:** Split on paragraph or heading boundaries in addition to sentence boundaries for the article PDFs, so a numbered section like "6. Beware of Renters Scams" does not get merged with unrelated sign-off content in the surrounding text, and so a chunk stays focused on one specific instruction rather than mixing a general topic sentence with the actionable detail.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
