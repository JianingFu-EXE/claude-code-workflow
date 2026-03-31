# Literature Review Level

> **Grading Agent Technical Standard** -- populated from gold-standard samples extracted from 4 reference papers.
>
> **Reference Papers:**
> - **[P1]** Zhang et al. (2021) "Fault-Tolerant Optimal Control for Discrete-Time Nonlinear System Subjected to Input Saturation: A Dynamic Event-Triggered Approach" -- *IEEE Trans. Cybernetics* `/Users/jn/Library/CloudStorage/OneDrive-UniversityofExeter/Zotero/storage/CPBBIG8S/Zhang 等 - 2021 - Fault-Tolerant Optimal Control for Discrete-Time N.pdf`
> - **[P2]** Zhang & Zhao (2025) "Startup Control of Grid-Forming Offshore Wind Turbines Connected to the Diode-Rectifier-Based HVDC Link" -- *IEEE Trans. Sustainable Energy* `/Users/jn/Library/CloudStorage/OneDrive-UniversityofExeter/Zotero/storage/GSTPA7IN/Zhang and Zhao - 2025 - Startup Control of Grid-Forming Offshore Wind Turbines Connected to the Diode-Rectifier-Based HVDC L.pdf`
> - **[P3]** Zhao et al. (2022) "Deep Reinforcement Learning-Based Model-Free On-Line Dynamic Multi-Microgrid Formation to Enhance Resilience" -- *IEEE Trans. Smart Grid* `/Users/jn/Library/CloudStorage/OneDrive-UniversityofExeter/Zotero/storage/V4FBL4W3/Zhao et al. - 2022 - Deep Reinforcement Learning-Based Model-Free On-Line Dynamic Multi-Microgrid Formation to Enhance Re.pdf`
> - **[P4]** Zhao et al. (2025) "Event-Triggered H-Infinity Pitch Control for Floating Offshore Wind Turbines" -- *IEEE Trans. Sustainable Energy* `/Users/jn/Library/CloudStorage/OneDrive-UniversityofExeter/Zotero/storage/3WJQ2W9U/Zhao et al. - 2025 - Event-Triggered H-Infinity Pitch Control for Floating Offshore Wind Turbines.pdf`

---

## 1. Background

### Goal: Prove this area is important

The opening paragraph must establish that the **broad domain** commands attention -- via scale, societal impact, or technological trend. The best papers use concrete data (numbers, policy targets, physical consequences) rather than vague claims.

#### Standard Illustration -- Triangulated Samples

| Paper | Opening Sentence(s) | Structural Markers |
|-------|---------------------|--------------------|
| **[P1]** Zhang 2021 | *"Over the decades, nonlinear control theories have gained considerable research attentions due to their wide applications in electrical power systems, industrial control systems, and spacecraft attitude control systems."* | **Breadth-first enumeration**: lists 3 distinct application domains to establish universality. Uses temporal anchor ("Over the decades") to signal maturity of field. |
| **[P2]** Zhang & Zhao 2025 | *"More and more newly-built offshore wind farms (OWFs) with large capacities (above 1000 MW) will be located further than 100 km offshore. To connect these OWFs to the onshore power grid, high-voltage direct current (HVDC) transmission has been commonly recognized as a feasible and economical solution. For example, in the U.K., there will be 40 new offshore HVDC converters required to connect up to 75 GW remote OWFs by 2050."* | **Quantified trend + policy anchor**: 1000 MW capacity, 100 km distance, UK 75 GW by 2050. Concrete numbers make the importance self-evident. |
| **[P3]** Zhao 2022 | *"High-impact and low-probability events, such as extreme weather events, are occurring with increasing intensity. The extensive damage and subsequent outages of a power system caused by extreme events indicates the necessity of enhancing power system resilience."* | **Consequence-driven framing**: starts from real-world consequence (outages from extreme weather) to motivate the technical area (resilience). No abstract generality -- immediate physical stakes. |
| **[P4]** Zhao 2025 | *"Offshore wind turbines are set to become the most competitive form of wind power generation, which have the advantages of saving land resources and having stronger and steadier wind resources compared with onshore wind turbines. Owing to the limited resources of the offshore space, the offshore wind turbine continues to shift from the shallow to deep sea locations."* | **Technology trajectory**: establishes a directional trend (shallow -> deep sea) that naturally sets up the technical challenge (floating platforms, harsher environment). |

