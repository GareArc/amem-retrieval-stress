#!/usr/bin/env python3
"""
Automatically generate metadata (keywords, context, tags) for all test fixtures.

This script analyzes memory content and generates:
- keywords: Important terms extracted from content
- context: One-sentence description of what the memory is about
- tags: Domain/category labels for classification
"""

import re
import sys
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from eval.fixtures import TIER_1, TIER_2, TIER_3, NOISE_MEMORIES


# Domain keywords for tag assignment
DOMAIN_KEYWORDS = {
    "business": [
        "revenue",
        "profit",
        "company",
        "quarterly",
        "sales",
        "earnings",
        "market",
        "stock",
        "financial",
        "economic",
    ],
    "technology": [
        "software",
        "algorithm",
        "ai",
        "machine learning",
        "backend",
        "server",
        "code",
        "programming",
        "data",
        "computing",
        "digital",
    ],
    "finance": [
        "investment",
        "portfolio",
        "trading",
        "stocks",
        "bonds",
        "capital",
        "funding",
        "valuation",
    ],
    "science": [
        "research",
        "study",
        "experiment",
        "analysis",
        "discovery",
        "scientific",
        "laboratory",
        "hypothesis",
    ],
    "health": [
        "medical",
        "health",
        "disease",
        "treatment",
        "patient",
        "hospital",
        "doctor",
        "medicine",
        "clinical",
    ],
    "sports": [
        "team",
        "game",
        "player",
        "championship",
        "season",
        "tournament",
        "athletic",
        "scored",
        "victory",
    ],
    "entertainment": [
        "movie",
        "film",
        "actor",
        "music",
        "concert",
        "performance",
        "show",
        "album",
        "artist",
    ],
    "politics": [
        "government",
        "president",
        "policy",
        "legislation",
        "congress",
        "senator",
        "election",
        "political",
    ],
    "education": [
        "university",
        "student",
        "professor",
        "degree",
        "academic",
        "research",
        "curriculum",
        "college",
    ],
    "agriculture": [
        "farm",
        "crop",
        "harvest",
        "orchard",
        "agriculture",
        "growing",
        "field",
        "produce",
    ],
    "nature": [
        "animal",
        "wildlife",
        "forest",
        "ocean",
        "species",
        "habitat",
        "ecosystem",
        "environment",
    ],
    "travel": [
        "destination",
        "tourist",
        "vacation",
        "hotel",
        "flight",
        "trip",
        "travel",
        "visiting",
    ],
    "food": [
        "restaurant",
        "recipe",
        "cooking",
        "chef",
        "menu",
        "dish",
        "ingredient",
        "cuisine",
    ],
}


def extract_keywords(content: str, max_keywords: int = 5) -> list[str]:
    """Extract important keywords from content."""
    # Find capitalized words (likely proper nouns or important terms)
    cap_words = re.findall(r"\b[A-Z][a-z]{2,}|\b[A-Z]{2,}\b", content)

    # Find important lowercase keywords
    important_words = set()
    content_lower = content.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in content_lower:
                important_words.add(kw)

    # Combine and deduplicate
    all_keywords = []
    seen = set()

    # Prioritize capitalized words
    for word in cap_words:
        if word.lower() not in seen and word not in [
            "The",
            "A",
            "An",
            "In",
            "On",
            "At",
        ]:
            all_keywords.append(word)
            seen.add(word.lower())

    # Add domain keywords
    for word in important_words:
        if word not in seen:
            all_keywords.append(word)
            seen.add(word)

    return all_keywords[:max_keywords] if all_keywords else ["information"]


def assign_tags(content: str, role: str = "unknown") -> list[str]:
    """Assign domain tags based on content analysis."""
    tags = []
    content_lower = content.lower()

    # Check each domain
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in content_lower for kw in keywords):
            tags.append(domain)

    # Default tag
    if not tags:
        tags.append("general")

    # Limit to top 3 most relevant
    return tags[:3]


def generate_context(content: str, role: str, tier: int, category: str = "") -> str:
    """Generate a one-sentence context description."""
    content_lower = content.lower()

    # Determine primary domain
    primary_domain = None
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in content_lower for kw in keywords):
            primary_domain = domain
            break

    # Build context based on role and content
    if role == "target":
        if tier == 1:  # Ambiguity
            return f"Primary information about {primary_domain or 'the topic'} relevant to disambiguation"
        elif tier == 2:  # Temporal
            return f"Current or recent {primary_domain or 'information'} with temporal context"
        elif tier == 3:  # Multi-hop
            return f"Key information requiring inferential reasoning about {primary_domain or 'the topic'}"
        else:
            return f"Primary information about {primary_domain or 'the topic'}"

    elif role == "distractor":
        if tier == 1:
            return f"Alternative meaning or sense in {primary_domain or 'different context'}"
        elif tier == 2:
            return f"Outdated or temporally incorrect {primary_domain or 'information'}"
        else:
            return (
                f"Related but not directly relevant {primary_domain or 'information'}"
            )

    elif role == "noise":
        return f"Background information about {primary_domain or 'various topics'}"

    else:
        return f"General information about {primary_domain or 'the topic'}"


