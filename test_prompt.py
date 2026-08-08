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

from generator import generate_representations

OUTPUT_DIR = "output"

TEST_CONCEPTS = [
    "Photosynthesis",
    "Supply and demand",
    "The causes of the French Revolution",
    "Justice",
    "Mitosis",
    "Newton's third law of motion",
    "The timeline of World War 2",
    "The stages of the water cycle",
    "The evolution of the cell phone from 1980 to today",
]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = []
    diagram_types_seen = []

    for concept in TEST_CONCEPTS:
        print(f"\n{'=' * 70}")
        print(f"CONCEPT: {concept}")
        print("=" * 70)

        try:
            parsed = generate_representations(concept)
        except Exception as e:
            print(f"  GENERATION FAILED: {e}")
            results.append({"concept": concept, "error": str(e)})
            continue

        diagram_type = parsed.get("diagram", {}).get("type", "MISSING")
        diagram_types_seen.append(diagram_type)

        print(f"  Reasoning    : {parsed.get('diagram_reasoning', 'MISSING')}")
        print(f"  Diagram type : {diagram_type}")
        print(f"  Mermaid      : {parsed.get('diagram', {}).get('mermaid', 'MISSING')[:100]}...")
        print(f"  Story        : {parsed.get('story', 'MISSING')[:150]}...")
        print(f"  Activity     : {parsed.get('activity', 'MISSING')[:150]}...")
        print(f"  Script       : {parsed.get('script', 'MISSING')[:150]}...")

        results.append({"concept": concept, "parsed": parsed})

        # Write out a clean, ready-to-paste .mmd file per concept
        safe_name = concept.lower().replace(" ", "_").replace("'", "")
        mermaid_code = parsed.get("diagram", {}).get("mermaid", "")
        if mermaid_code:
            with open(os.path.join(OUTPUT_DIR, f"diagram_{safe_name}.mmd"), "w") as f:
                f.write(mermaid_code)

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
    results_path = os.path.join(OUTPUT_DIR, "test_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull results saved to {results_path}")
    print("Individual .mmd files saved per concept — open one, copy its contents,")
    print("and paste directly into https://mermaid.live to see the rendered diagram.")


if __name__ == "__main__":
    main()