#### What makes these "Gold Standard"

1. **No vacuous importance claims** -- every sentence either provides data or describes a physical consequence
2. **Funnel geometry** -- broad domain (nonlinear control / offshore wind / grid resilience) narrowed within 2-3 sentences to the specific technological context
3. **Citation density is low** -- background paragraphs typically cite 2-4 foundational references, not exhaustive lists

---

## 2. Problem

### Goal: Prove this problem is important in this area

After establishing the area, the paper must isolate a **specific technical problem** and demonstrate it is (a) widely studied and (b) consequential. The transition from "area" to "problem" is the first major narrowing move.

- **Step 1**: State the problem
- **Step 2**: State this is widely studied

#### Standard Illustration -- Triangulated Samples

##### Step 1: State the Problem

| Paper | Problem Statement | Transition Mechanism |
|-------|------------------|---------------------|
| **[P1]** Zhang 2021 | *"In engineering practice, the actuator saturation phenomenon is pervasive due mainly to the protection facilities or physical limits of the actuators. If the saturation constraints are not taken into account in the controller design procedure, it is possible that the control performance degrades or even the overall stability is depraved."* | **Physical-consequence pivot**: moves from "nonlinear control" (area) to "actuator saturation" (problem) by citing physical limits. The word **"if... not taken into account"** frames the problem as a design-time failure mode. |
| **[P2]** Zhang & Zhao 2025 | *"However, the offshore HVDC converter platform with MMC is huge and requires high investment and maintenance costs. To cut the overall investment on the grid transmission systems for long-distance OWFs... the offshore HVDC converter adopts diode rectifier (DR)."* Then: *"However, the DR is a passive device and unable to build the offshore AC voltage, thus an external voltage source is essential for its conduction."* | **Cost-driven pivot + "However" chain**: two consecutive "However" sentences. First pivots from MMC cost to DR as alternative. Second immediately identifies DR's fundamental limitation. This **stacked-However pattern** is a hallmark of efficient gap identification. |
| **[P3]** Zhao 2022 | *"To fully utilize DERs to enhance power grid resilience, forming multiple MGs using DGs has become a promising solution for handling extreme conditions. The essence of the multi-MG formation (MMGF) problem is to identify the desired topology subject to various constraints."* | **Definitional pivot**: names the problem formally ("MMGF problem") and immediately defines its computational essence ("identify the desired topology"). This allows the reader to engage with the problem at a mathematical level. |

##### Step 2: Prove it is Widely Studied

| Paper | "Widely Studied" Evidence | Structural Markers |
|-------|--------------------------|-------------------|
| **[P1]** Zhang 2021 | *"Very recently, a wealth of literature has implemented the ADP approach in nonlinear control systems, such as power systems [35], mechanical systems [29], and intelligent transportation systems [41]. In particular, in [15], the stability analysis of the ADP has been investigated for the value iteration (VI)..."* | **Domain enumeration + deep dive**: first lists 3 application domains (breadth), then zooms into specific theoretical results (depth). This two-layer evidence structure proves both popularity and technical maturity. |
| **[P2]** Zhang & Zhao 2025 | *"Several methods have been investigated to provide such external voltage... For example, installing an additional voltage source converter (VSC) connected to DR [11]. However, this method will bring additional costs... An alternative approach is to control the offshore WTs with full power converters in grid-forming mode [12], [13]."* | **Solution enumeration + elimination**: lists existing approaches, systematically eliminates each with a technical or economic objection. Each elimination narrows the solution space toward the proposed approach. |
| **[P3]** Zhao 2022 | *"For the topology determination problem, mathematical programming [3], [4], [10] and heuristic search approaches [16], [17] are widely used methods. A mixed-integer non-linear programming (MINLP) model was built in [3]... The MMGF problem was formulated as a mixed-integer linear programming (MILP) model in [4]..."* | **Method taxonomy**: organises prior work into methodological families (mathematical programming vs. heuristic search), then reviews specific instances within each family. This categorical structure makes the review feel systematic rather than listing. |

