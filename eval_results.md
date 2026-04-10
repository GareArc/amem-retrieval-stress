# A-mem Retrieval Evaluation Report

## How to Read This Report

Each test case stores a set of **memories** (with known roles) into A-mem, then runs a **query** designed to require understanding beyond keyword matching. We compare what the system retrieved against ground truth.

**Two search methods are compared side by side:**

- `search()` -- pure vector similarity (ChromaDB cosine distance)
- `search_agentic()` -- vector similarity + associative link expansion

**Score** is ChromaDB's cosine distance. **Lower = more relevant.** A score of 0.8 is a better match than 1.4.

**Metrics (computed per case):**

| Metric | Meaning |
|--------|---------|
| Recall | Fraction of target memories found in top-k results (1.0 = all found) |
| Precision | Fraction of returned results that are actual targets (1.0 = no noise) |
| MRR | Reciprocal rank of the first correct result (1.0 = correct result ranked #1) |
| Distractors | Count of wrong-sense / outdated memories that appeared in results |

**Verdict:**

- **PASS** -- all targets retrieved, zero distractors
- **PARTIAL** -- some targets found, but missing results or distractor contamination
- **FAIL** -- no targets retrieved
- **ERR** -- test case encountered a runtime error

**Memory roles in tables:**

- **TARGET** -- this memory *should* be retrieved for the query
- **DISTR** -- this memory shares vocabulary with the target but is the *wrong* answer
- **NOISE** -- one of 20 unrelated filler memories loaded per case to force discrimination

## Shared Noise Corpus

These 20 unrelated memories are added alongside each case's test memories. With k=5, the system must retrieve the right memories from ~22 total.

| # | Content |
|---|---------|
| 1 | The average lifespan of a domestic cat is between 12 and 18 years depending on breed and care |
| 2 | The Mariana Trench reaches a maximum depth of approximately 11,034 meters below sea level |
| 3 | Photosynthesis converts carbon dioxide and water into glucose using sunlight as energy |
| 4 | Beethoven completed his Ninth Symphony in 1824, two years before his death |
| 5 | The Sahara Desert covers approximately 9.2 million square kilometers across northern Africa |

## Summary

| Tier | Pass (search) | Pass (agentic) | Avg Recall (S) | Avg Recall (A) | Avg MRR (S) | Avg MRR (A) |
|------|--------------|----------------|----------------|----------------|-------------|-------------|
| **Tier 1: AMBIGUITY** | 0/15 (0%) | 0/15 (0%) | 1.000 | 1.000 | 1.000 | 1.000 |
| **Tier 2: TEMPORAL** | 0/15 (0%) | 0/15 (0%) | 0.667 | 0.833 | 0.433 | 0.522 |
| **Tier 3: MULTI-HOP** | 0/15 (0%) | 0/15 (0%) | 0.467 | 0.533 | 0.378 | 0.411 |
| **Overall** | 0/45 (0%) | 0/45 (0%) | | | | |

## Tier 1: Ambiguity

### PARTIAL T1-01: Apple: tech company vs fruit

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | Apple's quarterly revenue reached $94 billion driven by strong iPhone and services growth |
| DISTR | The farmer's market had the freshest organic apples I've tasted all season |
| DISTR | Apple orchards in Washington State reported record harvest yields this quarter |
| DISTR | Apple pie remains the top-selling dessert at the bakery according to quarterly sales data |

**Query:** How did the Cupertino tech giant perform financially last quarter?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.6533 | Apple's quarterly revenue reached $94 billion driven by strong iPhone and services growth |
| 2 | DISTR distractor | 0.7614 | Apple pie remains the top-selling dessert at the bakery according to quarterly sales data |
| 3 | DISTR distractor | 0.7614 | The farmer's market had the freshest organic apples I've tasted all season |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.6533 | Apple's quarterly revenue reached $94 billion driven by strong iPhone and services growth |
| 2 | DISTR distractor | 0.7614 | Apple pie remains the top-selling dessert at the bakery according to quarterly sales data |
| 3 | DISTR distractor | 0.9077 | Apple orchards in Washington State reported record harvest yields this quarter |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> Query uses 'Cupertino tech giant' (no 'Apple'), 'perform financially' (no 'revenue'). Requires Apple = Cupertino tech giant. Multiple fruit-sense distractors including one with 'quarterly' to increase confusion.

---

### PARTIAL T1-02: Python: programming language vs snake

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | We migrated our backend services to Python for better machine learning integration |
| DISTR | The Burmese python at the reptile exhibit measured over fifteen feet in length |
| DISTR | Python populations in the Florida Everglades have grown rapidly in recent years |
| DISTR | The reticulated python is known for its impressive constriction capabilities and hunting efficiency |

**Query:** What scripting language was chosen for the server-side rewrite?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.8180 | We migrated our backend services to Python for better machine learning integration |
| 2 | DISTR distractor | 0.8579 | The reticulated python is known for its impressive constriction capabilities and hunting efficiency |
| 3 | DISTR distractor | 0.8579 | The Burmese python at the reptile exhibit measured over fifteen feet in length |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.8180 | We migrated our backend services to Python for better machine learning integration |
| 2 | DISTR distractor | 0.8579 | The reticulated python is known for its impressive constriction capabilities and hunting efficiency |
| 3 | DISTR distractor | 0.9131 | Python populations in the Florida Everglades have grown rapidly in recent years |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> Query says 'scripting language' and 'server-side rewrite' — no 'Python', 'backend', or 'machine learning'. Multiple snake-sense distractors.

---

### PARTIAL T1-03: Java: programming language vs Indonesian island

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The garbage collection pauses in our Java runtime caused latency spikes across production |
| DISTR | We visited ancient Buddhist temples on the island of Java during our backpacking trip |
| DISTR | Java coffee production reached record volumes during the latest harvest season |
| DISTR | The population density on Java exceeds 1,100 people per square kilometer making it one of the most crowded regions |

**Query:** What caused the application performance degradation in the runtime environment?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5335 | The garbage collection pauses in our Java runtime caused latency spikes across production |
| 2 | DISTR distractor | 0.8586 | We visited ancient Buddhist temples on the island of Java during our backpacking trip |
| 3 | DISTR distractor | 0.8824 | The population density on Java exceeds 1,100 people per square kilometer making it one of the most crowded regions |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5335 | The garbage collection pauses in our Java runtime caused latency spikes across production |
| 2 | DISTR distractor | 0.8586 | We visited ancient Buddhist temples on the island of Java during our backpacking trip |
| 3 | DISTR distractor | 0.8824 | The population density on Java exceeds 1,100 people per square kilometer making it one of the most crowded regions |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> Query avoids 'Java', 'garbage collection', 'latency'. Uses 'application performance degradation' and 'runtime environment'. Multiple island/geography-sense distractors.

---

### PARTIAL T1-04: Mercury: planet vs toxic element

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | Mercury's surface temperature fluctuates between minus 180 and plus 430 degrees Celsius |
| DISTR | Mercury contamination in the local river exceeded safe drinking water standards by a factor of three |
| DISTR | Mercury levels in the fish population have prompted new health warnings from environmental authorities |
| DISTR | The old mercury thermometer showed extreme temperature variations before it was replaced with digital sensors |

**Query:** Which celestial body has the most extreme day-night temperature variation in our solar system?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.7130 | Mercury's surface temperature fluctuates between minus 180 and plus 430 degrees Celsius |
| 2 | DISTR distractor | 0.8666 | The old mercury thermometer showed extreme temperature variations before it was replaced with digital sensors |
| 3 | DISTR distractor | 0.8666 | Mercury levels in the fish population have prompted new health warnings from environmental authorities |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.7130 | Mercury's surface temperature fluctuates between minus 180 and plus 430 degrees Celsius |
| 2 | DISTR distractor | 0.8666 | The old mercury thermometer showed extreme temperature variations before it was replaced with digital sensors |
| 3 | NOISE noise | 0.9001 | Photosynthesis converts carbon dioxide and water into glucose using sunlight as energy |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 1 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> Query says 'celestial body' and 'solar system' — no 'Mercury', 'surface', or 'degrees'. Multiple element/substance-sense distractors, with distractor_3 mentioning 'temperature' for extra confusion.

---

### PARTIAL T1-05: Mars: planet vs candy corporation

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The Perseverance rover collected rock samples in the Jezero Crater on Mars |
| DISTR | Mars Incorporated announced a global recall of certain Snickers and Milky Way products |
| DISTR | Mars chocolate bars saw record sales during the holiday season exceeding analyst expectations |
| DISTR | The Mars family maintains private ownership of the confectionery company founded in 1911 |

**Query:** What geological specimens has the robotic explorer gathered from the red planet?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5470 | The Perseverance rover collected rock samples in the Jezero Crater on Mars |
| 2 | DISTR distractor | 0.8515 | Mars Incorporated announced a global recall of certain Snickers and Milky Way products |
| 3 | DISTR distractor | 0.8589 | The Mars family maintains private ownership of the confectionery company founded in 1911 |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5470 | The Perseverance rover collected rock samples in the Jezero Crater on Mars |
| 2 | DISTR distractor | 0.8515 | Mars Incorporated announced a global recall of certain Snickers and Milky Way products |
| 3 | DISTR distractor | 0.8589 | The Mars family maintains private ownership of the confectionery company founded in 1911 |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Robotic explorer' not 'rover', 'geological specimens' not 'rock samples', 'red planet' not 'Mars'. Multiple candy company-sense distractors.

---

### PARTIAL T1-06: Bank: financial institution vs riverbank

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The central bank raised the benchmark interest rate by 50 basis points this quarter |
| DISTR | Wildflowers grew abundantly along the river bank where we held last summer's picnic |
| DISTR | Erosion along the creek bank has worsened significantly after the recent flooding |
| DISTR | The steep bank of the canal made it difficult to access the water for irrigation |
| DISTR | Bank stabilization projects are scheduled to begin next quarter along the waterfront |

**Query:** What monetary policy adjustments were announced by the national financial authority?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.6035 | The central bank raised the benchmark interest rate by 50 basis points this quarter |
| 2 | DISTR distractor | 0.7863 | Bank stabilization projects are scheduled to begin next quarter along the waterfront |
| 3 | DISTR distractor | 0.7863 | Erosion along the creek bank has worsened significantly after the recent flooding |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.6035 | The central bank raised the benchmark interest rate by 50 basis points this quarter |
| 2 | DISTR distractor | 0.7863 | Bank stabilization projects are scheduled to begin next quarter along the waterfront |
| 3 | DISTR distractor | 0.8725 | The steep bank of the canal made it difficult to access the water for irrigation |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Financial authority' not 'bank', 'monetary policy adjustments' not 'interest rate'. Multiple riverbank-sense distractors, one with 'quarter' for temporal confusion.

---

### PARTIAL T1-07: Crane: construction equipment vs wading bird

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The construction crew deployed a 200-ton crane to position the steel framework into place |
| DISTR | A pair of sandhill cranes built their nest near the wetland preserve this spring |
| DISTR | Whooping crane populations have shown encouraging recovery in protected habitats |
| DISTR | The migratory crane species travels thousands of miles each year seeking suitable breeding grounds |

**Query:** What heavy lifting apparatus was used at the building site?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.6345 | The construction crew deployed a 200-ton crane to position the steel framework into place |
| 2 | DISTR distractor | 0.7859 | A pair of sandhill cranes built their nest near the wetland preserve this spring |
| 3 | DISTR distractor | 0.8448 | Whooping crane populations have shown encouraging recovery in protected habitats |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.6345 | The construction crew deployed a 200-ton crane to position the steel framework into place |
| 2 | DISTR distractor | 0.7859 | A pair of sandhill cranes built their nest near the wetland preserve this spring |
| 3 | DISTR distractor | 0.8448 | Whooping crane populations have shown encouraging recovery in protected habitats |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Heavy lifting apparatus' not 'crane', 'building site' not 'construction'. Multiple bird-sense distractors.

---

### PARTIAL T1-08: Spring: season vs mechanical part

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | Cherry blossoms reach peak bloom every spring along the Tidal Basin in Washington DC |
| DISTR | The garage door torsion spring snapped and needs immediate professional replacement |
| DISTR | Coil spring suspension systems provide better ride quality compared to leaf springs in modern vehicles |
| DISTR | The mattress lost support after the box spring wore out from years of use |

**Query:** When do the ornamental trees put on their annual flowering display in the US capital?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5850 | Cherry blossoms reach peak bloom every spring along the Tidal Basin in Washington DC |
| 2 | NOISE noise | 0.9245 | Photosynthesis converts carbon dioxide and water into glucose using sunlight as energy |
| 3 | DISTR distractor | 0.9612 | Coil spring suspension systems provide better ride quality compared to leaf springs in modern vehicles |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5850 | Cherry blossoms reach peak bloom every spring along the Tidal Basin in Washington DC |
| 2 | NOISE noise | 0.9245 | Photosynthesis converts carbon dioxide and water into glucose using sunlight as energy |
| 3 | DISTR distractor | 0.9612 | Coil spring suspension systems provide better ride quality compared to leaf springs in modern vehicles |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 1 | 1 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Ornamental trees', 'flowering display', 'US capital' — no 'cherry', 'spring', 'bloom', 'Washington'. Multiple mechanical part-sense distractors.

---

### PARTIAL T1-09: Pitch: investor presentation vs musical tone

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The startup founder delivered a compelling pitch to three venture capital firms last Thursday |
| DISTR | The first violinist struggled to maintain accurate pitch throughout the concerto's second movement |
| DISTR | Perfect pitch ability allows musicians to identify notes without a reference tone |
| DISTR | The choir director adjusted the pitch upward by a half step to suit the sopranos' range |

**Query:** How did the entrepreneur's fundraising presentation go with the investment groups?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5653 | The startup founder delivered a compelling pitch to three venture capital firms last Thursday |
| 2 | DISTR distractor | 0.8232 | The first violinist struggled to maintain accurate pitch throughout the concerto's second movement |
| 3 | DISTR distractor | 0.9346 | The choir director adjusted the pitch upward by a half step to suit the sopranos' range |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5653 | The startup founder delivered a compelling pitch to three venture capital firms last Thursday |
| 2 | DISTR distractor | 0.8232 | The first violinist struggled to maintain accurate pitch throughout the concerto's second movement |
| 3 | DISTR distractor | 0.9346 | The choir director adjusted the pitch upward by a half step to suit the sopranos' range |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Entrepreneur' not 'founder', 'fundraising presentation' not 'pitch', 'investment groups' not 'venture capital firms'. Multiple musical tone-sense distractors.

---

### PARTIAL T1-10: Cell: biology vs prison

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The research team identified a novel stem cell variant capable of regenerating damaged nerve tissue |
| DISTR | The inmate was transferred to an isolation cell following the altercation in the exercise yard |
| DISTR | Prison overcrowding resulted in two inmates sharing a single cell designed for one occupant |
| DISTR | The holding cell detention area was renovated to meet modern safety standards |

**Query:** What breakthrough was achieved in the laboratory's tissue repair studies?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5497 | The research team identified a novel stem cell variant capable of regenerating damaged nerve tissue |
| 2 | DISTR distractor | 0.7682 | The holding cell detention area was renovated to meet modern safety standards |
| 3 | DISTR distractor | 0.7682 | The inmate was transferred to an isolation cell following the altercation in the exercise yard |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5497 | The research team identified a novel stem cell variant capable of regenerating damaged nerve tissue |
| 2 | DISTR distractor | 0.7682 | The holding cell detention area was renovated to meet modern safety standards |
| 3 | DISTR distractor | 0.8948 | Prison overcrowding resulted in two inmates sharing a single cell designed for one occupant |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Laboratory' not 'research team', 'tissue repair studies' not 'stem cell' or 'regenerating nerve tissue'. Multiple prison-sense distractors.

---

### PARTIAL T1-11: The White House: administration vs building

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The White House announced sweeping new executive orders on climate and emissions policy |
| DISTR | The White House was originally built with Aquia Creek sandstone and first painted white in 1818 |
| DISTR | The White House underwent major renovations during the Truman administration to stabilize its structure |
| DISTR | White House tours are now available by advance reservation through congressional offices |

**Query:** What environmental regulations did the US presidential administration enact?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5217 | The White House announced sweeping new executive orders on climate and emissions policy |
| 2 | DISTR distractor | 0.7367 | The White House underwent major renovations during the Truman administration to stabilize its structure |
| 3 | DISTR distractor | 0.7660 | The White House was originally built with Aquia Creek sandstone and first painted white in 1818 |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5217 | The White House announced sweeping new executive orders on climate and emissions policy |
| 2 | DISTR distractor | 0.7367 | The White House underwent major renovations during the Truman administration to stabilize its structure |
| 3 | DISTR distractor | 0.7660 | The White House was originally built with Aquia Creek sandstone and first painted white in 1818 |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'US presidential administration' not 'White House', 'environmental regulations' not 'climate policy' or 'executive orders'. Multiple building-sense distractors, with 'administration' appearing in historical context.

---

### PARTIAL T1-12: Hollywood: film industry vs neighborhood

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | Hollywood studios are investing heavily in generative AI for visual effects pipelines |
| DISTR | Residential property values in the Hollywood neighborhood climbed 15% year over year |
| DISTR | The Hollywood Walk of Fame added twelve new stars honoring entertainment industry pioneers |
| DISTR | Traffic congestion in Hollywood reached record levels during the recent film festival |

**Query:** How is the American motion picture industry integrating new computational tools into post-production?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.4719 | Hollywood studios are investing heavily in generative AI for visual effects pipelines |
| 2 | DISTR distractor | 0.7982 | Traffic congestion in Hollywood reached record levels during the recent film festival |
| 3 | DISTR distractor | 0.7982 | Residential property values in the Hollywood neighborhood climbed 15% year over year |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.4719 | Hollywood studios are investing heavily in generative AI for visual effects pipelines |
| 2 | DISTR distractor | 0.7982 | Traffic congestion in Hollywood reached record levels during the recent film festival |
| 3 | DISTR distractor | 0.8038 | The Hollywood Walk of Fame added twelve new stars honoring entertainment industry pioneers |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Motion picture industry' not 'Hollywood', 'computational tools' not 'AI', 'post-production' not 'visual effects'. Distractors mix geographic location with entertainment references (Walk of Fame, festival).

---

### PARTIAL T1-13: Wall Street: financial sector vs subway station

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | Wall Street analysts downgraded the technology sector following disappointing quarterly earnings |
| DISTR | The Wall Street subway station is undergoing extensive renovation for ADA accessibility |
| DISTR | Wall Street's historic cobblestone pavement will be preserved during upcoming infrastructure upgrades |
| DISTR | Tourist foot traffic on Wall Street increased significantly following the opening of new museums |

**Query:** What did the equity research community say about the recent performance of tech companies?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5141 | Wall Street analysts downgraded the technology sector following disappointing quarterly earnings |
| 2 | DISTR distractor | 0.8646 | Wall Street's historic cobblestone pavement will be preserved during upcoming infrastructure upgrades |
| 3 | DISTR distractor | 0.8665 | The Wall Street subway station is undergoing extensive renovation for ADA accessibility |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5141 | Wall Street analysts downgraded the technology sector following disappointing quarterly earnings |
| 2 | DISTR distractor | 0.8646 | Wall Street's historic cobblestone pavement will be preserved during upcoming infrastructure upgrades |
| 3 | DISTR distractor | 0.8665 | The Wall Street subway station is undergoing extensive renovation for ADA accessibility |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Equity research community' not 'analysts', 'tech companies' not 'technology sector'. Multiple geographic location distractors.

---

### PARTIAL T1-14: Silicon Valley: tech ecosystem vs geographic valley

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | Silicon Valley startups collectively raised $48 billion in venture funding during Q3 |
| DISTR | The Santa Clara Valley was once the largest fruit-producing region on the West Coast |
| DISTR | Valley floor irrigation systems transformed agricultural production in the Santa Clara region |
| DISTR | The valley's temperate climate supported diverse crops before suburban development |

**Query:** How much private equity flowed into the Bay Area technology entrepreneurship scene last quarter?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.4856 | Silicon Valley startups collectively raised $48 billion in venture funding during Q3 |
| 2 | DISTR distractor | 0.8211 | Valley floor irrigation systems transformed agricultural production in the Santa Clara region |
| 3 | DISTR distractor | 0.8226 | The Santa Clara Valley was once the largest fruit-producing region on the West Coast |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.4856 | Silicon Valley startups collectively raised $48 billion in venture funding during Q3 |
| 2 | DISTR distractor | 0.8211 | Valley floor irrigation systems transformed agricultural production in the Santa Clara region |
| 3 | DISTR distractor | 0.8226 | The Santa Clara Valley was once the largest fruit-producing region on the West Coast |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Private equity' not 'venture funding', 'Bay Area technology entrepreneurship scene' not 'Silicon Valley startups'. Multiple geographic valley/agriculture-sense distractors.

---

### PARTIAL T1-15: Crown: sovereign authority vs jeweled headpiece

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The Crown issued a formal pardon for all individuals convicted under the repealed statute |
| DISTR | The jewel-encrusted crown on display at the Tower of London weighs nearly five pounds |
| DISTR | The coronation crown was specially fitted with velvet lining for the upcoming ceremony |
| DISTR | Replicas of the crown jewels are sold at the museum gift shop for tourists |

**Query:** What clemency action did the British sovereign authority grant regarding the outdated law?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5699 | The Crown issued a formal pardon for all individuals convicted under the repealed statute |
| 2 | DISTR distractor | 0.8970 | The jewel-encrusted crown on display at the Tower of London weighs nearly five pounds |
| 3 | DISTR distractor | 0.9144 | The coronation crown was specially fitted with velvet lining for the upcoming ceremony |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5699 | The Crown issued a formal pardon for all individuals convicted under the repealed statute |
| 2 | DISTR distractor | 0.8970 | The jewel-encrusted crown on display at the Tower of London weighs nearly five pounds |
| 3 | DISTR distractor | 0.9144 | The coronation crown was specially fitted with velvet lining for the upcoming ceremony |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Sovereign authority' not 'Crown', 'clemency' not 'pardon', 'outdated law' not 'repealed statute'. Multiple jeweled headpiece-sense distractors.

---

## Tier 2: Temporal

### PARTIAL T2-01: Tomorrow morning -> today (next-day query)

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| TARGET | 202603100800 | Team sync rescheduled to tomorrow morning at nine |
| DISTR | 202603100800 | Team sync ran long last week and we skipped the retrospective |
| DISTR | 202603100800 | Team sync yesterday covered the sprint planning and capacity allocation |
| DISTR | 202603100800 | Team sync next week will include the new Q2 roadmap review |
| DISTR | 202603100800 | Team sync was cancelled this morning due to the all-hands meeting conflict |

**Query:** Is there a team sync happening today?

**Query issued at:** 202603110900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.3726 | Team sync was cancelled this morning due to the all-hands meeting conflict |
| 2 | TARGET target | 0.3726 | Team sync rescheduled to tomorrow morning at nine |
| 3 | DISTR distractor | 0.4458 | Team sync ran long last week and we skipped the retrospective |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.3726 | Team sync was cancelled this morning due to the all-hands meeting conflict |
| 2 | DISTR distractor | 0.4458 | Team sync ran long last week and we skipped the retrospective |
| 3 | DISTR distractor | 0.4561 | Team sync yesterday covered the sprint planning and capacity allocation |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 1.00 |
| Precision | 0.00 | 0.33 |
| MRR | 0.00 | 0.50 |
| Distractors | 3 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> All memories mention 'team sync'. Distinguishing factor is ONLY temporal: 'tomorrow' from Mar 10 = Mar 11 = 'today' from query perspective. Distractors span past (last week, yesterday, this morning) and future (next week).

---

### PARTIAL T2-02: Next Wednesday -> this week (query one week later)

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| TARGET | 202603030900 | Client walkthrough of the prototype pushed to next Wednesday afternoon |
| DISTR | 202603030900 | Client walkthrough in February covered the wireframes and got positive feedback |
| DISTR | 202603030900 | Client walkthrough last Wednesday went well and they approved moving to the next phase |
| DISTR | 202603030900 | Client walkthrough scheduled for late March will include the full feature set demonstration |

**Query:** Are there any client sessions this week?

**Query issued at:** 202603100900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5644 | Client walkthrough last Wednesday went well and they approved moving to the next phase |
| 2 | TARGET target | 0.5888 | Client walkthrough of the prototype pushed to next Wednesday afternoon |
| 3 | DISTR distractor | 0.6314 | Client walkthrough scheduled for late March will include the full feature set demonstration |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5644 | Client walkthrough last Wednesday went well and they approved moving to the next phase |
| 2 | TARGET target | 0.5888 | Client walkthrough of the prototype pushed to next Wednesday afternoon |
| 3 | DISTR distractor | 0.6314 | Client walkthrough scheduled for late March will include the full feature set demonstration |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 0.50 | 0.50 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Next Wednesday' from Mar 3 = Mar 10 = 'this week' from query. All memories mention 'client walkthrough'. Distractors reference different times (February, last Wednesday, late March).

---

### PARTIAL T2-03: Tonight -> last night (next-morning query)

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| TARGET | 202603101800 | Ops team taking the authentication services offline tonight from eleven to three |
| DISTR | 202603101800 | Authentication services had a brief hiccup two weeks ago but self-recovered |
| DISTR | 202603101800 | Authentication services will undergo scheduled maintenance next weekend for security patches |
| DISTR | 202603101800 | Authentication services experienced elevated latency three days ago during peak traffic |

**Query:** Were any of our services intentionally brought down last night?

**Query issued at:** 202603110800

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.6817 | Authentication services had a brief hiccup two weeks ago but self-recovered |
| 2 | TARGET target | 0.6817 | Ops team taking the authentication services offline tonight from eleven to three |
| 3 | DISTR distractor | 0.7132 | Authentication services experienced elevated latency three days ago during peak traffic |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.6817 | Authentication services had a brief hiccup two weeks ago but self-recovered |
| 2 | DISTR distractor | 0.7132 | Authentication services experienced elevated latency three days ago during peak traffic |
| 3 | DISTR distractor | 0.7304 | Authentication services will undergo scheduled maintenance next weekend for security patches |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 1.00 |
| Precision | 0.00 | 0.33 |
| MRR | 0.00 | 0.50 |
| Distractors | 3 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Tonight' from Mar 10 evening = 'last night' from Mar 11 morning. All mention 'authentication services'. Distractors span past incidents (two weeks ago, three days ago) and future maintenance (next weekend).

---

### PARTIAL T2-04: In two days -> today (query two days later)

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| TARGET | 202603080900 | Board review session happens in two days at 2pm sharp |
| DISTR | 202603080900 | Board review from last month concluded with full budget approval |
| DISTR | 202603080900 | Board review scheduled for next Tuesday will cover the annual strategy proposals |
| DISTR | 202603080900 | Board review yesterday focused exclusively on risk management and compliance issues |

**Query:** Any executive meetings on the calendar for today?

**Query issued at:** 202603100900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.6750 | Board review scheduled for next Tuesday will cover the annual strategy proposals |
| 2 | TARGET target | 0.7559 | Board review session happens in two days at 2pm sharp |
| 3 | DISTR distractor | 0.7724 | Board review from last month concluded with full budget approval |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.6750 | Board review scheduled for next Tuesday will cover the annual strategy proposals |
| 2 | TARGET target | 0.7559 | Board review session happens in two days at 2pm sharp |
| 3 | DISTR distractor | 0.7724 | Board review from last month concluded with full budget approval |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 0.50 | 0.50 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'In two days' from Mar 8 = Mar 10 = 'today' from query. All mention 'board review'. Distractors: past (last month, yesterday), future (next Tuesday).

---

### PARTIAL T2-05: In five days -> tomorrow (query four days later)

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| TARGET | 202603050900 | Conference registration window closes in five days |
| DISTR | 202603050900 | Conference registration opened with early bird pricing three weeks ago |
| DISTR | 202603050900 | Conference registration fees increase after the first two hundred attendees sign up |
| DISTR | 202603050900 | Conference registration is expected to sell out well before the event date in April |

**Query:** Is there a signup cutoff approaching tomorrow?

**Query issued at:** 202603090900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.7114 | Conference registration fees increase after the first two hundred attendees sign up |
| 2 | TARGET target | 0.7114 | Conference registration window closes in five days |
| 3 | DISTR distractor | 0.7165 | Conference registration is expected to sell out well before the event date in April |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.7114 | Conference registration fees increase after the first two hundred attendees sign up |
| 2 | DISTR distractor | 0.7165 | Conference registration is expected to sell out well before the event date in April |
| 3 | DISTR distractor | 0.7176 | Conference registration opened with early bird pricing three weeks ago |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 1.00 |
| Precision | 0.00 | 0.33 |
| MRR | 0.00 | 0.50 |
| Distractors | 3 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'In five days' from Mar 5 = Mar 10 = 'tomorrow' from Mar 9. All about 'conference registration'. Distractors: past opening, capacity-based (not time-based), future prediction.

---

### PARTIAL T2-06: Framework migration: React -> Svelte

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| DISTR | 202601150900 | Project Falcon uses React for its frontend framework |
| DISTR | 202602010900 | Project Falcon frontend framework evaluation considered Vue and Svelte as React alternatives |
| DISTR | 202602150900 | Project Falcon began the experimental Svelte migration branch for performance testing |
| TARGET | 202603010900 | Project Falcon frontend was completely rewritten using Svelte last month |

**Query:** What UI framework does Project Falcon currently rely on?

**Query issued at:** 202603100900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.3638 | Project Falcon uses React for its frontend framework |
| 2 | TARGET target | 0.4164 | Project Falcon frontend was completely rewritten using Svelte last month |
| 3 | DISTR distractor | 0.4164 | Project Falcon began the experimental Svelte migration branch for performance testing |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.3638 | Project Falcon uses React for its frontend framework |
| 2 | TARGET target | 0.4164 | Project Falcon frontend was completely rewritten using Svelte last month |
| 3 | DISTR distractor | 0.4365 | Project Falcon frontend framework evaluation considered Vue and Svelte as React alternatives |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 0.50 | 0.50 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> All memories about Project Falcon's frontend evolution. Timeline: Jan (React) -> Feb (evaluation) -> Feb (experiment) -> Mar (full Svelte migration). System must select the latest state.

---

### PARTIAL T2-07: Personnel handoff: Sarah -> Marcus

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| DISTR | 202602010900 | Sarah is the point of contact for all vendor negotiations |
| DISTR | 202602200900 | Sarah and Marcus are collaborating on the vendor management transition plan |
| TARGET | 202603050900 | Marcus has taken over all supplier relationship responsibilities from Sarah |
| DISTR | 202603050900 | Sarah will continue advising on vendor strategy through the end of the quarter |

**Query:** Who handles our external procurement partnerships right now?

**Query issued at:** 202603100900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.4948 | Marcus has taken over all supplier relationship responsibilities from Sarah |
| 2 | DISTR distractor | 0.4948 | Sarah is the point of contact for all vendor negotiations |
| 3 | DISTR distractor | 0.5600 | Sarah and Marcus are collaborating on the vendor management transition plan |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.4948 | Marcus has taken over all supplier relationship responsibilities from Sarah |
| 2 | DISTR distractor | 0.5600 | Sarah and Marcus are collaborating on the vendor management transition plan |
| 3 | DISTR distractor | 0.5611 | Sarah will continue advising on vendor strategy through the end of the quarter |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Vendor negotiations' vs 'supplier relationships' vs 'procurement partnerships' — all synonyms. Timeline shows handoff: Sarah (Feb) -> transition (late Feb) -> Marcus owns (Mar 5). Distractor_3 has same timestamp as target but mentions advisory role vs ownership.

---

### FAIL T2-08: Meeting room closure override

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| DISTR | 202602100900 | Weekly all-hands meeting is held in Conference Room B on the third floor |
| DISTR | 202602200900 | Conference Room B was upgraded with new video conferencing equipment last month |
| TARGET | 202603010900 | All third floor meeting rooms are closed for renovation through the end of April |
| DISTR | 202603010900 | The all-hands meeting agenda typically covers quarterly goals and team updates |

**Query:** Where should I go for the all-hands gathering this week?

**Query issued at:** 202603100900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4943 | Weekly all-hands meeting is held in Conference Room B on the third floor |
| 2 | DISTR distractor | 0.6470 | The all-hands meeting agenda typically covers quarterly goals and team updates |
| 3 | DISTR distractor | 0.6470 | Conference Room B was upgraded with new video conferencing equipment last month |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4943 | Weekly all-hands meeting is held in Conference Room B on the third floor |
| 2 | DISTR distractor | 0.6470 | The all-hands meeting agenda typically covers quarterly goals and team updates |
| 3 | TARGET target | 0.6857 | All third floor meeting rooms are closed for renovation through the end of April |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 0.00 |
| Precision | 0.33 | 0.00 |
| MRR | 0.33 | 0.00 |
| Distractors | 2 | 3 |
| **Verdict** | **FAIL** | **FAIL** |

> Multiple memories about Conference Room B and all-hands meetings. Latest memory (Mar 1) invalidates the location. Distractors include equipment upgrade and agenda content (same timestamp as target but irrelevant).

---

### PARTIAL T2-09: CI/CD migration: Jenkins -> GitHub Actions

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| DISTR | 202601200900 | Continuous integration builds run on the Jenkins server in the datacenter |
| DISTR | 202602010900 | Jenkins pipeline configuration requires Groovy scripting for custom build steps |
| DISTR | 202602150900 | The team evaluated GitHub Actions and CircleCI as potential Jenkins replacements |
| TARGET | 202603030900 | All CI/CD pipelines migrated to GitHub Actions effective last week |

**Query:** What automation platform handles our build and deployment workflows now?

**Query issued at:** 202603100900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5527 | Continuous integration builds run on the Jenkins server in the datacenter |
| 2 | TARGET target | 0.6064 | All CI/CD pipelines migrated to GitHub Actions effective last week |
| 3 | DISTR distractor | 0.6524 | The team evaluated GitHub Actions and CircleCI as potential Jenkins replacements |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5527 | Continuous integration builds run on the Jenkins server in the datacenter |
| 2 | TARGET target | 0.6064 | All CI/CD pipelines migrated to GitHub Actions effective last week |
| 3 | DISTR distractor | 0.6524 | The team evaluated GitHub Actions and CircleCI as potential Jenkins replacements |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 0.50 | 0.50 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Automation platform' not 'CI/CD'. Timeline: Jan (Jenkins active) -> Feb (Jenkins details) -> Feb (evaluation phase) -> Mar (GitHub Actions migration complete).

---

### PARTIAL T2-10: Python deprecation: 3.8 -> 3.11

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| DISTR | 202511100900 | All production codebases must be compatible with Python 3.8 or higher |
| DISTR | 202601150900 | Python 3.8 remains widely used despite the release of newer versions |
| TARGET | 202603010900 | Python 3.8 and 3.9 support was officially dropped from our projects as of February |
| DISTR | 202603010900 | Python 3.11 offers performance improvements over earlier interpreter releases |

**Query:** What interpreter version do our codebases need to support right now?

**Query issued at:** 202603100900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5019 | Python 3.11 offers performance improvements over earlier interpreter releases |
| 2 | TARGET target | 0.5019 | Python 3.8 and 3.9 support was officially dropped from our projects as of February |
| 3 | DISTR distractor | 0.5377 | All production codebases must be compatible with Python 3.8 or higher |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5019 | Python 3.11 offers performance improvements over earlier interpreter releases |
| 2 | DISTR distractor | 0.5377 | All production codebases must be compatible with Python 3.8 or higher |
| 3 | DISTR distractor | 0.5757 | Python 3.8 remains widely used despite the release of newer versions |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 1.00 |
| Precision | 0.00 | 0.33 |
| MRR | 0.00 | 0.50 |
| Distractors | 3 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Interpreter version' not 'Python version'. Timeline: Nov 2025 (3.8+ required) -> Jan (general 3.8 usage) -> Feb (3.8/3.9 dropped). Distractor_3 same timestamp but discusses benefits not requirements.

---

### PARTIAL T2-11: Prerequisite chain: audit before launch date

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| TARGET | 202603050900 | The security audit must be finalized before the product goes live |
| TARGET | 202603050900 | Product go-live date locked in for March 20th |
| DISTR | 202603050900 | The security audit for last quarter's release was completed on schedule in February |
| DISTR | 202603050900 | Product marketing materials need final approval before the April campaign launch |

**Query:** What tasks need to wrap up before March 20th?

**Query issued at:** 202603100900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.6718 | Product go-live date locked in for March 20th |
| 2 | TARGET target | 0.6718 | The security audit must be finalized before the product goes live |
| 3 | DISTR distractor | 0.7588 | Product marketing materials need final approval before the April campaign launch |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.6718 | Product go-live date locked in for March 20th |
| 2 | DISTR distractor | 0.7588 | Product marketing materials need final approval before the April campaign launch |
| 3 | DISTR distractor | 0.7917 | The security audit for last quarter's release was completed on schedule in February |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.50 | 1.00 |
| Precision | 0.33 | 0.67 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 1 |
| **Verdict** | **FAIL** | **PARTIAL** |

> Requires linking 'before product goes live' + 'go-live = March 20' to answer 'security audit before March 20'. Distractors: past audit (February), different deadline (April).

---

### PARTIAL T2-12: Quarterly cycle inference

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| TARGET | 202603010900 | Financial statements are always filed on the last business day of each fiscal quarter |
| DISTR | 202603010900 | Financial statements for the previous quarter were submitted ahead of the deadline |
| DISTR | 202603010900 | Annual financial reporting occurs at the end of the fiscal year in December |
| DISTR | 202603010900 | Monthly financial summaries are distributed to department heads by the fifth business day |

**Query:** When is the next regulatory filing obligation?

**Query issued at:** 202603150900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.6288 | Financial statements for the previous quarter were submitted ahead of the deadline |
| 2 | TARGET target | 0.6608 | Financial statements are always filed on the last business day of each fiscal quarter |
| 3 | DISTR distractor | 0.7283 | Annual financial reporting occurs at the end of the fiscal year in December |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.6288 | Financial statements for the previous quarter were submitted ahead of the deadline |
| 2 | TARGET target | 0.6608 | Financial statements are always filed on the last business day of each fiscal quarter |
| 3 | DISTR distractor | 0.7283 | Annual financial reporting occurs at the end of the fiscal year in December |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 0.50 | 0.50 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> Requires knowing: queried mid-March -> Q1 ends March 31 -> last business day of Q1 is the answer. Distractors: past quarter, annual cycle, monthly cycle.

---

### PARTIAL T2-13: Biannual cycle inference

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| TARGET | 202603010900 | Employee evaluations take place biannually in June and December without exception |
| DISTR | 202603010900 | Employee evaluation results from December showed improved satisfaction scores across all departments |
| DISTR | 202603010900 | New employee probationary reviews occur quarterly during the first year of employment |
| DISTR | 202603010900 | Annual compensation adjustments are typically announced in March following budget approval |

**Query:** When is the next round of staff performance assessments?

**Query issued at:** 202603150900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5938 | Employee evaluations take place biannually in June and December without exception |
| 2 | DISTR distractor | 0.6054 | New employee probationary reviews occur quarterly during the first year of employment |
| 3 | DISTR distractor | 0.6272 | Employee evaluation results from December showed improved satisfaction scores across all departments |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5938 | Employee evaluations take place biannually in June and December without exception |
| 2 | DISTR distractor | 0.6054 | New employee probationary reviews occur quarterly during the first year of employment |
| 3 | DISTR distractor | 0.6272 | Employee evaluation results from December showed improved satisfaction scores across all departments |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Staff performance assessments' not 'employee evaluations'. Requires: March query -> next is June. Distractors: past results (December), quarterly cycle (different schedule), annual cycle (compensation not evaluation).

---

### FAIL T2-14: Duration-from-date calculation

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| TARGET | 202603010900 | The commercial lease expires exactly eighteen months from the signing date of September 2024 |
| DISTR | 202603010900 | The previous office lease was signed for a five-year term in 2019 |
| DISTR | 202603010900 | Commercial lease negotiations typically begin six months before the current agreement ends |
| DISTR | 202603010900 | Office space requirements are reviewed annually during strategic planning in January |

**Query:** Do we need to find alternative office space soon?

**Query issued at:** 202603100900

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4631 | Office space requirements are reviewed annually during strategic planning in January |
| 2 | DISTR distractor | 0.4631 | Commercial lease negotiations typically begin six months before the current agreement ends |
| 3 | DISTR distractor | 0.6898 | The previous office lease was signed for a five-year term in 2019 |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4631 | Office space requirements are reviewed annually during strategic planning in January |
| 2 | DISTR distractor | 0.6898 | The previous office lease was signed for a five-year term in 2019 |
| 3 | TARGET target | 0.8457 | The commercial lease expires exactly eighteen months from the signing date of September 2024 |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 0.00 |
| Precision | 0.33 | 0.00 |
| MRR | 0.33 | 0.00 |
| Distractors | 2 | 3 |
| **Verdict** | **FAIL** | **FAIL** |

> Sep 2024 + 18 months = March 2026 = NOW. Distractors: past lease (2019), general advice (6 months before), annual review cycle (January).

---

### PARTIAL T2-15: Multi-memory temporal chain (recurring + last-run)

**Case memories** (+ 20 shared noise memories above):

| Role | Timestamp | Content |
|------|-----------|---------|
| TARGET | 202603010900 | Automated backups execute on a 72-hour cycle starting from midnight each Sunday |
| TARGET | 202603041200 | The latest backup run completed without errors on Wednesday at midnight |
| DISTR | 202603010900 | Database backups run nightly at 2am with a 24-hour retention policy |
| DISTR | 202603041200 | The backup system was upgraded last month to improve storage efficiency |

**Query:** When will the storage snapshots run again?

**Query issued at:** 202603051400

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5245 | The backup system was upgraded last month to improve storage efficiency |
| 2 | DISTR distractor | 0.5675 | Database backups run nightly at 2am with a 24-hour retention policy |
| 3 | TARGET target | 0.5675 | Automated backups execute on a 72-hour cycle starting from midnight each Sunday |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5245 | The backup system was upgraded last month to improve storage efficiency |
| 2 | DISTR distractor | 0.5675 | Database backups run nightly at 2am with a 24-hour retention policy |
| 3 | TARGET target | 0.6087 | The latest backup run completed without errors on Wednesday at midnight |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.50 | 0.50 |
| Precision | 0.33 | 0.33 |
| MRR | 0.33 | 0.33 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Storage snapshots' not 'backups'. Requires: last ran Wed midnight + 72h = Sat midnight. Distractors: different backup schedule (nightly 24h), upgrade info (not schedule).

---

## Tier 3: Multi-hop

### PARTIAL T3-01: Person -> division -> project

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | Elena was promoted to lead the infrastructure division last quarter |
| TARGET | The infrastructure division owns the cloud migration initiative end-to-end |
| DISTR | Elena previously managed the platform engineering team before her recent promotion |
| DISTR | The cloud migration initiative was originally proposed by the CTO in the annual strategy meeting |
| DISTR | The infrastructure division recently completed the datacenter consolidation project ahead of schedule |
| DISTR | The infrastructure division manages a team of forty engineers across platform, networking, and security |
| DISTR | Elena presented the division quarterly roadmap to senior leadership last week |
| DISTR | Cloud migration initiatives typically involve renegotiating vendor contracts and retraining staff |

**Query:** Who is accountable for the shift to cloud services?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4642 | Cloud migration initiatives typically involve renegotiating vendor contracts and retraining staff |
| 2 | DISTR distractor | 0.5219 | The cloud migration initiative was originally proposed by the CTO in the annual strategy meeting |
| 3 | TARGET target | 0.5220 | The infrastructure division owns the cloud migration initiative end-to-end |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4642 | Cloud migration initiatives typically involve renegotiating vendor contracts and retraining staff |
| 2 | DISTR distractor | 0.5219 | The cloud migration initiative was originally proposed by the CTO in the annual strategy meeting |
| 3 | TARGET target | 0.5220 | The infrastructure division owns the cloud migration initiative end-to-end |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.50 | 0.50 |
| Precision | 0.33 | 0.33 |
| MRR | 0.33 | 0.33 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Accountable' not 'lead/owns', 'shift to cloud services' not 'cloud migration initiative'. Requires: Elena -> infra division -> cloud migration. Distractors break the chain at different points: Elena's past role, cloud initiative origin, infra's other projects.

---

### PARTIAL T3-02: Factory halt -> supply dependency -> delivery delay

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The Shenzhen facility halted assembly lines due to a critical component shortage |
| TARGET | All second-quarter product shipments depend entirely on output from the Shenzhen facility |
| DISTR | The Shenzhen facility achieved record production efficiency last quarter with zero defects |
| DISTR | First-quarter customer deliveries exceeded projections by fifteen percent |
| DISTR | Component suppliers in Vietnam are expanding capacity to meet growing demand |
| DISTR | The Shenzhen facility supplies components to six product lines across three regional markets |
| DISTR | Q2 delivery commitments were confirmed with customers three months in advance |
| DISTR | Component shortages in the semiconductor industry have impacted manufacturers globally this year |

**Query:** Why might our Q2 customer deliveries fall behind schedule?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4097 | Q2 delivery commitments were confirmed with customers three months in advance |
| 2 | TARGET target | 0.4097 | All second-quarter product shipments depend entirely on output from the Shenzhen facility |
| 3 | DISTR distractor | 0.4097 | The Shenzhen facility supplies components to six product lines across three regional markets |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4097 | Q2 delivery commitments were confirmed with customers three months in advance |
| 2 | DISTR distractor | 0.4567 | First-quarter customer deliveries exceeded projections by fifteen percent |
| 3 | DISTR distractor | 0.6455 | Component shortages in the semiconductor industry have impacted manufacturers globally this year |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 0.50 |
| Precision | 0.00 | 0.33 |
| MRR | 0.00 | 0.50 |
| Distractors | 3 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Customer deliveries fall behind schedule' not 'shipments' or 'halted'. Requires chaining: shortage -> halt -> dependency -> delay. Distractors: past success (last quarter), different quarter (Q1), different supplier (Vietnam not Shenzhen).

---

### PARTIAL T3-03: Policy -> affected group -> individual

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | New attendance policy mandates all contract workers be physically present three days per week |
| TARGET | David joined the organization last month as a contract UX researcher |
| DISTR | Full-time employees are required to work from the office four days per week under the new policy |
| DISTR | David previously worked remotely at a fully distributed startup for two years |
| DISTR | The UX research team typically collaborates in person during user testing sessions |
| DISTR | Contract workers at the company are managed through an external staffing agency |
| DISTR | David's UX research role involves conducting user interviews and synthesizing findings for product teams |
| DISTR | The new attendance policy was communicated to all staff via email and posted on the internal HR portal |

**Query:** How often does David need to show up at the office?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5813 | David previously worked remotely at a fully distributed startup for two years |
| 2 | TARGET target | 0.6497 | David joined the organization last month as a contract UX researcher |
| 3 | TARGET target | 0.6523 | New attendance policy mandates all contract workers be physically present three days per week |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5813 | David previously worked remotely at a fully distributed startup for two years |
| 2 | TARGET target | 0.6497 | David joined the organization last month as a contract UX researcher |
| 3 | TARGET target | 0.6523 | New attendance policy mandates all contract workers be physically present three days per week |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.67 | 0.67 |
| MRR | 0.50 | 0.50 |
| Distractors | 1 | 1 |
| **Verdict** | **FAIL** | **PARTIAL** |

> Requires: David = contract worker -> contract worker policy = 3 days. Distractors: wrong policy group (full-time=4 days), David's past (remote work), team norms (not policy).

---

### PARTIAL T3-04: VP -> reports to CRO -> CRO identity

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The VP of Sales reports directly to the Chief Revenue Officer |
| TARGET | Karen was appointed as the new Chief Revenue Officer in January |
| DISTR | The VP of Sales previously led the regional sales team in the Northeast territory |
| DISTR | Karen started her career in sales operations before moving into executive leadership |
| DISTR | The Chief Marketing Officer and Chief Revenue Officer collaborate closely on go-to-market strategy |
| DISTR | Karen oversees a revenue organization of over two hundred sales and customer success professionals |
| DISTR | The Chief Revenue Officer role was created to unify sales, marketing, and customer success under one leader |
| DISTR | The VP of Sales exceeded annual quota by twenty-two percent in the previous fiscal year |

**Query:** Who is the VP of Sales' direct supervisor?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.4443 | The VP of Sales reports directly to the Chief Revenue Officer |
| 2 | DISTR distractor | 0.4854 | The VP of Sales previously led the regional sales team in the Northeast territory |
| 3 | TARGET target | 0.4854 | Karen was appointed as the new Chief Revenue Officer in January |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.4443 | The VP of Sales reports directly to the Chief Revenue Officer |
| 2 | DISTR distractor | 0.4854 | The VP of Sales previously led the regional sales team in the Northeast territory |
| 3 | DISTR distractor | 0.5495 | The Chief Revenue Officer role was created to unify sales, marketing, and customer success under one leader |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.50 | 1.00 |
| Precision | 0.33 | 0.67 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 1 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Direct supervisor' not 'reports to'. Requires: VP Sales -> CRO -> Karen. Distractors: VP's past role, Karen's past role, CRO's peer relationships.

---

### FAIL T3-05: Budget owner -> team -> headcount freeze

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The marketing department's annual spend is controlled by the CFO's office |
| TARGET | The CFO's office has frozen all new hiring requisitions until further notice |
| DISTR | The marketing department is actively recruiting for contractors to support the product launch campaign |
| DISTR | Marketing headcount grew by twelve percent last fiscal year to support expansion goals |
| DISTR | The engineering department received approval for three additional hires in specialized roles |
| DISTR | The CFO's office oversees procurement, financial planning, and expense management across all departments |
| DISTR | The marketing department's current headcount stands at thirty-two full-time employees |
| DISTR | New hiring across the company requires CFO approval for all roles above a certain salary threshold |

**Query:** Can the marketing group bring on additional staff right now?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.6112 | The marketing department's current headcount stands at thirty-two full-time employees |
| 2 | DISTR distractor | 0.6112 | The engineering department received approval for three additional hires in specialized roles |
| 3 | DISTR distractor | 0.6180 | The marketing department is actively recruiting for contractors to support the product launch campaign |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.6112 | The marketing department's current headcount stands at thirty-two full-time employees |
| 2 | DISTR distractor | 0.6180 | The marketing department is actively recruiting for contractors to support the product launch campaign |
| 3 | DISTR distractor | 0.6838 | Marketing headcount grew by twelve percent last fiscal year to support expansion goals |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 0.00 |
| Precision | 0.00 | 0.00 |
| MRR | 0.00 | 0.00 |
| Distractors | 3 | 3 |
| **Verdict** | **FAIL** | **FAIL** |

> 'Bring on additional staff' not 'hiring requisitions'. Requires: marketing -> CFO controls budget -> CFO froze hiring -> no. Distractors: contractor exception, past growth, different department approval.

---

### PARTIAL T3-06: Revenue beat expectations (full vocabulary swap)

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | Quarterly revenue exceeded Wall Street analyst consensus by a significant margin |
| DISTR | Quarterly expenses came in slightly below the finance team's initial budget projections |
| DISTR | Annual revenue growth has remained steady at approximately twelve percent year over year |
| DISTR | Market analysts anticipate continued strong performance in the upcoming fiscal quarter |
| DISTR | The finance team issued a press release highlighting key growth drivers after the earnings announcement |
| DISTR | Analyst consensus for next quarter has been revised upward following the strong results |
| DISTR | Revenue outperformance was driven primarily by the enterprise segment exceeding its quarterly target |

**Query:** Did the company's three-month income surpass what the financial forecasters predicted?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5816 | Quarterly revenue exceeded Wall Street analyst consensus by a significant margin |
| 2 | DISTR distractor | 0.5922 | The finance team issued a press release highlighting key growth drivers after the earnings announcement |
| 3 | DISTR distractor | 0.5922 | Annual revenue growth has remained steady at approximately twelve percent year over year |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5816 | Quarterly revenue exceeded Wall Street analyst consensus by a significant margin |
| 2 | DISTR distractor | 0.5922 | The finance team issued a press release highlighting key growth drivers after the earnings announcement |
| 3 | DISTR distractor | 0.6278 | Market analysts anticipate continued strong performance in the upcoming fiscal quarter |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> Every content word is swapped: 'quarterly'->'three-month', 'revenue'->'income', 'exceeded'->'surpass', 'analysts'->'forecasters', 'consensus'->'predicted'. Distractors: expenses vs revenue, annual vs quarterly, future predictions vs past results.

---

### PARTIAL T3-07: CTO advocates microservices (full vocabulary swap)

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The CTO advocated for adopting a microservices architecture during the annual planning session |
| DISTR | The VP of Engineering proposed maintaining the existing monolithic application for stability reasons |
| DISTR | Microservices migration discussions have been ongoing for several months across multiple teams |
| DISTR | The annual planning session covered topics including cloud migration and API strategy |
| DISTR | The CTO outlined a three-year technology modernization roadmap at the annual planning session |
| DISTR | Microservices architecture has been adopted by several peer companies in the industry |
| DISTR | The VP of Engineering and CTO jointly presented the technical strategy to the board |

**Query:** Who championed splitting the monolith into smaller independent modules at the yearly strategy offsite?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.8391 | The VP of Engineering proposed maintaining the existing monolithic application for stability reasons |
| 2 | TARGET target | 0.8391 | The CTO advocated for adopting a microservices architecture during the annual planning session |
| 3 | DISTR distractor | 0.8575 | The annual planning session covered topics including cloud migration and API strategy |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.8391 | The VP of Engineering proposed maintaining the existing monolithic application for stability reasons |
| 2 | DISTR distractor | 0.8575 | The annual planning session covered topics including cloud migration and API strategy |
| 3 | DISTR distractor | 0.8689 | The CTO outlined a three-year technology modernization roadmap at the annual planning session |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 1.00 |
| Precision | 0.00 | 0.33 |
| MRR | 0.00 | 0.50 |
| Distractors | 3 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Championed' not 'advocated', 'splitting monolith into modules' not 'microservices architecture', 'yearly strategy offsite' not 'annual planning session'. Distractors: opposing view (VP), generic discussion (no advocate), different topics.

---

### FAIL T3-08: Customer churn after price change (full vocabulary swap)

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | Customer attrition climbed to eight percent following the latest pricing adjustment |
| DISTR | New subscriber acquisition increased by twelve percent during the promotional campaign period |
| DISTR | The pricing committee is reviewing additional fee structure modifications for next quarter |
| DISTR | Customer satisfaction scores remained stable despite concerns about competitive pricing pressure |
| DISTR | The pricing adjustment was the first increase in three years and averaged fifteen percent across all tiers |
| DISTR | Customer attrition rates above five percent typically trigger a review by customer success leadership |
| DISTR | The customer success team launched a retention campaign following early signals of increased cancellations |

**Query:** How many subscribers cancelled after we revised our fee structure?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5439 | The pricing committee is reviewing additional fee structure modifications for next quarter |
| 2 | DISTR distractor | 0.5439 | New subscriber acquisition increased by twelve percent during the promotional campaign period |
| 3 | DISTR distractor | 0.5472 | The customer success team launched a retention campaign following early signals of increased cancellations |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5439 | The pricing committee is reviewing additional fee structure modifications for next quarter |
| 2 | DISTR distractor | 0.5472 | The customer success team launched a retention campaign following early signals of increased cancellations |
| 3 | TARGET target | 0.6238 | Customer attrition climbed to eight percent following the latest pricing adjustment |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 0.00 |
| Precision | 0.33 | 0.00 |
| MRR | 0.33 | 0.00 |
| Distractors | 2 | 3 |
| **Verdict** | **FAIL** | **FAIL** |

> 'Subscribers cancelled' not 'customer attrition', 'revised fee structure' not 'pricing adjustment'. Even 'eight percent' vs 'how many' tests numeric comprehension. Distractors: acquisition vs attrition, future changes vs past results, satisfaction vs churn.

---

### PARTIAL T3-09: Board approves acquisition (full vocabulary swap)

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The board of directors unanimously greenlit the purchase of a Scandinavian fintech startup |
| DISTR | The executive team is conducting due diligence on several potential acquisition targets in Europe |
| DISTR | Board meetings in previous quarters focused on organic growth rather than strategic acquisitions |
| DISTR | The fintech sector in Scandinavia has attracted significant venture capital investment recently |
| DISTR | The Scandinavian fintech startup had processed over two billion euros in transactions in the previous year |
| DISTR | The acquisition is expected to close within ninety days pending regulatory approval |
| DISTR | Board approval required a supermajority vote under the company's acquisition governance policy |

**Query:** Did the governing body consent to acquiring the Nordic financial technology venture?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.3953 | The board of directors unanimously greenlit the purchase of a Scandinavian fintech startup |
| 2 | DISTR distractor | 0.4252 | The Scandinavian fintech startup had processed over two billion euros in transactions in the previous year |
| 3 | DISTR distractor | 0.4342 | The fintech sector in Scandinavia has attracted significant venture capital investment recently |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.3953 | The board of directors unanimously greenlit the purchase of a Scandinavian fintech startup |
| 2 | DISTR distractor | 0.4252 | The Scandinavian fintech startup had processed over two billion euros in transactions in the previous year |
| 3 | DISTR distractor | 0.4342 | The fintech sector in Scandinavia has attracted significant venture capital investment recently |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Governing body' not 'board of directors', 'consent' not 'greenlit', 'acquiring' not 'purchase', 'Nordic' not 'Scandinavian', 'venture' not 'startup'. Distractors: still evaluating (not approved), past strategy (organic not M&A), sector investment (not acquisition).

---

### PARTIAL T3-10: Engineer resignation (full vocabulary swap)

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The principal backend engineer submitted her resignation citing burnout and work-life imbalance |
| DISTR | Several junior developers expressed concerns about workload balance during the recent employee survey |
| DISTR | The backend engineering team is actively hiring to expand capacity for upcoming projects |
| DISTR | A senior frontend developer was promoted to principal engineer last quarter |
| DISTR | The principal backend engineer was the technical lead on the company payment processing infrastructure |
| DISTR | The backend team operates an on-call rotation that has been cited as a source of significant stress |
| DISTR | The company has been experiencing above-average attrition in its senior engineering ranks this year |

**Query:** Which senior server-side developer decided to leave because of exhaustion and personal life conflicts?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5346 | The principal backend engineer submitted her resignation citing burnout and work-life imbalance |
| 2 | DISTR distractor | 0.6379 | A senior frontend developer was promoted to principal engineer last quarter |
| 3 | DISTR distractor | 0.6985 | Several junior developers expressed concerns about workload balance during the recent employee survey |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | TARGET target | 0.5346 | The principal backend engineer submitted her resignation citing burnout and work-life imbalance |
| 2 | DISTR distractor | 0.6379 | A senior frontend developer was promoted to principal engineer last quarter |
| 3 | DISTR distractor | 0.6985 | Several junior developers expressed concerns about workload balance during the recent employee survey |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 1.00 |
| Precision | 0.33 | 0.33 |
| MRR | 1.00 | 1.00 |
| Distractors | 2 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Senior server-side developer' not 'principal backend engineer', 'decided to leave' not 'submitted resignation', 'exhaustion' not 'burnout'. Distractors: junior developers (not senior), hiring (not resignation), frontend promotion (not backend resignation).

---

### FAIL T3-11: Elon -> Tesla implicit link

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | Elon announced a ten percent workforce reduction across all operating units |
| TARGET | The Austin gigafactory will bear the brunt of the upcoming headcount changes |
| DISTR | Elon's recent social media posts sparked controversy about free speech policies |
| DISTR | The Austin facility recently expanded its solar panel installation capacity |
| DISTR | Electric vehicle sales in Texas increased by twenty percent compared to last year |
| DISTR | Tesla's workforce reductions are expected to affect manufacturing, software, and sales divisions |
| DISTR | Elon's companies collectively employ over one hundred thousand people worldwide |
| DISTR | The Austin gigafactory produces both the Model Y and the Cybertruck for North American markets |

**Query:** How will the electric vehicle manufacturer's layoffs affect production in Texas?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4790 | Electric vehicle sales in Texas increased by twenty percent compared to last year |
| 2 | DISTR distractor | 0.4790 | The Austin facility recently expanded its solar panel installation capacity |
| 3 | DISTR distractor | 0.4858 | Tesla's workforce reductions are expected to affect manufacturing, software, and sales divisions |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4790 | Electric vehicle sales in Texas increased by twenty percent compared to last year |
| 2 | DISTR distractor | 0.4858 | Tesla's workforce reductions are expected to affect manufacturing, software, and sales divisions |
| 3 | DISTR distractor | 0.5606 | The Austin gigafactory produces both the Model Y and the Cybertruck for North American markets |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 0.00 |
| Precision | 0.00 | 0.00 |
| MRR | 0.00 | 0.00 |
| Distractors | 3 | 3 |
| **Verdict** | **FAIL** | **FAIL** |

> Requires world knowledge: Elon = Elon Musk = Tesla, Austin gigafactory = Tesla + Texas, workforce reduction = layoffs. Distractors: different Elon topic (social media), Austin facility different context (solar), EV sales (not production/layoffs).

---

### PARTIAL T3-12: Federal Reserve -> central bank implicit link

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The Fed Chair testified about potential rate trajectory shifts at the Jackson Hole symposium |
| DISTR | The European Central Bank president discussed inflation concerns at the Frankfurt banking conference |
| DISTR | Jackson Hole Mountain Resort attracts thousands of skiers annually during winter season |
| DISTR | Federal Reserve regional governors meet quarterly to coordinate monetary policy implementation |
| DISTR | The Jackson Hole symposium is hosted annually by the Federal Reserve Bank of Kansas City in Wyoming |
| DISTR | The Fed Chair's remarks on interest rate policy are among the most market-moving communications in finance |
| DISTR | The Federal Reserve is the central banking system of the United States, established by Congress in 1913 |

**Query:** What did the head of America's central banking system discuss at the Wyoming economics gathering?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4992 | The Jackson Hole symposium is hosted annually by the Federal Reserve Bank of Kansas City in Wyoming |
| 2 | DISTR distractor | 0.4992 | Federal Reserve regional governors meet quarterly to coordinate monetary policy implementation |
| 3 | TARGET target | 0.4992 | The Fed Chair testified about potential rate trajectory shifts at the Jackson Hole symposium |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4992 | The Jackson Hole symposium is hosted annually by the Federal Reserve Bank of Kansas City in Wyoming |
| 2 | DISTR distractor | 0.5747 | The Federal Reserve is the central banking system of the United States, established by Congress in 1913 |
| 3 | DISTR distractor | 0.6678 | The European Central Bank president discussed inflation concerns at the Frankfurt banking conference |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 1.00 |
| Precision | 0.00 | 0.33 |
| MRR | 0.00 | 0.33 |
| Distractors | 3 | 2 |
| **Verdict** | **FAIL** | **PARTIAL** |

> 'Head of America's central banking system' not 'Fed Chair', 'Wyoming economics gathering' not 'Jackson Hole symposium'. Requires knowing Jackson Hole is in Wyoming. Distractors: different central bank (ECB), Jackson Hole tourism (not symposium), Fed meetings (not Jackson Hole).

---

### FAIL T3-13: COP summit -> UN climate conference

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| TARGET | The 1.5 degree Celsius warming threshold was reaffirmed at the latest COP summit |
| DISTR | The Paris Agreement initially established the two degree warming limit with aspirations for 1.5 degrees |
| DISTR | United Nations sustainability goals include emissions reductions across multiple sectors by 2030 |
| DISTR | Climate scientists warn that current warming trends exceed historical temperature baselines |
| DISTR | COP stands for Conference of the Parties and is the primary decision-making body of the UNFCCC |
| DISTR | Delegates at COP negotiate binding and non-binding commitments on emissions, finance, and adaptation |
| DISTR | The UNFCCC secretariat coordinates the annual COP process and tracks member state progress on climate commitments |

**Query:** What temperature goal did delegates commit to at the annual United Nations environmental negotiations?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4861 | Delegates at COP negotiate binding and non-binding commitments on emissions, finance, and adaptation |
| 2 | DISTR distractor | 0.4861 | COP stands for Conference of the Parties and is the primary decision-making body of the UNFCCC |
| 3 | DISTR distractor | 0.4861 | The Paris Agreement initially established the two degree warming limit with aspirations for 1.5 degrees |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4861 | Delegates at COP negotiate binding and non-binding commitments on emissions, finance, and adaptation |
| 2 | DISTR distractor | 0.5266 | United Nations sustainability goals include emissions reductions across multiple sectors by 2030 |
| 3 | DISTR distractor | 0.5323 | The UNFCCC secretariat coordinates the annual COP process and tracks member state progress on climate commitments |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 0.00 |
| Precision | 0.00 | 0.00 |
| MRR | 0.00 | 0.00 |
| Distractors | 3 | 3 |
| **Verdict** | **FAIL** | **FAIL** |

> 'United Nations environmental negotiations' not 'COP summit'. Requires knowing COP = UNFCCC Conference of the Parties. Distractors: past agreement (Paris), broader UN goals (not temperature specific), scientific warnings (not policy commitment).

---

### FAIL T3-14: Python: suitable vs unsuitable domains

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| DISTR | Python excels at rapid prototyping, data analysis, and machine learning workloads |
| DISTR | Python's extensive library ecosystem makes it ideal for web development and automation tasks |
| DISTR | Python has become the dominant language for scientific computing and numerical analysis |
| TARGET | Python is generally a poor choice for latency-sensitive mobile applications and GPU-bound game engines |
| DISTR | Real-time embedded systems and firmware development typically require C or C++ rather than Python |
| DISTR | Python's performance limitations make it unsuitable as the primary language for high-throughput trading systems |
| DISTR | Operating system kernels and device drivers cannot be written in Python due to memory management constraints |

**Query:** For which types of software projects is Python considered inappropriate?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4459 | Python's extensive library ecosystem makes it ideal for web development and automation tasks |
| 2 | DISTR distractor | 0.4459 | Python excels at rapid prototyping, data analysis, and machine learning workloads |
| 3 | DISTR distractor | 0.4848 | Python's performance limitations make it unsuitable as the primary language for high-throughput trading systems |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.4459 | Python's extensive library ecosystem makes it ideal for web development and automation tasks |
| 2 | DISTR distractor | 0.4848 | Python's performance limitations make it unsuitable as the primary language for high-throughput trading systems |
| 3 | DISTR distractor | 0.4890 | Python has become the dominant language for scientific computing and numerical analysis |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 0.00 | 0.00 |
| Precision | 0.00 | 0.00 |
| MRR | 0.00 | 0.00 |
| Distractors | 3 | 3 |
| **Verdict** | **FAIL** | **FAIL** |

> All memories discuss Python's applicability to different domains. Query asks for NEGATIVE cases ('inappropriate'). System must select the 'poor choice' memory among three positive statements.

---

### FAIL T3-15: Microservices: benefits vs drawbacks

**Case memories** (+ 20 shared noise memories above):

| Role | Content |
|------|---------|
| DISTR | Microservices enable independent scaling and faster deployment cycles for large teams |
| DISTR | Microservices architecture allows different teams to choose optimal technology stacks for their specific needs |
| DISTR | Microservices improve fault isolation so failures in one component don't bring down the entire system |
| TARGET | Microservices introduce significant operational overhead including distributed tracing, service mesh complexity, and cascading failure risks |
| DISTR | Teams adopting microservices must invest heavily in observability tooling including logging, tracing, and alerting |
| DISTR | Microservices increase deployment complexity as each service requires its own CI/CD pipeline and versioning strategy |
| DISTR | Distributed systems introduce network latency and partial failure modes absent in monolithic architectures |

**Query:** What are the downsides of breaking a system into many small services?

**Results (`search_agentic`):**

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5745 | Microservices improve fault isolation so failures in one component don't bring down the entire system |
| 2 | DISTR distractor | 0.5745 | Microservices architecture allows different teams to choose optimal technology stacks for their specific needs |
| 3 | DISTR distractor | 0.5745 | Microservices enable independent scaling and faster deployment cycles for large teams |

<details><summary>Results (<code>search</code>)</summary>

| # | Role | Score | Content |
|---|------|-------|---------|
| 1 | DISTR distractor | 0.5745 | Microservices improve fault isolation so failures in one component don't bring down the entire system |
| 2 | TARGET target | 0.5868 | Microservices introduce significant operational overhead including distributed tracing, service mesh complexity, and cas |
| 3 | DISTR distractor | 0.6732 | Microservices increase deployment complexity as each service requires its own CI/CD pipeline and versioning strategy |

</details>

| Metric | search | search_agentic |
|--------|--------|----------------|
| Recall | 1.00 | 0.00 |
| Precision | 0.33 | 0.00 |
| MRR | 0.50 | 0.00 |
| Distractors | 2 | 3 |
| **Verdict** | **FAIL** | **FAIL** |

> 'Downsides' targets the negative memory. All highly relevant to 'microservices'. System must distinguish the negative statement among three positive benefits. Note distractor_3 mentions 'failures' but in a positive framing (fault isolation).

---