def add_metadata_to_memory(
    memory: dict[str, Any], tier: int, category: str = ""
) -> dict[str, Any]:
    """Add metadata fields to a single memory dict."""
    # Skip if metadata already exists
    if "keywords" in memory and "context" in memory and "tags" in memory:
        return memory

    content = memory.get("content", "")
    role = memory.get("role", "unknown")

    # Generate metadata
    if "keywords" not in memory:
        memory["keywords"] = extract_keywords(content)

    if "context" not in memory:
        memory["context"] = generate_context(content, role, tier, category)

    if "tags" not in memory:
        memory["tags"] = assign_tags(content, role)

    return memory


def process_all_fixtures():
    """Add metadata to all fixtures."""
    print("Generating metadata for all test fixtures...")
    print("=" * 70)

    total_memories = 0

    # Process Tier 1
    print(f"\nTier 1: Ambiguity ({len(TIER_1)} cases)")
    for case in TIER_1:
        tier = case["tier"]
        category = case.get("category", "")
        for memory in case["memories"]:
            add_metadata_to_memory(memory, tier, category)
            total_memories += 1

    # Process Tier 2
    print(f"Tier 2: Temporal ({len(TIER_2)} cases)")
    for case in TIER_2:
        tier = case["tier"]
        category = case.get("category", "")
        for memory in case["memories"]:
            add_metadata_to_memory(memory, tier, category)
            total_memories += 1

    # Process Tier 3
    print(f"Tier 3: Multi-hop ({len(TIER_3)} cases)")
    for case in TIER_3:
        tier = case["tier"]
        category = case.get("category", "")
        for memory in case["memories"]:
            add_metadata_to_memory(memory, tier, category)
            total_memories += 1

    # Process noise memories
    print(f"Noise memories ({len(NOISE_MEMORIES)} memories)")
    for memory in NOISE_MEMORIES:
        add_metadata_to_memory(memory, tier=0, category="noise")
        total_memories += 1

    print(f"\nTotal memories processed: {total_memories}")
    print("=" * 70)

    return TIER_1, TIER_2, TIER_3, NOISE_MEMORIES


def write_fixtures(tier_1, tier_2, tier_3, noise):
    """Write updated fixtures back to file."""
    fixtures_path = PROJECT_ROOT / "eval" / "fixtures.py"

    print(f"\nWriting updated fixtures to {fixtures_path}...")

    # Read original file to preserve header and structure
    with open(fixtures_path, "r") as f:
        original = f.read()

    # Extract header (everything before TIER_1 definition)
    header_end = original.find("TIER_1: list[dict[str, Any]] = [")
    if header_end == -1:
        print("Error: Could not find TIER_1 definition in fixtures.py")
        return False

    header = original[:header_end]

    # Build new content
    import pprint

    content = header
    content += "TIER_1: list[dict[str, Any]] = "
    content += pprint.pformat(tier_1, width=120, sort_dicts=False)
    content += "\n\n"

    content += "TIER_2: list[dict[str, Any]] = "
    content += pprint.pformat(tier_2, width=120, sort_dicts=False)
    content += "\n\n"

    content += "TIER_3: list[dict[str, Any]] = "
    content += pprint.pformat(tier_3, width=120, sort_dicts=False)
    content += "\n\n"

    content += "NOISE_MEMORIES: list[dict[str, Any]] = "
    content += pprint.pformat(noise, width=120, sort_dicts=False)
    content += "\n\n"

    # Add footer
    content += """
# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def get_fixtures(tiers: list[int] | None = None) -> list[dict[str, Any]]:
    \"\"\"Get test fixtures, optionally filtered by tier.\"\"\"
    all_fixtures = TIER_1 + TIER_2 + TIER_3
    if tiers is None:
        return all_fixtures
    return [f for f in all_fixtures if f["tier"] in tiers]


def get_fixture_by_id(case_id: str) -> dict[str, Any] | None:
    \"\"\"Get a single fixture by its ID.\"\"\"
    for fixture in TIER_1 + TIER_2 + TIER_3:
        if fixture["id"] == case_id:
            return fixture
    return None


ALL_FIXTURES = TIER_1 + TIER_2 + TIER_3
"""

    # Write to file
    with open(fixtures_path, "w") as f:
        f.write(content)

    print(f"✅ Successfully wrote {len(tier_1) + len(tier_2) + len(tier_3)} test cases")
    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate metadata for test fixtures")
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )
    args = parser.parse_args()

    tier_1, tier_2, tier_3, noise = process_all_fixtures()

    # Preview some examples
    print("\n" + "=" * 70)
    print("PREVIEW: First memory from T1-01")
    print("=" * 70)
    example = tier_1[0]["memories"][0]
    print(f"Content: {example['content'][:60]}...")
    print(f"Keywords: {example['keywords']}")
    print(f"Context: {example['context']}")
    print(f"Tags: {example['tags']}")
    print("=" * 70)

    # Ask for confirmation
    if args.yes:
        confirmed = True
    else:
        try:
            response = input("\nWrite changes to fixtures.py? [y/N]: ")
            confirmed = response.lower() == "y"
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            confirmed = False

    if confirmed:
        if write_fixtures(tier_1, tier_2, tier_3, noise):
            print("\n✅ Metadata generation complete!")
        else:
            print("\n❌ Failed to write fixtures")
            sys.exit(1)
    else:
        print("\nAborted. No changes made.")


if __name__ == "__main__":
    main()
