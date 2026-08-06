"""
Phase 0 validation script for Concept Kaleidoscope.

Hits Gemini with the batched structured-output prompt across a set of
stress-test concepts, and prints the raw + parsed JSON so you can eyeball
whether the diagram type selection, story quality, activity quality, and
script quality actually hold up.

Setup:
    pip install google-genai --break-system-packages
    export GEMINI_API_KEY="your-key-here"

Run:
    python test_prompt.py
"""

import os
import json
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv()  # reads GEMINI_API_KEY from a .env file in this directory

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are an assistant that transforms abstract concepts into four parallel
learning representations for a student. Given a concept, generate ONE JSON
object with exactly these fields:

{
  "diagram": {
    "type": "cycle | hierarchy | comparison | timeline | flow",
    "mermaid": "<valid Mermaid.js syntax for this diagram type>"
  },
  "story": "<a short metaphor or narrative, 3-5 sentences, that maps the
            concept onto something concrete and familiar (e.g. everyday
            objects, animals, sports, cooking)>",
  "activity": "<a hands-on mini-activity the student can do right now with
                common household objects or just their body/environment,
                2-4 steps, that physically demonstrates the concept>",
  "script": "<a plain-language explanation written to be read aloud, as if
              explaining to a curious 12-year-old, 4-6 sentences, no jargon>"
}

Rules:
- Pick the SINGLE diagram type that best fits this concept's structure.
  Do not force a type that doesn't fit - if genuinely nothing fits well,
  use "flow".
- The Mermaid syntax must be valid and renderable.
- Output ONLY the JSON object. No preamble, no markdown fences, no commentary."""

TEST_CONCEPTS = [
    "Photosynthesis",
    "Supply and demand",
    "The causes of the French Revolution",
    "Justice",
    "Mitosis",
    "Newton's third law of motion",
]


def strip_json_fences(text: str) -> str:
    """Some models wrap JSON in ```json fences despite instructions. Strip them."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # drop opening fence
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]  # drop closing fence
        text = "\n".join(lines)
    return text.strip()


def call_gemini(client: genai.Client, concept: str) -> dict:
    response = client.models.generate_content(
        model=MODEL,
        contents=f"Concept: {concept}",
        config={
            "system_instruction": SYSTEM_PROMPT,
            "response_mime_type": "application/json",
        },
    )
    raw_text = response.text
    cleaned = strip_json_fences(raw_text)
    return raw_text, cleaned


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set the GEMINI_API_KEY environment variable first.")
        print('  export GEMINI_API_KEY="your-key-here"')
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    results = []
    diagram_types_seen = []

    for concept in TEST_CONCEPTS:
        print(f"\n{'=' * 70}")
        print(f"CONCEPT: {concept}")
        print("=" * 70)

        try:
            raw_text, cleaned = call_gemini(client, concept)
        except Exception as e:
            print(f"  API CALL FAILED: {e}")
            results.append({"concept": concept, "error": str(e)})
            continue

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"  JSON PARSE FAILED: {e}")
            print(f"  RAW OUTPUT:\n{raw_text}")
            results.append({"concept": concept, "error": "parse_failed", "raw": raw_text})
            continue

        diagram_type = parsed.get("diagram", {}).get("type", "MISSING")
        diagram_types_seen.append(diagram_type)

        print(f"  Diagram type : {diagram_type}")
        print(f"  Mermaid      : {parsed.get('diagram', {}).get('mermaid', 'MISSING')[:100]}...")
        print(f"  Story        : {parsed.get('story', 'MISSING')[:150]}...")
        print(f"  Activity     : {parsed.get('activity', 'MISSING')[:150]}...")
        print(f"  Script       : {parsed.get('script', 'MISSING')[:150]}...")

        results.append({"concept": concept, "parsed": parsed})

    # Summary — this is the part that tells you if the architecture holds up
    print(f"\n\n{'#' * 70}")
    print("SUMMARY")
    print("#" * 70)
    print(f"Concepts tested: {len(TEST_CONCEPTS)}")
    print(f"Successful parses: {sum(1 for r in results if 'parsed' in r)}")
    print(f"Diagram types chosen: {diagram_types_seen}")
    if len(set(diagram_types_seen)) == 1 and len(diagram_types_seen) > 1:
        print("  ⚠️  WARNING: same diagram type every time — model may not be discriminating.")

    # Save full results for closer inspection
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nFull results saved to test_results.json")
    print("Next: paste a few of the Mermaid snippets into https://mermaid.live to check they render.")


if __name__ == "__main__":
    main()