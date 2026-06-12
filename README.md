# The Unofficial Guide — Project 1

A Retrieval-Augmented Generation (RAG) system for UT Austin CS professor reviews.

---

## Domain

Student-generated knowledge about UT Austin CS professors and courses, drawn from Rate My Professors and Reddit. This knowledge is valuable because it contains honest insights about teaching styles, exam formats, grading policies, and course difficulty that official university sources never provide. A student trying to decide between professors for CS439 or understand what determines their grade in CS314 cannot find that information in any course catalog or department website.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors | Review page | documents/rmp_mike_scott.txt |
| 2 | Rate My Professors | Review page | documents/rmp_devangi_parikh.txt |
| 3 | Rate My Professors | Review page | documents/rmp_siddhartha_chatterjee.txt |
| 4 | Rate My Professors | Review page | documents/rmp_prashant_joshi.txt |
| 5 | Rate My Professors | Review page | documents/rmp_alison_norman.txt |
| 6 | r/UTAustin | Reddit thread | documents/reddit_cs439_mootaz_vs_norman.txt |
| 7 | r/UTAustin | Reddit thread | documents/reddit_comarch_vs_os.txt |
| 8 | r/UTAustin | Reddit thread | documents/reddit_cs312_professor.txt |
| 9 | r/UTAustin | Reddit thread | documents/reddit_incoming_cs_recommendations.txt |
| 10 | r/UTAustin | Reddit thread | documents/reddit_ut_cs_junior_rant.txt |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** The documents are almost entirely short, opinion-based reviews and Reddit comments (2–5 sentences each). 400 characters fits 1–2 complete reviews without merging unrelated opinions into one chunk. A larger chunk would blend multiple reviewers' opinions, making it harder to match specific queries. Overlap of 50 characters protects against splitting a single sentence across two chunks.

**Preprocessing:** Removed section dividers (`--- REVIEWS ---`), URL lines, and blank lines; collapsed whitespace to single spaces.

**Final chunk count:** 185

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (local, no API key).

**Production tradeoff reflection:** For production I would consider text-embedding-3-small (OpenAI) or all-mpnet-base-v2 for better accuracy on informal text. Tradeoffs to weigh: (1) all-MiniLM-L6-v2 has a 256-token context limit which fits our 400-char chunks but would need upgrading if chunks grew; (2) API-based models cost per token but offer better multilingual support; (3) local models avoid API latency; (4) a model fine-tuned on social/review text would handle slang like "goated" better than a general-purpose model.

---

## Sample Chunks

**Chunk 1 — `rmp_mike_scott.txt`**

```text
s: Extra credit, Amazing lectures, Test heavy Quality: 5.0 | Difficulty: 4.0 | Grade: B- | Dec 2025 Mike cares so much for his students it's insane. He loves teaching and it shows -- just go to his office hours. I was blown away by his patience with me every time I was insanely confused with something on an assignment or content. Don't cheat, and lock in early on those practice exams -- exams rewa
```

**Chunk 2 — `rmp_mike_scott.txt`**

```text
tes. The tests are fairly difficult and 90% of the grade, but he gives abundant past tests to help you prep. Tags: Inspirational, Respected, Test heavy Quality: 5.0 | Difficulty: 4.0 | Grade: A | Dec 2024 Mike Scott is a fantastic professor, a real gem within the UTCS department. His lectures are super engaging where it seems to be a conversation rather than a lecture. His class is super test heav
```

**Chunk 3 — `reddit_comarch_vs_os.txt`**

```text
Source: Reddit r/UTAustin Thread Title: CS majors: Comp Arch vs OS Total Comments: 4 I just finished CS429 and was wondering what people's thoughts are on OS. Was it about the same intensity as 429 or way harder? I have heard mixed opinions. I am registered for Gheith right now and I'm a bit nervous. Any insight would be greatly appreciated! afbl24: It's harder than comp arch, but it's mostly due
```

**Chunk 4 — `rmp_alison_norman.txt`**

