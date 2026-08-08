"""
Core generation logic for Concept Kaleidoscope.
Validated in Phase 0 — this is just the reusable, importable version.
"""

import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are an assistant that transforms abstract concepts into four parallel
learning representations for a student. Given a concept, generate ONE JSON
object with exactly these fields:

{
  "diagram_reasoning": "<one sentence: what is this concept's underlying structure - is it a repeating process, a ranked/nested structure, two or more things being weighed against each other, a sequence of events over time, or a one-directional chain of cause and effect?>",
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

How to choose the diagram type - check these in order and use the FIRST one that fits,
not the first one that's easy:
- "cycle": the concept repeats or returns to its starting point (e.g. seasons, cell division, water cycle)
- "timeline": the concept is fundamentally about WHEN things happened relative to each other
- "comparison": the concept centers on two or more things being weighed, contrasted, or in tension
  (e.g. supply vs demand, action vs reaction, two competing forces or ideas)
- "hierarchy": the concept has nested categories, rankings, or one thing made of sub-parts
  (e.g. multiple causes feeding into one outcome, a taxonomy, an org structure)
- "flow": ONLY use this if the concept is a straightforward one-directional chain with no
  meaningful repetition, ranking, or comparison - this should be your last resort, not your default.

Do not default to "flow" out of convenience. If a concept could arguably be "comparison" or
"hierarchy" instead of "flow", choose the more specific one.

Rules:
- The Mermaid syntax must be valid and renderable.
- Output ONLY the JSON object. No preamble, no markdown fences, no commentary."""


def strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def generate_representations(concept: str) -> dict:
    """
    Calls Gemini with the validated prompt and returns a parsed dict with:
    diagram_reasoning, diagram (type, mermaid), story, activity, script.

    Raises ValueError if the API response isn't valid JSON.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set. Check your .env file.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=f"Concept: {concept}",
        config={
            "system_instruction": SYSTEM_PROMPT,
            "response_mime_type": "application/json",
        },
    )

    cleaned = strip_json_fences(response.text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}\nRaw output: {response.text}")