# Concept Kaleidoscope — Phase 0

Validates the core prompt before any app code gets built.

## Setup

1. Get a free Gemini API key: https://aistudio.google.com/apikey
2. Install deps:
   ```
   pip install -r requirements.txt --break-system-packages
   ```
3. Set your key:
   ```
   export GEMINI_API_KEY="your-key-here"
   ```

## Run

```
python test_prompt.py
```

This calls Gemini once per test concept (6 calls total) using the batched
JSON-output prompt, prints a preview of each field, and flags if diagram
type selection looks like it's not discriminating (same type every time).

Full raw output gets saved to `test_results.json` for closer inspection.

## What to look for

- **Diagram type variety** — should differ across concepts (cycle vs.
  timeline vs. comparison), not default to the same thing every time.
- **Mermaid validity** — copy a few snippets into https://mermaid.live
  and confirm they render without syntax errors.
- **Story quality** — should be an actual metaphor, not just a restatement
  with "imagine if..." tacked on.
- **Activity quality** — should be physically doable, not secretly just
  "write down..." or "think about...".
- **The "Justice" case** — this is the stress test for concepts with no
  obvious spatial structure. See what it defaults to and whether it's
  still useful.

## Next step

Once outputs look solid across the 6 concepts, move to Phase 1: wrap this
into a clean reusable function and build the minimal UI around it.