```text
Professor: Alison Norman Department: Computer Science University of Texas at Austin Course: CS439 (Operating Systems) Overall Quality: 2.5/5 | Would Take Again: 35% | Difficulty: 4.6/5 Total Ratings: 166 Quality: 5.0 | Difficulty: 5.0 | Grade: A | May 2026 Looking past the grading scheme (which is confusing), Norman is one of the best professors in UTCS. The class is meant to be hard,
```

**Chunk 5 — `reddit_cs439_mootaz_vs_norman.txt`**

```text
Source: Reddit r/UTAustin Thread Title: Is Mootaz better than Norman for CS439? The positive re Norman is that she does have a VERY good sequence of challenging projects that build nicely upon each other. It's a sequence that's been honed over years and you can rely on it to be very challenging, feel rewarding when completed, and impart good foundational knowledge relevant to the class.
```

---

## Retrieval Test Results

**Query 1: "What do students say about Mike Scott's exams?"**

- Top chunks: `rmp_mike_scott.txt` chunks 3, 25, 10, 27, 12
- Distance scores: 0.28, 0.31, 0.38, 0.40, 0.41
- Why relevant: All chunks come from Mike Scott's RMP page and contain direct student opinions about exam difficulty, the 90% grade weight, and past exam preparation strategies.

**Query 2: "Should I take Chatterjee or Joshi for CS429?"**

- Top chunks: `rmp_prashant_joshi.txt` chunks 3, 29, 30, 11, 21
- Distance scores: 0.44, 0.50, 0.52, 0.53, 0.53
- Why partially relevant: Chunks contain Joshi reviews for CS429 but no Chatterjee review chunks were retrieved, making comparison impossible.

**Query 3: "Is CS439 harder than CS429?"**

- Top chunks: `reddit_comarch_vs_os.txt` chunk 0, `rmp_siddhartha_chatterjee.txt` chunk 0, `rmp_alison_norman.txt` chunk 0
- Distance scores: 0.42, 0.49, 0.49
- Why relevant: The Reddit thread directly compares the two courses; the RMP headers contain difficulty ratings for both (4.3 vs 4.6).

---

## Grounded Generation

**System prompt grounding instruction:**

> "You are a helpful assistant that answers questions about UT Austin CS professors and courses. Use ONLY the information in the context provided below to answer. Do not use outside knowledge. If the answer cannot be found in the context, say: 'I don't have enough information in my documents to answer that.' Always cite which source documents you used in your answer."

**How source attribution is surfaced in the response:** Extracted programmatically from `retrieve()` results before the LLM is called. The deduplicated list of source filenames is returned in the `"sources"` key of the response dict alongside `"answer"`. The model is never asked to report its own sources.

---

## Example Responses

**Response 1**

- **Q:** "What do students say about Mike Scott's exams in CS314?"
- **A:** "According to the source documents (rmp_mike_scott.txt), students say that Mike Scott's exams are fairly difficult and make up 90% of the grade. They mention he provides abundant past tests to help prep. Students advise to GRIND past exams to succeed."
- **Sources:** rmp_mike_scott.txt

**Response 2**

- **Q:** "Is CS439 harder than CS429?"
- **A:** "According to the provided context, yes, CS439 is considered harder than CS429. Source [1] (reddit_comarch_vs_os.txt) states it's harder than comp arch, mostly due to projects. The difficulty rating for CS429 is 4.3/5 while CS439 is 4.6/5."
- **Sources:** reddit_comarch_vs_os.txt, rmp_siddhartha_chatterjee.txt, rmp_alison_norman.txt

**Out-of-scope response**

- **Q:** "What is the best pizza place near UT Austin?"
- **A:** "I don't have enough information in my documents to answer that. The provided source documents do not mention pizza places near UT Austin."
- **Sources:** reddit_comarch_vs_os.txt, reddit_ut_cs_junior_rant.txt, rmp_alison_norman.txt, rmp_mike_scott.txt

---

## Query Interface

- **Interface:** Gradio web UI (`app.py`) at http://localhost:7860
- **Input:** Textbox labeled "Your question"
- **Output:** "Answer" textbox (8 lines) and "Retrieved from" textbox (4 lines)
- Both the **Ask** button and pressing **Enter** submit the query.