---

## 3. Research Problem and Research Gap

### Goal: Settle the researched object by reviewing the domain

- **Important criterion**: prove the researched object is important
  - Such as: For load mitigation, there is active structural control, passive structural control, conventional control without ancillary support. Whatever I choose, this part should prove I choose this with a reason and it is widely studied.

### Goal: Sell the adopted methodology by review-based storytelling

- **Important criterion**: is methodology-level research gap stressed
  - Such as: If my work is model-free, then criticise model-based. If my work is nonlinear, criticise linear.

#### Standard Illustration -- Researched Object Justification (3-Paper Cluster)

| Paper | Researched Object | How Importance is Proven |
|-------|------------------|------------------------|
| **[P1]** Zhang 2021 | **Dynamic event-triggered FTC with ADP under input saturation** | Reviews FTC literature and input saturation literature *separately*, then shows the *intersection* is nearly empty: *"although fruitful results on the FTC and input saturation have been extensively studied, very few results investigate the fault-tolerant optimal control strategy for the discrete-time nonlinear systems subjected to the input saturation constraint."* **Venn-diagram gap**: two mature fields, empty intersection. |
| **[P2]** Zhang & Zhao 2025 | **Wind-energy-based startup of DR-connected GFM-WTs** | Enumerates existing startup methods (umbilical AC cable [14], BESS [15][16]) and eliminates each on cost/space grounds. Then shows that using the WT's own kinetic energy is unexplored: *"Instead, it is possible to use wind energy to complete these energization tasks to get rid of the additional grid support or the BESS."* **Elimination funnel**: all alternatives eliminated, only proposed path remains. |
| **[P4]** Zhao 2025 | **Event-triggered $H_\infty$ pitch control for FOWTs** | Reviews pitch control for FOWTs (continuous-time, [8]-[10]) and event-triggered control (power systems [18], nonlinear systems [19], DC microgrids [20][21]) *separately*, then reveals the gap: *"It should be pointed out that the event-triggered control has not been applied to pitch control of FOWTs."* **Domain-transfer gap**: method proven in adjacent domains, never applied to the target domain. |

#### Standard Illustration -- Methodology-Level Gap (3-Paper Cluster)

| Paper | Methodology Gap | Linguistic Markers | Structural Pattern |
|-------|----------------|-------------------|-------------------|
| **[P1]** Zhang 2021 | Existing dynamic ETM research *"mainly focused on the continuous-time systems or linear systems. To the best of our knowledge, very few efforts have been devoted to the investigation on dynamic event-triggered ADP-based optimal control strategy for nonlinear discrete-time systems, not to mention the systems with actuator faults and input saturation."* | **"not to mention"** -- escalation marker. Stacks the gap: first "nonlinear discrete-time" is under-studied, then "with faults AND saturation" is even more so. | **Stacked insufficiency**: linear->nonlinear gap + continuous->discrete gap + no faults/saturation = triple gap. |
| **[P3]** Zhao 2022 | *"The aforementioned MG formation strategies are mainly based on observable system conditions and environments with short-term considerations, while conditions under natural disasters might be uncertain and changeable... Therefore, an adaptive and dynamic MG formation strategy is needed."* Then: *"For the MMGF problem, the action space of DRL methods has exponential growth with the increase of the number of switches, which deteriorates the learning ability of DRL methods."* | **"mainly based on... while"** -- contrast marker. **"Therefore"** -- logical necessity. Then **second-order gap**: even DRL (the proposed method family) has a scalability problem that needs solving. | **Two-tier gap**: (1) static methods can't handle uncertainty, (2) even DRL has action-space explosion. Paper addresses both. |
| **[P4]** Zhao 2025 | *"For FOWTs, pitch control based on continuous-time control strategies requires continuous adjustment of the pitch angle, which increases mechanical wear. In view of this, we introduce the event-triggered control strategy into the $H_\infty$ pitch control."* Preceding this: *"$H_\infty$ theory has a superiority in rejecting uncertainty disturbances... However, there are only few results on $H_\infty$ problem of FOWTs."* | **"requires... which increases"** -- consequence chain. **"However, there are only few results"** -- scarcity marker. | **Consequence-to-solution**: identifies a practical drawback of continuous-time (mechanical wear), positions event-triggered as the natural remedy, and notes $H_\infty$ for FOWTs is itself under-explored. |

