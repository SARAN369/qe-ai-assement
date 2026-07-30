# AI Testing Assistant (Phase 7)

A Python CLI chatbot that reads this repo's requirement document
(`docs/AI Usecase.docx`) and Gherkin feature file
(`features/multiCityFlightBooking.feature`), then answers questions about
test cases/requirements or generates Selenium automation code — grounded in
what's actually in those files, via a **local** LLM through
[Ollama](https://ollama.com) (no API key, no cloud calls).

## How it works

```
docx / .feature files
        │
        ▼
doc_loader.py    → splits into chunks (one per docx section, one per Gherkin scenario)
        │
        ▼
retriever.py     → dependency-free keyword-overlap scoring, top-k chunks above a
        │           relevance threshold (score >= 4 — see note below)
        ▼
prompts.py + llm_client.py → sends CONTEXT + QUESTION to a local Ollama model
        │
        ▼
   answer, grounded in the retrieved chunks
```

The "does this even relate to the question" decision is made in
**`retriever.py` by a score threshold, not by the LLM**. Small local models
(this was built and tested against `llama3.2:3b`) are not reliable judges
of their own retrieval relevance — during development, asking the model to
recognize "the CONTEXT doesn't actually cover this" and reply accordingly
produced two failure modes depending on prompt wording: either confidently
hallucinating a plausible-sounding scenario that doesn't exist in the
project (e.g. inventing Gherkin steps for a login flow this project has
none of), or the opposite — refusing genuinely relevant questions it should
have answered. Filtering by retrieval score before the model ever sees the
question sidesteps both: the model only ever gets called with context that's
already been confirmed on-topic in code.

## Setup

1. Install [Ollama](https://ollama.com) and start it (installing it starts
   the background service; on Windows it also runs after install).
2. Pull a model: `ollama pull llama3.2:3b` (~2GB).
3. `pip install -r requirements.txt`

## Usage

```bash
python main.py                                          # interactive REPL
python main.py --query "What are the test cases for the search flow?"
python main.py --query "Generate Selenium code for search functionality."
```

REPL commands: `:sources` (show which chunks the last answer used),
`:reload` (re-read the source documents), `:exit`.

Point it at different documents with `--docs path1 path2 ...` (accepts
`.docx` and `.feature` files), or a different local model with `--model`.

## Example

```
$ python main.py --query "What are the test cases for the search flow?"
The test cases for the search flow, as described in the provided Gherkin feature file, are:

1. Search for multi-city flights with valid traveller count and cabin class
2. Attempt search with an incomplete itinerary
...

$ python main.py --query "What are the test cases for login?"
No matching test cases/requirements found in the current requirement document
or feature file for: "What are the test cases for login?".
```

The second example is intentional: this project has no login flow (the
MakeMyTrip use case starts directly at multi-city search), so the assistant
says so instead of fabricating one — that grounding behavior is the point
of this component per the Phase 7 brief.

## Known limitations

- Retrieval is keyword-overlap, not semantic/embedding-based — a query
  using entirely different vocabulary from the source docs (e.g. a synonym
  the docs never use) may under-match. Good enough for a project this size
  (~80 chunks); swap in an embedding-based retriever if the corpus grows.
- Code generation quality depends on the local model. `llama3.2:3b` is
  small and fast but will sometimes fill gaps with clearly-labeled
  placeholders rather than fully-grounded specifics — by design, per the
  grounding rule above, it should label those as placeholders rather than
  presenting them as drawn from the requirement doc.
