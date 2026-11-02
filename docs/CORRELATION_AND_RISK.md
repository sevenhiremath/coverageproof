# How we group findings and explain priority

## The problem
Two tools can describe the same condition differently. Matching titles alone can also combine different endpoints or even different assets. We need a useful grouping rule that a reviewer can inspect.

## Choice: exact asset identity and a small rule list
We group by the complete canonical URL (scheme, literal IP, port, path and query) plus an issue condition. Original tool identifiers, timestamps, severities, confidence labels, observation IDs and artifact references remain in the case.

The first cross-tool rule maps **ZAP rule 10021, GET, no parameter** to the registered HTTP GET check for X-Content-Type-Options. The official ZAP rule describes that condition: https://www.zaproxy.org/docs/alerts/10021/ . It does not establish that every response variant is identical. POST, parameter-specific results, unknown Nikto rules and unknown ZAP IDs stay separate.

| Option | Advantage | Drawback | Why we chose or deferred it |
|---|---|---|---|
| Exact identities plus explicit mappings | Inspectable and testable; avoids broad title matches | Misses duplicates not yet mapped | Chosen for the first working version |
| Match titles or CVEs | Fast and easy to implement | Same title/CVE can affect distinct assets or conditions | Not used as a merge rule |
| Ask an LLM to merge findings | Can recognize similar descriptions | Can merge unrelated issues and is harder to reproduce | Could propose related cases later; cannot silently merge them |
| Semantic/vector similarity | Finds wording variations | Needs thresholds and labeled evaluation; similarity is not equivalence | Deferred until genuine output data supports evaluation |
| Use a full vulnerability-management platform | Mature parser and case workflows | Adds a larger deployment and overlapping state model | Kept as a reference; small app remains easier to demonstrate |

## What happens when sources disagree?
A positive tool observation and a negative direct receipt for the same URL/condition remain attached to one case. The evidence status becomes `conflicting_observations`. No majority vote picks a winner. Time, response variants and configuration differences can explain disagreement. A negative receipt never creates a vulnerability by itself.

The benefit is that neither source disappears. The cost is that analysts must investigate rather than receive an automatic verdict. A report acceptance is still separate from this evidence status and does not erase the disagreement.

The raw receipts are unchanged. Existing exact-HTTP case identities remain stable. A source-only ZAP case newly mapped to a shared condition can receive a new case ID; old review events remain in the audit trail and are not silently transferred to the new case.

## Choice: explain priority without inventing a score
Order candidates by:
1. Highest supplied source severity.
2. Analyst-declared exposure.
3. Analyst-declared asset impact.
4. Analyst-stated validation with evidence references.
5. Asset and case ID for stable ties.

These are ordered comparisons, not a calculated CVSS or probability. Source confidence labels remain visible without treating labels from different tools as equivalent numbers. Missing CVSS, exposure and impact stay unknown. Different source severities remain visible; choosing the highest is conservative triage, not independent verification.

| Option | Advantage | Drawback | Decision |
|---|---|---|---|
| Source severity plus attributed context | Explains which inputs affected order; missing facts stay visible | Priority depends on source/analyst quality | Chosen; show every input and its limits |
| Severity only | Simple and reproducible | Misses asset context | Previous baseline; retained as the first ordering input |
| Weighted numerical risk score | Convenient single number | We have no validated weights or complete inputs | Not used |
| LLM assigns severity/CVSS | Flexible narrative reasoning | Can fabricate numbers or overstate confidence | AI may explain evidence, never invent scores |

An analyst who selects validated exploitability must cite observations from that finding and provide a reason. The backend verifies that references exist, not that they prove exploitation. The UI/report therefore label this as analyst-declared context. It is not an execution approval. Further semantic verification is still needed before a strong confirmed-exploitation claim.

## Verification and limits
Synthetic unit cases check cross-tool grouping, contradictory receipts, distinct assets/ports/paths/queries/methods, severity order independence, missing inputs, invalid evidence references, and UI/PDF/model-context consistency. These are parser/workflow tests, not genuine scanner recordings or measured real-world accuracy. Genuine Nmap/Nikto/ZAP lab outputs and live model evaluation are still pending.