#### Key Linguistic Markers for Gap Identification

| Marker | Function | Example |
|--------|----------|---------|
| **"However"** | Signals limitation of cited work | *"However, the limitation of those studies is that they mainly focused on..."* [P2] |
| **"To the best of our knowledge"** | Claims novelty (use sparingly) | *"To the best of our knowledge, very few efforts..."* [P1] |
| **"not to mention"** | Escalation -- stacks additional gap on existing one | *"...not to mention the systems with actuator faults and input saturation."* [P1] |
| **"Although... very few"** | Concessive-scarcity pattern | *"although fruitful results on the FTC and input saturation have been extensively studied, very few results..."* [P1] |
| **"It should be pointed out that"** | Explicit gap declaration | *"It should be pointed out that the event-triggered control has not been applied to pitch control of FOWTs."* [P4] |
| **"mainly focused on... while"** | Scope-limitation contrast | *"mainly focused on the continuous-time systems or linear systems"* [P1]; *"mainly based on observable system conditions... while conditions under natural disasters..."* [P3] |

---

## 4. Methodology

### 4.1 Methodology Overall

- **Goal**: Prove the above gap is bridged

#### Standard Illustration -- Gap-Bridge Statements (3-Paper Cluster)

| Paper | Gap-Bridge Statement | Pattern |
|-------|---------------------|---------|
| **[P1]** Zhang 2021 | *"Summarizing the above discussions, in this paper, we devote ourselves to design a dynamic event-triggered fault-tolerant optimal control strategy for nonlinear discrete-time systems subjected to actuator faults and input saturation."* | **Summative bridge**: "Summarizing the above discussions" explicitly closes the review and transitions to contribution. Every gap word reappears: "dynamic event-triggered" + "fault-tolerant" + "optimal" + "nonlinear discrete-time" + "input saturation". |
| **[P3]** Zhao 2022 | *"For the purpose of realizing an on-line dynamic MMGF, a new deep RL-based model-free real-time adaptive scheme is proposed in this paper to enhance grid resilience over a long time-horizon."* | **Purpose-driven bridge**: "For the purpose of" + method descriptor that mirrors the gap (on-line, dynamic, model-free, real-time, adaptive, long time-horizon). Each adjective addresses a specific limitation identified earlier. |
| **[P4]** Zhao 2025 | *"Consequently, this paper integrates $H_\infty$ theory with pitch control of FOWTs to reduce power fluctuations and effectively reject external disturbances."* | **"Consequently"**: single-word logical bridge. The sentence directly combines the two reviewed threads ($H_\infty$ theory + FOWT pitch control) into one integrated proposal. |

### 4.2 Same or Similar Method Applied in Other Domain

- **Goal**: Prove this method is valid for this research problem because it was used in other domain facing the same problem

#### Standard Illustration (3-Paper Cluster)