**Sample interaction**

```
User input:     "What do students say about Mike Scott's exams?"
Answer:         "According to the source documents (rmp_mike_scott.txt), students
                say that Mike Scott's exams are fairly difficult and make up 90%
                of the grade..."
Retrieved from: rmp_mike_scott.txt
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Mike Scott's exams in CS314? | Exams ~90% of grade, very difficult, grind past exams | Correctly identified 90% weight, past exams, difficulty | Relevant | Accurate |
| 2 | Should I take Chatterjee or Joshi for CS429? | Both teach same curriculum; Joshi rated higher for passion; both have brutal exams | Refused — said it lacked information to compare professors | Partially relevant | Inaccurate |
| 3 | What is Norman's grading system like in CS439? | Floor-based column system, confusing, hard to know grade all semester | Described it as confusing and demotivating but missed floor-based details | Relevant | Partially accurate |
| 4 | Is CS439 harder than CS429? | Yes, primarily due to projects (20–30 hrs/week vs 10–15) | Correctly concluded CS439 harder, cited difficulty ratings and Reddit thread | Relevant | Accurate |
| 5 | What are the most important things to do to pass CS314? | Attend lectures, do assignments, grind past exams | Correctly identified past exams, office hours, data structures knowledge | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "Should I take Chatterjee or Joshi for CS429?"

**What the system returned:** Refused with "I don't have enough information in my documents to answer that."

**Root cause (tied to a specific pipeline stage):** At the retrieval stage, the query semantically matched `rmp_prashant_joshi.txt` chunks more strongly than `rmp_siddhartha_chatterjee.txt` chunks. This likely occurred because the Joshi file contains the phrase "watching Chatterjee's videos are a good way to do well in class," which caused Joshi chunks to rank highly for Chatterjee-related queries. All 5 retrieved chunks came from the Joshi file, leaving the model with no Chatterjee review context. With no basis for comparison, the model correctly refused rather than hallucinating.

**What you would change to fix it:** Increase top-k to 10 to surface chunks from more files, or implement metadata filtering to guarantee at least one chunk per professor when a comparison query names two professors explicitly.

---

## Spec Reflection

**One way the spec helped you during implementation:** Writing planning.md before any code forced me to decide on chunk size (400 characters) and justify it before seeing the data. This meant I had a principled reason for my chunking decision rather than guessing, and it gave Claude Code a clear spec to implement from — the generated ingest.py matched the spec exactly on first try.

**One way your implementation diverged from the spec, and why:** The spec assumed the system prompt could use a strict refusal instruction with the word "exactly." In practice, that exact wording caused llama-3.3-70b-versatile to refuse every query, including well-supported ones. I had to soften the refusal clause after debugging, which was not anticipated in the spec.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* My chunking strategy and pipeline diagram from planning.md.
- *What it produced:* ingest.py with `load_documents()`, `clean_text()`, and `chunk_text()` functions using 400-char chunks with 50-char overlap.
- *What I changed or overrode:* Nothing in the core logic. I verified by inspecting 5 sample chunks and confirmed they were readable and correctly attributed. Noted that chunks can span adjacent reviews, which was anticipated challenge #1 in planning.md.

**Instance 2**

- *What I gave the AI:* My retrieval approach from planning.md, the output format from ingest.py, and the pipeline diagram.
- *What it produced:* embed.py with ChromaDB storage using cosine distance (`hnsw:space: cosine`) instead of the default L2 distance.
- *What I changed or overrode:* Kept the cosine distance change because it is the correct metric for MiniLM embeddings and makes the distance scores meaningful for the <0.5 threshold in my evaluation plan. This was an improvement over what my spec described.

**Instance 3**

- *What I gave the AI:* Grounding requirement, source attribution requirement, and the Gradio skeleton from the project instructions.
- *What it produced:* generate.py with a strict system prompt using the word "exactly" in the refusal instruction, which caused the model to refuse all queries.
- *What I changed or overrode:* Directed Claude Code to replace the system prompt with a softer version that kept grounding enforcement but removed the exact-match refusal clause. This was a significant override that required understanding why the model was misbehaving.
```
