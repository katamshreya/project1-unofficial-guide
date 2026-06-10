# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
This project covers student-generated knowledge about Computer Science professors and courses at the University of Texas at Austin. This knowledge is valuable because it contains honest, experience-based insights about teaching styles, exam formats, grading policies, and course difficulty that official university sources never provide. A student trying to decide between professors for CS439 or understand what actually determines their grade in CS314 cannot find that information in any course catalog or department website — it lives entirely in Rate My Professors reviews and Reddit threads.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Student reviews of Mike Scott (CS314) | documents/rmp_mike_scott.txt |
| 2 | Rate My Professors | Student reviews of Devangi Parikh (CS311) | documents/rmp_devangi_parikh.txt |
| 3 | Rate My Professors | Student reviews of Siddhartha Chatterjee (CS429) | documents/rmp_siddhartha_chatterjee.txt |
| 4 | Rate My Professors | Student reviews of Prashant Joshi (CS429/CS327E) | documents/rmp_prashant_joshi.txt |
| 5 | Rate My Professors | Student reviews of Alison Norman (CS439) | documents/rmp_alison_norman.txt |
| 6 | r/UTAustin | Thread comparing Mootaz vs Norman for CS439 | documents/reddit_cs439_mootaz_vs_norman.txt |
| 7 | r/UTAustin | Thread comparing CS429 vs CS439 difficulty | documents/reddit_comarch_vs_os.txt |
| 8 | r/UTAustin | Thread about best professor for CS312 | documents/reddit_cs312_professor.txt |
| 9 | r/UTAustin | Thread with professor recommendations for incoming CS freshmen | documents/reddit_incoming_cs_recommendations.txt |
| 10 | r/UTAustin | Thread from UT CS junior about burnout, internships, and CS experience | documents/reddit_ut_cs_junior_rant.txt |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 400 characters

**Overlap:** 50 characters

**Reasoning:** The documents are almost entirely short, opinion-based reviews and Reddit comments. Most individual reviews are 2-5 sentences and express one or two distinct opinions (e.g. "exams are brutal" and "he's a great lecturer"). A 400-character chunk is large enough to capture a complete thought from a single review without merging unrelated reviews together. A larger chunk (e.g. 800+ characters) would blend multiple reviewers' opinions into one embedding, making it harder to match specific queries like "what do students say about Norman's grading?" Overlap of 50 characters is small because the documents don't contain multi-sentence arguments that span natural boundaries -- each review stands alone. The overlap mainly protects against splitting a single sentence across two chunks.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers 

**Top-k:** 5

**Production tradeoff reflection:** For a production deployment I would consider text-embedding-3-small from OpenAI or a larger sentence-transformers model like all-mpnet-base-v2. The tradeoffs I would weigh are: (1) accuracy on short, informal text -- all-MiniLM-L6-v2 was trained on general text and may not handle slang like "goated" or "cooked" as well as a model fine-tuned on social/review text; (2) context length -- at 256 tokens, all-MiniLM-L6-v2 fits our 400-character chunks comfortably, but a longer-context model would be needed if chunk sizes grew; (3) latency -- local models avoid API round-trips but are slower on CPU than API-based embeddings on optimized infrastructure; (4) cost -- local models are free at any scale, while API-based models cost per token and would add up across thousands of queries.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Mike Scott's exams in CS314? | Exams are worth ~90% of the grade, are very difficult, and students strongly recommend grinding past exams for 2+ weeks before each one |
| 2 | Should I take Chatterjee or Joshi for CS429? | Both teach the same curriculum; Joshi is rated more highly for passion and approachability, Chatterjee is more polarizing; both have brutal exams and time-consuming labs |
| 3 | What is Norman's grading system like in CS439? | It is a floor-based, column system that is confusing and makes it hard to know your grade during the semester; getting a B is relatively achievable but getting an A requires significant effort |
| 4 | Is CS439 harder than CS429? | Yes, primarily due to projects (20-30 hrs/week vs 10-15 for CS429); exam difficulty is comparable or slightly lower, but the workload and stress are significantly higher |
| 5 | What are the most important things to do to pass CS314 with Mike Scott? | Attend lectures, complete programming assignments, and most importantly grind past exams extensively -- exams are nearly 90% of the grade |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Review sentiment split across chunk boundaries:** Many reviews contain both positive and negative opinions about the same professor (e.g. "great lecturer but terrible grading system"). If a 400-character chunk cuts between the positive and negative halves, a query about grading might retrieve the positive half and vice versa, producing misleading context for the LLM.

2. **Short or thin Reddit threads producing low-signal chunks:** Several Reddit threads (especially reddit_cs312_professor.txt and reddit_comarch_vs_os.txt) have very few comments. Chunks from these files will be short and may not carry enough semantic content to match queries reliably, resulting in high distance scores and poor retrieval for questions about those topics.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

     ```mermaid
     graph LR
     A[Document Ingestion\npdfplumber / plain text loader] --> B[Chunking\nCustom chunk_text\n400 chars / 50 overlap]
     B --> C[Embedding\nsentence-transformers\nall-MiniLM-L6-v2]
     C --> D[Vector Store\nChromaDB\nlocal]
     D --> E[Retrieval\nSemantic search\ntop-k=5]
     E --> F[Generation\nGroq API\nllama-3.3-70b-versatile]
     F --> G[Query Interface\nGradio web UI]
     ```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I will use Claude. I will provide the Documents section (file names, types, and locations), the Chunking Strategy section (400 characters, 50 overlap), and the Architecture diagram. I will ask Claude to implement a script called ingest.py that loads all .txt files from the documents/ folder, cleans them by removing any leftover formatting artifacts, splits them into chunks using the specified size and overlap, and outputs a list of dicts with keys: text, source, and chunk_index. I will verify the output by printing 5 random chunks and confirming they are readable, complete thoughts with no HTML artifacts and correct source labels.

**Milestone 4 — Embedding and retrieval:**
I will use Claude. I will provide the Retrieval Approach section (all-MiniLM-L6-v2, top-k=5), the Architecture diagram, and the output format from ingest.py. I will ask Claude to implement embed.py that loads chunks from ingest.py, embeds them with SentenceTransformer("all-MiniLM-L6-v2"), stores them in a local ChromaDB collection with source metadata, and implements a retrieve(query, k=5) function that returns the top-k chunks and their source filenames. I will verify by running retrieve() on 3 of my evaluation questions and checking that returned chunks are visibly relevant and distance scores are below 0.5.

**Milestone 5 — Generation and interface:**
I will use Claude. I will provide the grounding requirement (answers must come only from retrieved context, not general knowledge), the source attribution requirement, the output format (answer + source list), and the Gradio skeleton from the project instructions. I will ask Claude to implement generate.py that takes a query and retrieved chunks, formats a prompt that instructs llama-3.3-70b-versatile to answer only from the provided context or say it doesn't have enough information, and returns a response with cited sources. I will also ask it to wire this into a Gradio app.py. I will verify grounding by asking a question my documents don't cover and confirming the system declines rather than hallucinating.