| Paper | Cross-Domain Evidence | Structural Role |
|-------|----------------------|----------------|
| **[P1]** Zhang 2021 | ADP/RL methods reviewed in power systems [35], mechanical systems [29], intelligent transportation [41] -- all nonlinear control domains. Then specific theoretical advances: VI convergence [30], extension to unknown dynamics [34]. | **Method credibility via domain breadth**: ADP is proven across 3+ domains, establishing general reliability before applying it to the specific FTC problem. |
| **[P3]** Zhao 2022 | DRL reviewed as solving Markov decision problems generally: *"As an efficient solution to handle Markov decision processes (MDPs), DRL methods have become an attractive method for intractable problems in power systems."* Specific prior work: volt-VAR optimization via DQN [20], imitation learning for service restoration [21], energy management [22]-[24]. | **Method credibility via adjacent applications**: DRL proven in power-system sub-problems (voltage control, restoration, energy management), building confidence it can handle the related MMGF problem. |
| **[P4]** Zhao 2025 | Event-triggered control reviewed in power systems [18], nonlinear systems [19], DC microgrids [20][21]. $H_\infty$ reviewed for onshore WT control [14][15][16] and general disturbance rejection [11][12][13]. | **Two-method cross-validation**: both constituent methods (event-triggered + $H_\infty$) are independently validated in adjacent domains before being combined for the target domain. |

### 4.3 Same or Similar Method Applied in the Same Domain

- **Goal 1**: Prove other works had similar attempts, so my attempt is viable in nature
- **Goal 2**: Prove they have something insufficient and I am here to bridge the gap

#### Standard Illustration (3-Paper Cluster)

| Paper | Similar Attempts in Same Domain | Insufficiency Identified |
|-------|-------------------------------|------------------------|
| **[P1]** Zhang 2021 | Static ETMs applied to NCS: [2], [25]. Dynamic ETMs: leader-following multiagent [7], nonlinear stochastic [27], event-based filter [13]. | *"the researches on the dynamic ETM-based control problems have mainly focused on the continuous-time systems or linear systems"* -- **scope limitation**. No one has done discrete-time nonlinear with faults + saturation. |
| **[P2]** Zhang & Zhao 2025 | PLL-based synchronization [5], decentralized P/V and Q/f droop [8] for GFM-WT synchronization. | *"However, in weak systems or when the WTs intended to be synchronized with offshore networks are far from the point of common coupling (PCC), PLLs can negatively impact the transient stability of synchronization."* -- **operating-condition limitation**: existing method fails under realistic weak-grid conditions. |
| **[P3]** Zhao 2022 | DRL for energy management in MGs [22]-[24] shows "satisfying performance." | *"However, because of the difficulty of ensuring feasible radial topology, few studies have discussed the MMGF problem using DRL methods. For the MMGF problem, the action space of DRL methods has exponential growth..."* -- **scalability limitation** specific to the MMGF topology problem. |

---

## 5. Contribution

### Goal: At least three points

Contributions must be **tripartite**: domain-wise, research-problem-wise, and methodology-wise. The best contribution lists mirror the three-level gap structure established in the review.

#### Standard Illustration -- Contribution Structure Comparison

| Dimension | **[P1]** Zhang 2021 | **[P2]** Zhang & Zhao 2025 | **[P3]** Zhao 2022 |
|-----------|---------------------|---------------------------|-------------------|
| **Domain-wise** | NN-based observer under dynamic ETM for state + fault estimation | Startup process using kinetic wind energy (no external grid/BESS needed) | New DRL-supported on-line dynamic MMGF scheme; problem reformulated as MDP |
| **Research-problem-wise** | Nonlinear optimal control obtained via ADP under input saturation | Improved pitch control for low-power startup operation of GFM-WTs | Large action space mitigated via topology transformation + CNN action-decoupling |
| **Methodology-wise** | Stability analysis for overall closed-loop system (observer + ADP + dynamic ETM) | PLL-free synchronization strategy for DR-connected GFM-WTs within P/V and Q/f droop | CNN-based multi-buffer double DQN (CM-DDQN) with improved learning ability |

#### Structural Pattern: Gap-to-Contribution Traceability

Each contribution point should be **traceable** to a specific gap identified in the review:

