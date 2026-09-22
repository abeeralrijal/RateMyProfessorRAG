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

**Model used:**

**Production tradeoff reflection:**

---

## Retrieval Test Results

<!-- Run these 3 queries through your retrieval system and record the top returned chunks.
     For at least 2 of the 3, explain why the returned chunks are relevant to the query.
     Results must be text — not screenshots. -->

**Query 1:**

Top returned chunks:
-
-
-

Relevance explanation:

---

**Query 2:**

Top returned chunks:
-
-
-

Relevance explanation:

---

**Query 3:**

Top returned chunks:
-
-
-

Relevance explanation:

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Example Responses

<!-- Provide at least 2 grounded responses (query + response + source attribution)
     and 1 out-of-scope query showing your system's refusal.
     All entries must be text — not screenshots. -->

**Grounded response 1**

Query:

Response:

Source attribution:

---

**Grounded response 2**

Query:

Response:

Source attribution:

---

**Out-of-scope query**

Query:

System response (refusal):

---

## Query Interface

<!-- Describe your query interface: what are the input fields, what does the output look like?
     Then provide a complete sample interaction transcript showing a real exchange. -->

**Input fields:**

**Output format:**

---

**Sample Interaction Transcript**

<!-- Show a complete query → response exchange as it actually appears in your interface.
     Must be text — not a screenshot. -->

> **User:** 

> **System:** 

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

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

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
