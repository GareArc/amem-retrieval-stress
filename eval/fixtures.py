"""
Test fixtures for A-mem memory retrieval evaluation.

45 test cases across 3 tiers:
  Tier 1 (15): Lexical/Semantic Ambiguity
  Tier 2 (15): Temporal Reasoning
  Tier 3 (15): Multi-hop / Indirect Connection

Design principles:
  - Query vocabulary MUST NOT trivially overlap with target memory content.
    e.g. if memory says "deadline", query must NOT say "due" (too easy for embeddings).
  - Each case has "target" memories (SHOULD be retrieved) and "distractor" memories
    (should NOT be retrieved or ranked lower).
  - Temporal cases include timestamps and a query_timestamp to anchor "current time".
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Tier 1 — LEXICAL / SEMANTIC AMBIGUITY
#
# Pattern: Two+ memories share an ambiguous term in different senses.
# Query targets ONE sense using vocabulary with zero keyword overlap.
# ---------------------------------------------------------------------------

TIER_1: list[dict[str, Any]] = [
    # ── Polysemy: named entity vs common noun ──────────────────────────
    {
        "id": "T1-01",
        "tier": 1,
        "category": "polysemy_entity",
        "title": "Apple: tech company vs fruit",
        "memories": [
            {
                "id": "target",
                "content": "Apple's quarterly revenue reached $94 billion driven by strong iPhone and services growth",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The farmer's market had the freshest organic apples I've tasted all season",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Apple orchards in Washington State reported record harvest yields this quarter",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Apple pie remains the top-selling dessert at the bakery according to quarterly sales data",
                "role": "distractor",
            },
        ],
        "query": "How did the Cupertino tech giant perform financially last quarter?",
        "notes": "Query uses 'Cupertino tech giant' (no 'Apple'), 'perform financially' (no 'revenue'). Requires Apple = Cupertino tech giant. Multiple fruit-sense distractors including one with 'quarterly' to increase confusion.",
    },
    {
        "id": "T1-02",
        "tier": 1,
        "category": "polysemy_entity",
        "title": "Python: programming language vs snake",
        "memories": [
            {
                "id": "target",
                "content": "We migrated our backend services to Python for better machine learning integration",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The Burmese python at the reptile exhibit measured over fifteen feet in length",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Python populations in the Florida Everglades have grown rapidly in recent years",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The reticulated python is known for its impressive constriction capabilities and hunting efficiency",
                "role": "distractor",
            },
        ],
        "query": "What scripting language was chosen for the server-side rewrite?",
        "notes": "Query says 'scripting language' and 'server-side rewrite' — no 'Python', 'backend', or 'machine learning'. Multiple snake-sense distractors.",
    },
    {
        "id": "T1-03",
        "tier": 1,
        "category": "polysemy_entity",
        "title": "Java: programming language vs Indonesian island",
        "memories": [
            {
                "id": "target",
                "content": "The garbage collection pauses in our Java runtime caused latency spikes across production",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "We visited ancient Buddhist temples on the island of Java during our backpacking trip",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Java coffee production reached record volumes during the latest harvest season",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The population density on Java exceeds 1,100 people per square kilometer making it one of the most crowded regions",
                "role": "distractor",
            },
        ],
        "query": "What caused the application performance degradation in the runtime environment?",
        "notes": "Query avoids 'Java', 'garbage collection', 'latency'. Uses 'application performance degradation' and 'runtime environment'. Multiple island/geography-sense distractors.",
    },
    {
        "id": "T1-04",
        "tier": 1,
        "category": "polysemy_entity",
        "title": "Mercury: planet vs toxic element",
        "memories": [
            {
                "id": "target",
                "content": "Mercury's surface temperature fluctuates between minus 180 and plus 430 degrees Celsius",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "Mercury contamination in the local river exceeded safe drinking water standards by a factor of three",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Mercury levels in the fish population have prompted new health warnings from environmental authorities",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The old mercury thermometer showed extreme temperature variations before it was replaced with digital sensors",
                "role": "distractor",
            },
        ],
        "query": "Which celestial body has the most extreme day-night temperature variation in our solar system?",
        "notes": "Query says 'celestial body' and 'solar system' — no 'Mercury', 'surface', or 'degrees'. Multiple element/substance-sense distractors, with distractor_3 mentioning 'temperature' for extra confusion.",
    },
    {
        "id": "T1-05",
        "tier": 1,
        "category": "polysemy_entity",
        "title": "Mars: planet vs candy corporation",
        "memories": [
            {
                "id": "target",
                "content": "The Perseverance rover collected rock samples in the Jezero Crater on Mars",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "Mars Incorporated announced a global recall of certain Snickers and Milky Way products",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Mars chocolate bars saw record sales during the holiday season exceeding analyst expectations",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The Mars family maintains private ownership of the confectionery company founded in 1911",
                "role": "distractor",
            },
        ],
        "query": "What geological specimens has the robotic explorer gathered from the red planet?",
        "notes": "'Robotic explorer' not 'rover', 'geological specimens' not 'rock samples', 'red planet' not 'Mars'. Multiple candy company-sense distractors.",
    },
    # ── Polysemy: domain-shift (same word, different fields) ──────────
    {
        "id": "T1-06",
        "tier": 1,
        "category": "polysemy_domain",
        "title": "Bank: financial institution vs riverbank",
        "memories": [
            {
                "id": "target",
                "content": "The central bank raised the benchmark interest rate by 50 basis points this quarter",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "Wildflowers grew abundantly along the river bank where we held last summer's picnic",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Erosion along the creek bank has worsened significantly after the recent flooding",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The steep bank of the canal made it difficult to access the water for irrigation",
                "role": "distractor",
            },
            {
                "id": "distractor_4",
                "content": "Bank stabilization projects are scheduled to begin next quarter along the waterfront",
                "role": "distractor",
            },
        ],
        "query": "What monetary policy adjustments were announced by the national financial authority?",
        "notes": "'Financial authority' not 'bank', 'monetary policy adjustments' not 'interest rate'. Multiple riverbank-sense distractors, one with 'quarter' for temporal confusion.",
    },
    {
        "id": "T1-07",
        "tier": 1,
        "category": "polysemy_domain",
        "title": "Crane: construction equipment vs wading bird",
        "memories": [
            {
                "id": "target",
                "content": "The construction crew deployed a 200-ton crane to position the steel framework into place",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "A pair of sandhill cranes built their nest near the wetland preserve this spring",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Whooping crane populations have shown encouraging recovery in protected habitats",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The migratory crane species travels thousands of miles each year seeking suitable breeding grounds",
                "role": "distractor",
            },
        ],
        "query": "What heavy lifting apparatus was used at the building site?",
        "notes": "'Heavy lifting apparatus' not 'crane', 'building site' not 'construction'. Multiple bird-sense distractors.",
    },
    {
        "id": "T1-08",
        "tier": 1,
        "category": "polysemy_domain",
        "title": "Spring: season vs mechanical part",
        "memories": [
            {
                "id": "target",
                "content": "Cherry blossoms reach peak bloom every spring along the Tidal Basin in Washington DC",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The garage door torsion spring snapped and needs immediate professional replacement",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Coil spring suspension systems provide better ride quality compared to leaf springs in modern vehicles",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The mattress lost support after the box spring wore out from years of use",
                "role": "distractor",
            },
        ],
        "query": "When do the ornamental trees put on their annual flowering display in the US capital?",
        "notes": "'Ornamental trees', 'flowering display', 'US capital' — no 'cherry', 'spring', 'bloom', 'Washington'. Multiple mechanical part-sense distractors.",
    },
    {
        "id": "T1-09",
        "tier": 1,
        "category": "polysemy_domain",
        "title": "Pitch: investor presentation vs musical tone",
        "memories": [
            {
                "id": "target",
                "content": "The startup founder delivered a compelling pitch to three venture capital firms last Thursday",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The first violinist struggled to maintain accurate pitch throughout the concerto's second movement",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Perfect pitch ability allows musicians to identify notes without a reference tone",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The choir director adjusted the pitch upward by a half step to suit the sopranos' range",
                "role": "distractor",
            },
        ],
        "query": "How did the entrepreneur's fundraising presentation go with the investment groups?",
        "notes": "'Entrepreneur' not 'founder', 'fundraising presentation' not 'pitch', 'investment groups' not 'venture capital firms'. Multiple musical tone-sense distractors.",
    },
    {
        "id": "T1-10",
        "tier": 1,
        "category": "polysemy_domain",
        "title": "Cell: biology vs prison",
        "memories": [
            {
                "id": "target",
                "content": "The research team identified a novel stem cell variant capable of regenerating damaged nerve tissue",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The inmate was transferred to an isolation cell following the altercation in the exercise yard",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Prison overcrowding resulted in two inmates sharing a single cell designed for one occupant",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The holding cell detention area was renovated to meet modern safety standards",
                "role": "distractor",
            },
        ],
        "query": "What breakthrough was achieved in the laboratory's tissue repair studies?",
        "notes": "'Laboratory' not 'research team', 'tissue repair studies' not 'stem cell' or 'regenerating nerve tissue'. Multiple prison-sense distractors.",
    },
    # ── Metonymy / cultural knowledge ─────────────────────────────────
    {
        "id": "T1-11",
        "tier": 1,
        "category": "metonymy",
        "title": "The White House: administration vs building",
        "memories": [
            {
                "id": "target",
                "content": "The White House announced sweeping new executive orders on climate and emissions policy",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The White House was originally built with Aquia Creek sandstone and first painted white in 1818",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "The White House underwent major renovations during the Truman administration to stabilize its structure",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "White House tours are now available by advance reservation through congressional offices",
                "role": "distractor",
            },
        ],
        "query": "What environmental regulations did the US presidential administration enact?",
        "notes": "'US presidential administration' not 'White House', 'environmental regulations' not 'climate policy' or 'executive orders'. Multiple building-sense distractors, with 'administration' appearing in historical context.",
    },
    {
        "id": "T1-12",
        "tier": 1,
        "category": "metonymy",
        "title": "Hollywood: film industry vs neighborhood",
        "memories": [
            {
                "id": "target",
                "content": "Hollywood studios are investing heavily in generative AI for visual effects pipelines",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "Residential property values in the Hollywood neighborhood climbed 15% year over year",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "The Hollywood Walk of Fame added twelve new stars honoring entertainment industry pioneers",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Traffic congestion in Hollywood reached record levels during the recent film festival",
                "role": "distractor",
            },
        ],
        "query": "How is the American motion picture industry integrating new computational tools into post-production?",
        "notes": "'Motion picture industry' not 'Hollywood', 'computational tools' not 'AI', 'post-production' not 'visual effects'. Distractors mix geographic location with entertainment references (Walk of Fame, festival).",
    },
    {
        "id": "T1-13",
        "tier": 1,
        "category": "metonymy",
        "title": "Wall Street: financial sector vs subway station",
        "memories": [
            {
                "id": "target",
                "content": "Wall Street analysts downgraded the technology sector following disappointing quarterly earnings",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The Wall Street subway station is undergoing extensive renovation for ADA accessibility",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Wall Street's historic cobblestone pavement will be preserved during upcoming infrastructure upgrades",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Tourist foot traffic on Wall Street increased significantly following the opening of new museums",
                "role": "distractor",
            },
        ],
        "query": "What did the equity research community say about the recent performance of tech companies?",
        "notes": "'Equity research community' not 'analysts', 'tech companies' not 'technology sector'. Multiple geographic location distractors.",
    },
    {
        "id": "T1-14",
        "tier": 1,
        "category": "metonymy",
        "title": "Silicon Valley: tech ecosystem vs geographic valley",
        "memories": [
            {
                "id": "target",
                "content": "Silicon Valley startups collectively raised $48 billion in venture funding during Q3",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The Santa Clara Valley was once the largest fruit-producing region on the West Coast",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Valley floor irrigation systems transformed agricultural production in the Santa Clara region",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The valley's temperate climate supported diverse crops before suburban development",
                "role": "distractor",
            },
        ],
        "query": "How much private equity flowed into the Bay Area technology entrepreneurship scene last quarter?",
        "notes": "'Private equity' not 'venture funding', 'Bay Area technology entrepreneurship scene' not 'Silicon Valley startups'. Multiple geographic valley/agriculture-sense distractors.",
    },
    {
        "id": "T1-15",
        "tier": 1,
        "category": "metonymy",
        "title": "Crown: sovereign authority vs jeweled headpiece",
        "memories": [
            {
                "id": "target",
                "content": "The Crown issued a formal pardon for all individuals convicted under the repealed statute",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The jewel-encrusted crown on display at the Tower of London weighs nearly five pounds",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "The coronation crown was specially fitted with velvet lining for the upcoming ceremony",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Replicas of the crown jewels are sold at the museum gift shop for tourists",
                "role": "distractor",
            },
        ],
        "query": "What clemency action did the British sovereign authority grant regarding the outdated law?",
        "notes": "'Sovereign authority' not 'Crown', 'clemency' not 'pardon', 'outdated law' not 'repealed statute'. Multiple jeweled headpiece-sense distractors.",
    },
]


# ---------------------------------------------------------------------------
# Tier 2 — TEMPORAL REASONING
#
# Pattern A (relative_to_absolute): Memory uses relative time ("tomorrow",
#   "next week"). Query uses a DIFFERENT relative reference anchored to a
#   later date that resolves to the same absolute moment.
# Pattern B (state_conflict): Two memories about the same topic at different
#   times. The LATER one supersedes. Query asks for "current" state.
# Pattern C (temporal_arithmetic): Requires date math to connect memory and
#   query (e.g., "in 5 days" vs "tomorrow" from 4 days later).
#
# IMPORTANT: distractor memories share the same TOPIC so embedding similarity
# is high — only temporal reasoning can distinguish target from distractor.
# ---------------------------------------------------------------------------

TIER_2: list[dict[str, Any]] = [
    # ── Relative → Absolute (5 cases) ────────────────────────────────
    {
        "id": "T2-01",
        "tier": 2,
        "category": "relative_to_absolute",
        "title": "Tomorrow morning -> today (next-day query)",
        "memories": [
            {
                "id": "target",
                "content": "Team sync rescheduled to tomorrow morning at nine",
                "role": "target",
                "timestamp": "202603100800",
            },
            {
                "id": "distractor_1",
                "content": "Team sync ran long last week and we skipped the retrospective",
                "role": "distractor",
                "timestamp": "202603100800",
            },
            {
                "id": "distractor_2",
                "content": "Team sync yesterday covered the sprint planning and capacity allocation",
                "role": "distractor",
                "timestamp": "202603100800",
            },
            {
                "id": "distractor_3",
                "content": "Team sync next week will include the new Q2 roadmap review",
                "role": "distractor",
                "timestamp": "202603100800",
            },
            {
                "id": "distractor_4",
                "content": "Team sync was cancelled this morning due to the all-hands meeting conflict",
                "role": "distractor",
                "timestamp": "202603100800",
            },
        ],
        "query": "Is there a team sync happening today?",
        "query_timestamp": "202603110900",
        "notes": "All memories mention 'team sync'. Distinguishing factor is ONLY temporal: 'tomorrow' from Mar 10 = Mar 11 = 'today' from query perspective. Distractors span past (last week, yesterday, this morning) and future (next week).",
    },
    {
        "id": "T2-02",
        "tier": 2,
        "category": "relative_to_absolute",
        "title": "Next Wednesday -> this week (query one week later)",
        "memories": [
            {
                "id": "target",
                "content": "Client walkthrough of the prototype pushed to next Wednesday afternoon",
                "role": "target",
                "timestamp": "202603030900",
            },
            {
                "id": "distractor_1",
                "content": "Client walkthrough in February covered the wireframes and got positive feedback",
                "role": "distractor",
                "timestamp": "202603030900",
            },
            {
                "id": "distractor_2",
                "content": "Client walkthrough last Wednesday went well and they approved moving to the next phase",
                "role": "distractor",
                "timestamp": "202603030900",
            },
            {
                "id": "distractor_3",
                "content": "Client walkthrough scheduled for late March will include the full feature set demonstration",
                "role": "distractor",
                "timestamp": "202603030900",
            },
        ],
        "query": "Are there any client sessions this week?",
        "query_timestamp": "202603100900",
        "notes": "'Next Wednesday' from Mar 3 = Mar 10 = 'this week' from query. All memories mention 'client walkthrough'. Distractors reference different times (February, last Wednesday, late March).",
    },
    {
        "id": "T2-03",
        "tier": 2,
        "category": "relative_to_absolute",
        "title": "Tonight -> last night (next-morning query)",
        "memories": [
            {
                "id": "target",
                "content": "Ops team taking the authentication services offline tonight from eleven to three",
                "role": "target",
                "timestamp": "202603101800",
            },
            {
                "id": "distractor_1",
                "content": "Authentication services had a brief hiccup two weeks ago but self-recovered",
                "role": "distractor",
                "timestamp": "202603101800",
            },
            {
                "id": "distractor_2",
                "content": "Authentication services will undergo scheduled maintenance next weekend for security patches",
                "role": "distractor",
                "timestamp": "202603101800",
            },
            {
                "id": "distractor_3",
                "content": "Authentication services experienced elevated latency three days ago during peak traffic",
                "role": "distractor",
                "timestamp": "202603101800",
            },
        ],
        "query": "Were any of our services intentionally brought down last night?",
        "query_timestamp": "202603110800",
        "notes": "'Tonight' from Mar 10 evening = 'last night' from Mar 11 morning. All mention 'authentication services'. Distractors span past incidents (two weeks ago, three days ago) and future maintenance (next weekend).",
    },
    {
        "id": "T2-04",
        "tier": 2,
        "category": "relative_to_absolute",
        "title": "In two days -> today (query two days later)",
        "memories": [
            {
                "id": "target",
                "content": "Board review session happens in two days at 2pm sharp",
                "role": "target",
                "timestamp": "202603080900",
            },
            {
                "id": "distractor_1",
                "content": "Board review from last month concluded with full budget approval",
                "role": "distractor",
                "timestamp": "202603080900",
            },
            {
                "id": "distractor_2",
                "content": "Board review scheduled for next Tuesday will cover the annual strategy proposals",
                "role": "distractor",
                "timestamp": "202603080900",
            },
            {
                "id": "distractor_3",
                "content": "Board review yesterday focused exclusively on risk management and compliance issues",
                "role": "distractor",
                "timestamp": "202603080900",
            },
        ],
        "query": "Any executive meetings on the calendar for today?",
        "query_timestamp": "202603100900",
        "notes": "'In two days' from Mar 8 = Mar 10 = 'today' from query. All mention 'board review'. Distractors: past (last month, yesterday), future (next Tuesday).",
    },
    {
        "id": "T2-05",
        "tier": 2,
        "category": "relative_to_absolute",
        "title": "In five days -> tomorrow (query four days later)",
        "memories": [
            {
                "id": "target",
                "content": "Conference registration window closes in five days",
                "role": "target",
                "timestamp": "202603050900",
            },
            {
                "id": "distractor_1",
                "content": "Conference registration opened with early bird pricing three weeks ago",
                "role": "distractor",
                "timestamp": "202603050900",
            },
            {
                "id": "distractor_2",
                "content": "Conference registration fees increase after the first two hundred attendees sign up",
                "role": "distractor",
                "timestamp": "202603050900",
            },
            {
                "id": "distractor_3",
                "content": "Conference registration is expected to sell out well before the event date in April",
                "role": "distractor",
                "timestamp": "202603050900",
            },
        ],
        "query": "Is there a signup cutoff approaching tomorrow?",
        "query_timestamp": "202603090900",
        "notes": "'In five days' from Mar 5 = Mar 10 = 'tomorrow' from Mar 9. All about 'conference registration'. Distractors: past opening, capacity-based (not time-based), future prediction.",
    },
    # ── State Conflict (5 cases) ──────────────────────────────────────
    {
        "id": "T2-06",
        "tier": 2,
        "category": "state_conflict",
        "title": "Framework migration: React -> Svelte",
        "memories": [
            {
                "id": "distractor_1",
                "content": "Project Falcon uses React for its frontend framework",
                "role": "distractor",
                "timestamp": "202601150900",
            },
            {
                "id": "distractor_2",
                "content": "Project Falcon frontend framework evaluation considered Vue and Svelte as React alternatives",
                "role": "distractor",
                "timestamp": "202602010900",
            },
            {
                "id": "distractor_3",
                "content": "Project Falcon began the experimental Svelte migration branch for performance testing",
                "role": "distractor",
                "timestamp": "202602150900",
            },
            {
                "id": "target",
                "content": "Project Falcon frontend was completely rewritten using Svelte last month",
                "role": "target",
                "timestamp": "202603010900",
            },
        ],
        "query": "What UI framework does Project Falcon currently rely on?",
        "query_timestamp": "202603100900",
        "notes": "All memories about Project Falcon's frontend evolution. Timeline: Jan (React) -> Feb (evaluation) -> Feb (experiment) -> Mar (full Svelte migration). System must select the latest state.",
    },
    {
        "id": "T2-07",
        "tier": 2,
        "category": "state_conflict",
        "title": "Personnel handoff: Sarah -> Marcus",
        "memories": [
            {
                "id": "distractor_1",
                "content": "Sarah is the point of contact for all vendor negotiations",
                "role": "distractor",
                "timestamp": "202602010900",
            },
            {
                "id": "distractor_2",
                "content": "Sarah and Marcus are collaborating on the vendor management transition plan",
                "role": "distractor",
                "timestamp": "202602200900",
            },
            {
                "id": "target",
                "content": "Marcus has taken over all supplier relationship responsibilities from Sarah",
                "role": "target",
                "timestamp": "202603050900",
            },
            {
                "id": "distractor_3",
                "content": "Sarah will continue advising on vendor strategy through the end of the quarter",
                "role": "distractor",
                "timestamp": "202603050900",
            },
        ],
        "query": "Who handles our external procurement partnerships right now?",
        "query_timestamp": "202603100900",
        "notes": "'Vendor negotiations' vs 'supplier relationships' vs 'procurement partnerships' — all synonyms. Timeline shows handoff: Sarah (Feb) -> transition (late Feb) -> Marcus owns (Mar 5). Distractor_3 has same timestamp as target but mentions advisory role vs ownership.",
    },
    {
        "id": "T2-08",
        "tier": 2,
        "category": "state_conflict",
        "title": "Meeting room closure override",
        "memories": [
            {
                "id": "distractor_1",
                "content": "Weekly all-hands meeting is held in Conference Room B on the third floor",
                "role": "distractor",
                "timestamp": "202602100900",
            },
            {
                "id": "distractor_2",
                "content": "Conference Room B was upgraded with new video conferencing equipment last month",
                "role": "distractor",
                "timestamp": "202602200900",
            },
            {
                "id": "target",
                "content": "All third floor meeting rooms are closed for renovation through the end of April",
                "role": "target",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_3",
                "content": "The all-hands meeting agenda typically covers quarterly goals and team updates",
                "role": "distractor",
                "timestamp": "202603010900",
            },
        ],
        "query": "Where should I go for the all-hands gathering this week?",
        "query_timestamp": "202603100900",
        "notes": "Multiple memories about Conference Room B and all-hands meetings. Latest memory (Mar 1) invalidates the location. Distractors include equipment upgrade and agenda content (same timestamp as target but irrelevant).",
    },
    {
        "id": "T2-09",
        "tier": 2,
        "category": "state_conflict",
        "title": "CI/CD migration: Jenkins -> GitHub Actions",
        "memories": [
            {
                "id": "distractor_1",
                "content": "Continuous integration builds run on the Jenkins server in the datacenter",
                "role": "distractor",
                "timestamp": "202601200900",
            },
            {
                "id": "distractor_2",
                "content": "Jenkins pipeline configuration requires Groovy scripting for custom build steps",
                "role": "distractor",
                "timestamp": "202602010900",
            },
            {
                "id": "distractor_3",
                "content": "The team evaluated GitHub Actions and CircleCI as potential Jenkins replacements",
                "role": "distractor",
                "timestamp": "202602150900",
            },
            {
                "id": "target",
                "content": "All CI/CD pipelines migrated to GitHub Actions effective last week",
                "role": "target",
                "timestamp": "202603030900",
            },
        ],
        "query": "What automation platform handles our build and deployment workflows now?",
        "query_timestamp": "202603100900",
        "notes": "'Automation platform' not 'CI/CD'. Timeline: Jan (Jenkins active) -> Feb (Jenkins details) -> Feb (evaluation phase) -> Mar (GitHub Actions migration complete).",
    },
    {
        "id": "T2-10",
        "tier": 2,
        "category": "state_conflict",
        "title": "Python deprecation: 3.8 -> 3.11",
        "memories": [
            {
                "id": "distractor_1",
                "content": "All production codebases must be compatible with Python 3.8 or higher",
                "role": "distractor",
                "timestamp": "202511100900",
            },
            {
                "id": "distractor_2",
                "content": "Python 3.8 remains widely used despite the release of newer versions",
                "role": "distractor",
                "timestamp": "202601150900",
            },
            {
                "id": "target",
                "content": "Python 3.8 and 3.9 support was officially dropped from our projects as of February",
                "role": "target",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_3",
                "content": "Python 3.11 offers performance improvements over earlier interpreter releases",
                "role": "distractor",
                "timestamp": "202603010900",
            },
        ],
        "query": "What interpreter version do our codebases need to support right now?",
        "query_timestamp": "202603100900",
        "notes": "'Interpreter version' not 'Python version'. Timeline: Nov 2025 (3.8+ required) -> Jan (general 3.8 usage) -> Feb (3.8/3.9 dropped). Distractor_3 same timestamp but discusses benefits not requirements.",
    },
    # ── Temporal Arithmetic / Paraphrase (5 cases) ────────────────────
    {
        "id": "T2-11",
        "tier": 2,
        "category": "temporal_arithmetic",
        "title": "Prerequisite chain: audit before launch date",
        "memories": [
            {
                "id": "target",
                "content": "The security audit must be finalized before the product goes live",
                "role": "target",
                "timestamp": "202603050900",
            },
            {
                "id": "support",
                "content": "Product go-live date locked in for March 20th",
                "role": "target",
                "timestamp": "202603050900",
            },
            {
                "id": "distractor_1",
                "content": "The security audit for last quarter's release was completed on schedule in February",
                "role": "distractor",
                "timestamp": "202603050900",
            },
            {
                "id": "distractor_2",
                "content": "Product marketing materials need final approval before the April campaign launch",
                "role": "distractor",
                "timestamp": "202603050900",
            },
        ],
        "query": "What tasks need to wrap up before March 20th?",
        "query_timestamp": "202603100900",
        "notes": "Requires linking 'before product goes live' + 'go-live = March 20' to answer 'security audit before March 20'. Distractors: past audit (February), different deadline (April).",
    },
    {
        "id": "T2-12",
        "tier": 2,
        "category": "temporal_arithmetic",
        "title": "Quarterly cycle inference",
        "memories": [
            {
                "id": "target",
                "content": "Financial statements are always filed on the last business day of each fiscal quarter",
                "role": "target",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_1",
                "content": "Financial statements for the previous quarter were submitted ahead of the deadline",
                "role": "distractor",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_2",
                "content": "Annual financial reporting occurs at the end of the fiscal year in December",
                "role": "distractor",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_3",
                "content": "Monthly financial summaries are distributed to department heads by the fifth business day",
                "role": "distractor",
                "timestamp": "202603010900",
            },
        ],
        "query": "When is the next regulatory filing obligation?",
        "query_timestamp": "202603150900",
        "notes": "Requires knowing: queried mid-March -> Q1 ends March 31 -> last business day of Q1 is the answer. Distractors: past quarter, annual cycle, monthly cycle.",
    },
    {
        "id": "T2-13",
        "tier": 2,
        "category": "temporal_arithmetic",
        "title": "Biannual cycle inference",
        "memories": [
            {
                "id": "target",
                "content": "Employee evaluations take place biannually in June and December without exception",
                "role": "target",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_1",
                "content": "Employee evaluation results from December showed improved satisfaction scores across all departments",
                "role": "distractor",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_2",
                "content": "New employee probationary reviews occur quarterly during the first year of employment",
                "role": "distractor",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_3",
                "content": "Annual compensation adjustments are typically announced in March following budget approval",
                "role": "distractor",
                "timestamp": "202603010900",
            },
        ],
        "query": "When is the next round of staff performance assessments?",
        "query_timestamp": "202603150900",
        "notes": "'Staff performance assessments' not 'employee evaluations'. Requires: March query -> next is June. Distractors: past results (December), quarterly cycle (different schedule), annual cycle (compensation not evaluation).",
    },
    {
        "id": "T2-14",
        "tier": 2,
        "category": "temporal_arithmetic",
        "title": "Duration-from-date calculation",
        "memories": [
            {
                "id": "target",
                "content": "The commercial lease expires exactly eighteen months from the signing date of September 2024",
                "role": "target",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_1",
                "content": "The previous office lease was signed for a five-year term in 2019",
                "role": "distractor",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_2",
                "content": "Commercial lease negotiations typically begin six months before the current agreement ends",
                "role": "distractor",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_3",
                "content": "Office space requirements are reviewed annually during strategic planning in January",
                "role": "distractor",
                "timestamp": "202603010900",
            },
        ],
        "query": "Do we need to find alternative office space soon?",
        "query_timestamp": "202603100900",
        "notes": "Sep 2024 + 18 months = March 2026 = NOW. Distractors: past lease (2019), general advice (6 months before), annual review cycle (January).",
    },
    {
        "id": "T2-15",
        "tier": 2,
        "category": "temporal_arithmetic",
        "title": "Multi-memory temporal chain (recurring + last-run)",
        "memories": [
            {
                "id": "target",
                "content": "Automated backups execute on a 72-hour cycle starting from midnight each Sunday",
                "role": "target",
                "timestamp": "202603010900",
            },
            {
                "id": "support",
                "content": "The latest backup run completed without errors on Wednesday at midnight",
                "role": "target",
                "timestamp": "202603041200",
            },
            {
                "id": "distractor_1",
                "content": "Database backups run nightly at 2am with a 24-hour retention policy",
                "role": "distractor",
                "timestamp": "202603010900",
            },
            {
                "id": "distractor_2",
                "content": "The backup system was upgraded last month to improve storage efficiency",
                "role": "distractor",
                "timestamp": "202603041200",
            },
        ],
        "query": "When will the storage snapshots run again?",
        "query_timestamp": "202603051400",
        "notes": "'Storage snapshots' not 'backups'. Requires: last ran Wed midnight + 72h = Sat midnight. Distractors: different backup schedule (nightly 24h), upgrade info (not schedule).",
    },
]


# ---------------------------------------------------------------------------
# Tier 3 — MULTI-HOP / INDIRECT CONNECTION
#
# Pattern A (chain): Query connects to answer only through 2+ memories
#   (A->B, B->C; query about A->C).
# Pattern B (paraphrase): Same meaning, ZERO lexical overlap between
#   memory content and query.
# Pattern C (world_knowledge): Connection requires implicit knowledge not
#   stated in any memory.
# Pattern D (negation): Query asks about what is NOT true; retrieval must
#   respect logical polarity.
#
# CRITICAL: Query must have near-zero keyword overlap with target memories.
# The connection must require INFERENCE, not keyword matching.
# ---------------------------------------------------------------------------

TIER_3: list[dict[str, Any]] = [
    # ── 2-Hop Inference Chain (5 cases) ───────────────────────────────
    {
        "id": "T3-01",
        "tier": 3,
        "category": "chain_2hop",
        "title": "Person -> division -> project",
        "memories": [
            {
                "id": "hop1",
                "content": "Elena was promoted to lead the infrastructure division last quarter",
                "role": "target",
            },
            {
                "id": "hop2",
                "content": "The infrastructure division owns the cloud migration initiative end-to-end",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "Elena previously managed the platform engineering team before her recent promotion",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "The cloud migration initiative was originally proposed by the CTO in the annual strategy meeting",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The infrastructure division recently completed the datacenter consolidation project ahead of schedule",
                "role": "distractor",
            },
        ],
        "query": "Who is accountable for the shift to cloud services?",
        "notes": "'Accountable' not 'lead/owns', 'shift to cloud services' not 'cloud migration initiative'. Requires: Elena -> infra division -> cloud migration. Distractors break the chain at different points: Elena's past role, cloud initiative origin, infra's other projects.",
    },
    {
        "id": "T3-02",
        "tier": 3,
        "category": "chain_2hop",
        "title": "Factory halt -> supply dependency -> delivery delay",
        "memories": [
            {
                "id": "hop1",
                "content": "The Shenzhen facility halted assembly lines due to a critical component shortage",
                "role": "target",
            },
            {
                "id": "hop2",
                "content": "All second-quarter product shipments depend entirely on output from the Shenzhen facility",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The Shenzhen facility achieved record production efficiency last quarter with zero defects",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "First-quarter customer deliveries exceeded projections by fifteen percent",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Component suppliers in Vietnam are expanding capacity to meet growing demand",
                "role": "distractor",
            },
        ],
        "query": "Why might our Q2 customer deliveries fall behind schedule?",
        "notes": "'Customer deliveries fall behind schedule' not 'shipments' or 'halted'. Requires chaining: shortage -> halt -> dependency -> delay. Distractors: past success (last quarter), different quarter (Q1), different supplier (Vietnam not Shenzhen).",
    },
    {
        "id": "T3-03",
        "tier": 3,
        "category": "chain_2hop",
        "title": "Policy -> affected group -> individual",
        "memories": [
            {
                "id": "hop1",
                "content": "New attendance policy mandates all contract workers be physically present three days per week",
                "role": "target",
            },
            {
                "id": "hop2",
                "content": "David joined the organization last month as a contract UX researcher",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "Full-time employees are required to work from the office four days per week under the new policy",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "David previously worked remotely at a fully distributed startup for two years",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The UX research team typically collaborates in person during user testing sessions",
                "role": "distractor",
            },
        ],
        "query": "How often does David need to show up at the office?",
        "notes": "Requires: David = contract worker -> contract worker policy = 3 days. Distractors: wrong policy group (full-time=4 days), David's past (remote work), team norms (not policy).",
    },
    {
        "id": "T3-04",
        "tier": 3,
        "category": "chain_2hop",
        "title": "VP -> reports to CRO -> CRO identity",
        "memories": [
            {
                "id": "hop1",
                "content": "The VP of Sales reports directly to the Chief Revenue Officer",
                "role": "target",
            },
            {
                "id": "hop2",
                "content": "Karen was appointed as the new Chief Revenue Officer in January",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The VP of Sales previously led the regional sales team in the Northeast territory",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Karen started her career in sales operations before moving into executive leadership",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The Chief Marketing Officer and Chief Revenue Officer collaborate closely on go-to-market strategy",
                "role": "distractor",
            },
        ],
        "query": "Who is the VP of Sales' direct supervisor?",
        "notes": "'Direct supervisor' not 'reports to'. Requires: VP Sales -> CRO -> Karen. Distractors: VP's past role, Karen's past role, CRO's peer relationships.",
    },
    {
        "id": "T3-05",
        "tier": 3,
        "category": "chain_2hop",
        "title": "Budget owner -> team -> headcount freeze",
        "memories": [
            {
                "id": "hop1",
                "content": "The marketing department's annual spend is controlled by the CFO's office",
                "role": "target",
            },
            {
                "id": "hop2",
                "content": "The CFO's office has frozen all new hiring requisitions until further notice",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The marketing department is actively recruiting for contractors to support the product launch campaign",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Marketing headcount grew by twelve percent last fiscal year to support expansion goals",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The engineering department received approval for three additional hires in specialized roles",
                "role": "distractor",
            },
        ],
        "query": "Can the marketing group bring on additional staff right now?",
        "notes": "'Bring on additional staff' not 'hiring requisitions'. Requires: marketing -> CFO controls budget -> CFO froze hiring -> no. Distractors: contractor exception, past growth, different department approval.",
    },
    # ── Zero-Overlap Paraphrase (5 cases) ─────────────────────────────
    {
        "id": "T3-06",
        "tier": 3,
        "category": "paraphrase",
        "title": "Revenue beat expectations (full vocabulary swap)",
        "memories": [
            {
                "id": "target",
                "content": "Quarterly revenue exceeded Wall Street analyst consensus by a significant margin",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "Quarterly expenses came in slightly below the finance team's initial budget projections",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Annual revenue growth has remained steady at approximately twelve percent year over year",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Market analysts anticipate continued strong performance in the upcoming fiscal quarter",
                "role": "distractor",
            },
        ],
        "query": "Did the company's three-month income surpass what the financial forecasters predicted?",
        "notes": "Every content word is swapped: 'quarterly'->'three-month', 'revenue'->'income', 'exceeded'->'surpass', 'analysts'->'forecasters', 'consensus'->'predicted'. Distractors: expenses vs revenue, annual vs quarterly, future predictions vs past results.",
    },
    {
        "id": "T3-07",
        "tier": 3,
        "category": "paraphrase",
        "title": "CTO advocates microservices (full vocabulary swap)",
        "memories": [
            {
                "id": "target",
                "content": "The CTO advocated for adopting a microservices architecture during the annual planning session",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The VP of Engineering proposed maintaining the existing monolithic application for stability reasons",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Microservices migration discussions have been ongoing for several months across multiple teams",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The annual planning session covered topics including cloud migration and API strategy",
                "role": "distractor",
            },
        ],
        "query": "Who championed splitting the monolith into smaller independent modules at the yearly strategy offsite?",
        "notes": "'Championed' not 'advocated', 'splitting monolith into modules' not 'microservices architecture', 'yearly strategy offsite' not 'annual planning session'. Distractors: opposing view (VP), generic discussion (no advocate), different topics.",
    },
    {
        "id": "T3-08",
        "tier": 3,
        "category": "paraphrase",
        "title": "Customer churn after price change (full vocabulary swap)",
        "memories": [
            {
                "id": "target",
                "content": "Customer attrition climbed to eight percent following the latest pricing adjustment",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "New subscriber acquisition increased by twelve percent during the promotional campaign period",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "The pricing committee is reviewing additional fee structure modifications for next quarter",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Customer satisfaction scores remained stable despite concerns about competitive pricing pressure",
                "role": "distractor",
            },
        ],
        "query": "How many subscribers cancelled after we revised our fee structure?",
        "notes": "'Subscribers cancelled' not 'customer attrition', 'revised fee structure' not 'pricing adjustment'. Even 'eight percent' vs 'how many' tests numeric comprehension. Distractors: acquisition vs attrition, future changes vs past results, satisfaction vs churn.",
    },
    {
        "id": "T3-09",
        "tier": 3,
        "category": "paraphrase",
        "title": "Board approves acquisition (full vocabulary swap)",
        "memories": [
            {
                "id": "target",
                "content": "The board of directors unanimously greenlit the purchase of a Scandinavian fintech startup",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The executive team is conducting due diligence on several potential acquisition targets in Europe",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Board meetings in previous quarters focused on organic growth rather than strategic acquisitions",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "The fintech sector in Scandinavia has attracted significant venture capital investment recently",
                "role": "distractor",
            },
        ],
        "query": "Did the governing body consent to acquiring the Nordic financial technology venture?",
        "notes": "'Governing body' not 'board of directors', 'consent' not 'greenlit', 'acquiring' not 'purchase', 'Nordic' not 'Scandinavian', 'venture' not 'startup'. Distractors: still evaluating (not approved), past strategy (organic not M&A), sector investment (not acquisition).",
    },
    {
        "id": "T3-10",
        "tier": 3,
        "category": "paraphrase",
        "title": "Engineer resignation (full vocabulary swap)",
        "memories": [
            {
                "id": "target",
                "content": "The principal backend engineer submitted her resignation citing burnout and work-life imbalance",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "Several junior developers expressed concerns about workload balance during the recent employee survey",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "The backend engineering team is actively hiring to expand capacity for upcoming projects",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "A senior frontend developer was promoted to principal engineer last quarter",
                "role": "distractor",
            },
        ],
        "query": "Which senior server-side developer decided to leave because of exhaustion and personal life conflicts?",
        "notes": "'Senior server-side developer' not 'principal backend engineer', 'decided to leave' not 'submitted resignation', 'exhaustion' not 'burnout'. Distractors: junior developers (not senior), hiring (not resignation), frontend promotion (not backend resignation).",
    },
    # ── World Knowledge / Implicit Connection (3 cases) ───────────────
    {
        "id": "T3-11",
        "tier": 3,
        "category": "world_knowledge",
        "title": "Elon -> Tesla implicit link",
        "memories": [
            {
                "id": "hop1",
                "content": "Elon announced a ten percent workforce reduction across all operating units",
                "role": "target",
            },
            {
                "id": "hop2",
                "content": "The Austin gigafactory will bear the brunt of the upcoming headcount changes",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "Elon's recent social media posts sparked controversy about free speech policies",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "The Austin facility recently expanded its solar panel installation capacity",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Electric vehicle sales in Texas increased by twenty percent compared to last year",
                "role": "distractor",
            },
        ],
        "query": "How will the electric vehicle manufacturer's layoffs affect production in Texas?",
        "notes": "Requires world knowledge: Elon = Elon Musk = Tesla, Austin gigafactory = Tesla + Texas, workforce reduction = layoffs. Distractors: different Elon topic (social media), Austin facility different context (solar), EV sales (not production/layoffs).",
    },
    {
        "id": "T3-12",
        "tier": 3,
        "category": "world_knowledge",
        "title": "Federal Reserve -> central bank implicit link",
        "memories": [
            {
                "id": "target",
                "content": "The Fed Chair testified about potential rate trajectory shifts at the Jackson Hole symposium",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The European Central Bank president discussed inflation concerns at the Frankfurt banking conference",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Jackson Hole Mountain Resort attracts thousands of skiers annually during winter season",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Federal Reserve regional governors meet quarterly to coordinate monetary policy implementation",
                "role": "distractor",
            },
        ],
        "query": "What did the head of America's central banking system discuss at the Wyoming economics gathering?",
        "notes": "'Head of America's central banking system' not 'Fed Chair', 'Wyoming economics gathering' not 'Jackson Hole symposium'. Requires knowing Jackson Hole is in Wyoming. Distractors: different central bank (ECB), Jackson Hole tourism (not symposium), Fed meetings (not Jackson Hole).",
    },
    {
        "id": "T3-13",
        "tier": 3,
        "category": "world_knowledge",
        "title": "COP summit -> UN climate conference",
        "memories": [
            {
                "id": "target",
                "content": "The 1.5 degree Celsius warming threshold was reaffirmed at the latest COP summit",
                "role": "target",
            },
            {
                "id": "distractor_1",
                "content": "The Paris Agreement initially established the two degree warming limit with aspirations for 1.5 degrees",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "United Nations sustainability goals include emissions reductions across multiple sectors by 2030",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Climate scientists warn that current warming trends exceed historical temperature baselines",
                "role": "distractor",
            },
        ],
        "query": "What temperature goal did delegates commit to at the annual United Nations environmental negotiations?",
        "notes": "'United Nations environmental negotiations' not 'COP summit'. Requires knowing COP = UNFCCC Conference of the Parties. Distractors: past agreement (Paris), broader UN goals (not temperature specific), scientific warnings (not policy commitment).",
    },
    # ── Negation / Contrast (2 cases) ─────────────────────────────────
    {
        "id": "T3-14",
        "tier": 3,
        "category": "negation",
        "title": "Python: suitable vs unsuitable domains",
        "memories": [
            {
                "id": "distractor_1",
                "content": "Python excels at rapid prototyping, data analysis, and machine learning workloads",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Python's extensive library ecosystem makes it ideal for web development and automation tasks",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Python has become the dominant language for scientific computing and numerical analysis",
                "role": "distractor",
            },
            {
                "id": "target",
                "content": "Python is generally a poor choice for latency-sensitive mobile applications and GPU-bound game engines",
                "role": "target",
            },
        ],
        "query": "For which types of software projects is Python considered inappropriate?",
        "notes": "All memories discuss Python's applicability to different domains. Query asks for NEGATIVE cases ('inappropriate'). System must select the 'poor choice' memory among three positive statements.",
    },
    {
        "id": "T3-15",
        "tier": 3,
        "category": "negation",
        "title": "Microservices: benefits vs drawbacks",
        "memories": [
            {
                "id": "distractor_1",
                "content": "Microservices enable independent scaling and faster deployment cycles for large teams",
                "role": "distractor",
            },
            {
                "id": "distractor_2",
                "content": "Microservices architecture allows different teams to choose optimal technology stacks for their specific needs",
                "role": "distractor",
            },
            {
                "id": "distractor_3",
                "content": "Microservices improve fault isolation so failures in one component don't bring down the entire system",
                "role": "distractor",
            },
            {
                "id": "target",
                "content": "Microservices introduce significant operational overhead including distributed tracing, service mesh complexity, and cascading failure risks",
                "role": "target",
            },
        ],
        "query": "What are the downsides of breaking a system into many small services?",
        "notes": "'Downsides' targets the negative memory. All highly relevant to 'microservices'. System must distinguish the negative statement among three positive benefits. Note distractor_3 mentions 'failures' but in a positive framing (fault isolation).",
    },
]


# ---------------------------------------------------------------------------
# Noise corpus — loaded into every test case so the system must discriminate.
# These are topically diverse and unrelated to any specific test case.
# With k=5, the system must pick the right 5 out of ~25 total memories.
# ---------------------------------------------------------------------------

NOISE_MEMORIES: list[dict[str, str]] = [
    {
        "id": "noise_01",
        "content": "The average lifespan of a domestic cat is between 12 and 18 years depending on breed and care",
    },
    {
        "id": "noise_02",
        "content": "Reinforced concrete was patented in 1867 by Joseph Monier, a French gardener",
    },
    {
        "id": "noise_03",
        "content": "The International Space Station orbits Earth approximately every 90 minutes at 28,000 km/h",
    },
    {
        "id": "noise_04",
        "content": "Sourdough bread requires a fermentation period of 12 to 24 hours for proper flavor development",
    },
    {
        "id": "noise_05",
        "content": "The Mariana Trench reaches a maximum depth of approximately 11,034 meters below sea level",
    },
    {
        "id": "noise_06",
        "content": "Photosynthesis converts carbon dioxide and water into glucose using sunlight as energy",
    },
    {
        "id": "noise_07",
        "content": "The first commercial telephone exchange opened in New Haven, Connecticut in January 1878",
    },
    {
        "id": "noise_08",
        "content": "Antarctic krill biomass is estimated at around 379 million tonnes, making it one of the most abundant species",
    },
    {
        "id": "noise_09",
        "content": "Regular exercise reduces the risk of cardiovascular disease by improving blood circulation and lowering cholesterol",
    },
    {
        "id": "noise_10",
        "content": "The Gutenberg printing press, invented around 1440, revolutionized the spread of written knowledge across Europe",
    },
    {
        "id": "noise_11",
        "content": "Titanium has a strength-to-weight ratio higher than steel, making it ideal for aerospace components",
    },
    {
        "id": "noise_12",
        "content": "The Sahara Desert covers approximately 9.2 million square kilometers across northern Africa",
    },
    {
        "id": "noise_13",
        "content": "Beethoven completed his Ninth Symphony in 1824, two years before his death",
    },
    {
        "id": "noise_14",
        "content": "The human brain consumes roughly 20 percent of the body's total energy despite being only 2 percent of body weight",
    },
    {
        "id": "noise_15",
        "content": "Container shipping handles over 80 percent of global trade by volume through standardized intermodal containers",
    },
    {
        "id": "noise_16",
        "content": "The boiling point of water decreases at higher altitudes due to lower atmospheric pressure",
    },
    {
        "id": "noise_17",
        "content": "Renaissance art flourished in Florence during the 15th century under the patronage of the Medici family",
    },
    {
        "id": "noise_18",
        "content": "Coral reefs support approximately 25 percent of all marine species despite covering less than one percent of the ocean floor",
    },
    {
        "id": "noise_19",
        "content": "The Trans-Siberian Railway spans 9,289 kilometers from Moscow to Vladivostok across seven time zones",
    },
    {
        "id": "noise_20",
        "content": "Honeybees communicate the location of food sources through a series of movements known as the waggle dance",
    },
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

ALL_FIXTURES: list[dict[str, Any]] = TIER_1 + TIER_2 + TIER_3


def get_fixtures(tiers: list[int] | None = None) -> list[dict[str, Any]]:
    if tiers is None:
        return ALL_FIXTURES
    return [f for f in ALL_FIXTURES if f["tier"] in tiers]


def get_fixture_by_id(fixture_id: str) -> dict[str, Any] | None:
    for f in ALL_FIXTURES:
        if f["id"] == fixture_id:
            return f
    return None
