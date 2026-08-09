# Answers

Fill this in as you go. It is checked, and it is where the actual understanding shows.

## Round 1 — prediction

How many comparisons would a single `serve` perform if `prepare` handed it the raw list of trips
untouched?

- My prediction:
- What the test reported:
- Why the difference (if any):

## Round 2 — the cost of the second question

Name the cost you took on in this round that Round 1 did not have.

A colleague proposes that `prepare` should build only what the support desk needs, and that the
dashboard's answer be recomputed on demand. Under what mix of the two question kinds is she right?

## Round 4 — what `prepare` now costs

`prepare` costs more than it did in Round 1. Say what it costs, and why the trade is worth it here and
not there.

## Round 6 — the five decisions

| round | `Round<N>Prepared` | the one property of the demand that forced it |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

### (a) Round 4 vs a balanced binary search tree

Describe the one change to Round 4's workload that flips the answer, and say precisely what Round 4's
structure would then have to pay.

### (b) The refactor that did not happen

Describe what you would have had to change in a codebase where the prepared structure was passed
around directly and every caller reached into it in-line.
