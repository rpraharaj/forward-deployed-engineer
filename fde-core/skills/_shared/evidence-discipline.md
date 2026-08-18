# Evidence discipline

The convention that every FDE skill depends on. Read this once per engagement; the compressed form is embedded in each SKILL.md.

## Why this exists

An FDE makes claims about systems they have known for days, to people who have known them for years. The claims will be checked. Being confidently wrong once, in front of the team that owns the code, costs more credibility than being slow costs — and it is very easy to do, because an unfamiliar codebase produces plausible-sounding conclusions that are subtly false.

The defence is not to be more careful. It is to make the *confidence level visible in the artifact itself*, so a reader can calibrate without having to re-verify everything. A document where the shaky claims are labelled shaky is more useful than one where everything reads equally certain — and it stays useful after you leave.

## The three tags

Attach exactly one to any claim that isn't trivially checkable by the reader.

**`[confirmed]`** — You read the code that does it, or you ran it and observed the result. You can point to the line or the command output.

> Orders are written to `orders` and `order_lines` in a single transaction `[confirmed: src/orders/OrderRepository.java:88-140]`

**`[inferred]`** — Strong signal from naming, structure, convention, or consistency with the rest of the system, but you did not verify it directly. Legitimate and useful; just labelled.

> The `legacy_` table prefix appears to mark the pre-2019 schema `[inferred: naming is consistent across 11 tables, no code references them]`

**`[unverified]`** — You believe it, it matters, and you couldn't check it. Usually blocked on access, environment, or a person. Always name what would resolve it.

> Nightly reconciliation runs at 02:00 UTC `[unverified: scheduler config is in an environment I can't reach — needs someone with prod Airflow access]`

## How to cite

Three forms. Use whichever is cheapest for the reader to re-check.

| Form | Use for | Example |
|---|---|---|
| `path:line` | Anything in the repo | `src/billing/Invoice.kt:212` |
| Command + output | Runtime behavior, counts, versions | `` `mvn -v` → Apache Maven 3.9.6, Java 17.0.9 `` |
| Person + date | Anything learned from a human | `per J. Okafor (platform team), 2026-03-14` |

A person+date citation is **not** `[confirmed]`. Confirmed means you read the code or ran it. Human recollection is `[inferred]` until verified, or `[unverified]` if it is memory of a design from years ago.

Cite the **narrowest thing that supports the claim**. `src/billing/` is not a citation; `src/billing/Invoice.kt:212` is. A reader who has to search for what you meant will stop checking, and then the discipline has bought nothing.

Include the commit SHA in the artifact header. A precise line citation against an unstated revision goes stale silently, which is worse than no citation at all — the reader trusts it and it has drifted.

## What this rules out

These are the specific failure patterns the tags exist to prevent. All of them read as authoritative.

- **Laundering inference as fact.** "The service retries three times" when you saw a constant named `MAX_RETRIES = 3` and never confirmed it is used on that path.
- **Confident silence about the gap.** Writing a complete-looking system map that simply omits the third of the system you couldn't reach. Omission reads as "not there."
- **Averaging.** Combining one confirmed fact and one guess into a single unlabelled sentence. Split them.
- **Citing the search, not the source.** "Grep shows this is unused" is a claim about grep. Dynamic dispatch, reflection, config-driven wiring, and string-built SQL all defeat it. Say what you searched and what that can't see.
- **Stale certainty.** A `[confirmed]` from three weeks and forty commits ago is now `[inferred]` at best.

## Escalating a tag

Tags move as you learn. When an `[unverified]` claim is load-bearing for a decision, that is a signal to spend the access request or the interview slot on it rather than on something cheaper. `feasibility-probe` and `release-readiness` both key off this: the residual `[unverified]` items *are* the risk register.

## When someone disagrees

A cited claim turns an argument into a check. If a long-tenured engineer says your map is wrong, the citation lets both of you look at the same line — and roughly half the time they are right and the code changed under a comment that didn't. Either way it resolves in a minute instead of becoming a standoff about who knows the system better, which is an argument the FDE will always lose.