```
[P1] Example traceability:
  Gap 1: "very few results investigate FTC optimal control for discrete-time
          nonlinear systems with input saturation"
  --> Contribution 2: "the nonlinear optimal control strategy is obtained by
                       using the ADP method" (under input saturation)

  Gap 2: "dynamic ETM research mainly focused on continuous-time or linear"
  --> Contribution 1: "NN-based observer proposed under dynamic ETM"
                       (discrete-time, nonlinear)

  Gap 3: No stability analysis for combined observer + ADP + ETM
  --> Contribution 3: "stability analysis is carried out for the overall
                       closed-loop systems"
```

```
[P4] Example traceability:
  Gap 1: "only few results on H-infinity for FOWTs"
  --> Contribution 1: "novel LPV model of FOWTs" (enabling H-infinity design)

  Gap 2: "event-triggered control has not been applied to pitch control of FOWTs"
  --> Contribution 2: "event-triggered control strategy introduced into
                       H-infinity pitch control of FOWTs for the first time"

  Gap 3: No criterion for combined asymptotic stability + H-infinity under ETM
  --> Contribution 3: "criterion proposed for asymptotic stability and
                       H-infinity norm boundedness under event-triggered strategy"
```

---

## Appendix: Structural DNA Summary

### A. The Canonical Flow (all 4 papers follow this)

```
Area Importance (1-2 paragraphs)
  |
  v  [narrowing pivot -- "However" / consequence]
Problem Isolation (1-2 paragraphs)
  |
  v  [enumeration + elimination of prior solutions]
Research Object Selection (1 paragraph)
  |
  v  [review of methodology family -- cross-domain then same-domain]
Methodology Review (2-4 paragraphs)
  |
  v  ["However" / "very few" / "not to mention" -- gap declaration]
Gap Statement (1-2 sentences)
  |
  v  ["Summarizing" / "Consequently" / "In this paper"]
Proposed Solution (1 paragraph)
  |
  v  [technical challenges as numbered questions -- optional]
Contribution List (numbered, 3+ points)
```

### B. High-Order Transition Patterns

| Transition Type | Pattern | Example |
|----------------|---------|---------|
| **General -> Specific** | Area -> Physical constraint -> Mathematical formulation | [P4]: "Offshore wind turbines" -> "floating platforms, complex wind-wave" -> "LPV model with $H_\infty$ disturbance attenuation $J_{y\omega} < 0$" |
| **Broad review -> Intersection gap** | Two literature threads reviewed independently, then gap at intersection | [P1]: FTC literature + input saturation literature -> "very few results at the intersection" |
| **Solution enumeration -> Elimination -> Proposal** | List N approaches, disqualify each, propose (N+1)th | [P2]: umbilical cable (cost) -> BESS (space) -> VSC (cost) -> wind energy (proposed) |
| **Method in other domain -> Method in same domain -> Remaining insufficiency** | Cross-domain credibility -> same-domain attempts -> specific limitation | [P3]: DRL in power systems generally -> DRL for MG energy management -> but MMGF has action-space explosion |

### C. Grading Diagnostic: What to Check

| Check | Gold Standard | Red Flag |
|-------|-------------|----------|
| Background uses data? | Numbers, dates, policy targets (e.g., "75 GW by 2050") | Vague claims ("increasingly important", "attracting attention") |
| Problem stated via consequence? | Physical/economic consequence of not solving | Problem stated as abstract academic curiosity |
| Gap uses Venn/elimination/transfer pattern? | Structured gap identification from review | Gap asserted without review evidence |
| Each contribution traces to a gap? | 1:1 mapping between gaps and contributions | Contributions disconnected from review narrative |
| Linguistic markers present? | "However", "although...few", "not to mention", "It should be pointed out" | No transition markers; abrupt jumps between topics |
| Citation density appropriate? | Background: 2-5 refs; Problem review: 5-15 refs per paragraph; Gap: 0-2 refs | Uniform citation density throughout (no modulation) |
