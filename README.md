# Right Data Structure

_Picking the structure the business is asking for._

Same bike-share as the ingest exercise, one floor up. The trips are already loaded; you are on the
team that answers questions about them. The questions arrive as sentences from humans, and each new
one **quietly invalidates the structure that answered the last.**

That is the entire exercise. You will write about a dozen short functions. None of them is long. The
work is deciding what to put the data *in* — and the harness will not let you get it wrong by
accident.

Every round tells you the business demand and the cost you must hit. It does not tell you how. That
is the exercise; if you are stuck, you are in the right place.

**Budget** ~2h50, including §0.

---

## 0. Your repository (~10 min)

This exercise leaves the course. Copy it somewhere on your own machine — **not** into the course repo:

```bash
cp -R hands-on/practicum/right-structure ~/projects/right-structure
cd ~/projects/right-structure
git init && git add -A && git commit -m "Start from the provided stub"
```

Commit the stub **before you write a line**, so your history shows what you did rather than what you
were handed. Then create an empty repository on GitHub, and:

```bash
git remote add origin git@github.com:<you>/right-structure.git
git push -u origin main
```

Commit as you finish each round — the rounds are the natural commits, and a reviewer should be able to
read your history and see the structures change under the demands.

**You hand in the repository URL.** It must contain: every round green (`uv run pytest`), a clean
`uv run mypy src/`, and a filled-in `ANSWERS.md`.

You need `git`, `uv`, and Python 3.11+. No Docker, no database — this one is pure Python.

---

## 1. The shape of every round

Every round asks you for the same two functions, and this split is the whole design:

```python
def prepare(trips: Sequence[Trip]) -> PreparedDataStructure         # run ONCE, at startup
def serve(prepared: PreparedDataStructure, query: Query) -> Answer  # run MILLIONS of times
```

`prepare` gets the raw trips and builds whatever you like out of them. `serve` answers one question
using only what `prepare` built. They are two ordinary module-level functions — no classes here. The
harness invokes them exactly like a real service would:

```python
prepared = prepare(trips)             # once, at boot
for query in queries:                 # 100,000 times, while users wait
    answer = serve(prepared, query)
```

`prepare` is allowed to do real work; it runs once, while nobody is waiting. `serve` runs in the
request path.

**`PreparedDataStructure` is yours to choose, and choosing it is the exercise.** It is not a parameter
we hand you — it is the return type of `prepare` and the argument type of `serve`, and those two must
agree. That agreement is expressed with a **generic**.

### Why the type is generic — read this once

Look at the signatures again: `prepare` returns some type, and `serve` consumes *that same type*. We
cannot name it here, because it changes every round. But it must be *the same one* on both sides.

`given/round.py` says exactly that, with a **type variable** — a hole in a signature that gets filled
in once and then has to stay filled the same way:

```python
PreparedDataStructure = TypeVar("PreparedDataStructure")

def check_round(
    prepare: Callable[[Source], PreparedDataStructure],
    serve: Callable[[PreparedDataStructure, Query], Answer],
) -> None: ...
```

`PreparedDataStructure` appears twice: as what `prepare` returns and as what `serve` takes. That single
name is the whole point — if your two functions disagree about the type, mypy has no consistent thing
to put in the hole and it says so. If the contract had used `Any` instead, `prepare` could return one
thing,
`serve` could take another, and nothing would complain until it crashed in production.

In your solution you fill the hole and let `mypy` check that you filled it consistently. The last line
hands your two functions to `check_round`; it does nothing at runtime, it only makes the type checker
line them up:

```python
Round1Prepared: TypeAlias = ...                  # <- YOUR structural decision, in one line

def prepare(trips: Sequence[Trip]) -> Round1Prepared: ...
def serve(prepared: Round1Prepared, station: Station) -> int: ...

check_round(prepare, serve)                       # keep this line; mypy fails if the ends disagree
```

Notice what that `TypeAlias` line has become: **the answer to the round, written down.** Change it and
everything else must change with it. That is not an accident of the exercise; that is what a good type
does.

> Generics in full — parameterised classes, bounds, variance — are
> `python/22-type-hints-generics-and-advanced`. You need only the paragraph above to finish this.

---

## 2. How you are checked

Twice per round: on **what `serve` returns**, and on **what it cost to run**.

Cost is not measured with a stopwatch. Stopwatches are flaky on a shared machine and they teach you
nothing about *why*. Instead, **the dataset counts.** The `Trip`, `Station`, `TripId`, `Timestamp`, and
`Distance` objects in `given/probe.py` keep a tally of every question your code asks them:

```python
prepared = prepare(trips)             # not measured, unless the round says otherwise

with count_ops() as ops:
    for q in queries:
        answers.append(serve(prepared, q))

assert answers == expected                       # did you get the right answer
assert ops.comparisons <= 2 * len(queries)       # ...at the cost this round demands
```

Correctness is asserted first, always. A fast wrong answer fails on the answer. A right slow answer
fails on the cost.

The tally has four fields:

| field | counts |
|---|---|
| `ops.hashes` | a value was asked for its hash |
| `ops.comparisons` | two values were checked for equality |
| `ops.orderings` | two values were asked which comes first |
| `ops.arithmetic` | two distances were added or subtracted |

**You never touch a counter, and you import nothing special into your solution.** You write ordinary
Python over ordinary-looking objects. `count_ops()` is yours to use while you work — wrap your own
experiments in it and watch the count explode when you write the first thing that comes to mind. That
moment is the lesson; the test just makes sure you had it.

> Outside a `count_ops()` block the tally is inert, so your own scripts pay nothing for it.

<details>
<summary><b>Optional enrichment — how the counting works.</b> Skip this; you do not need it.</summary>

Nothing in the harness inspects your code. It cannot: your `serve` is a black box to it. Instead,
Python itself reports what happened. When a container looks something up, when you ask whether one
value equals or precedes another, the work is not done by the operator — the operator *asks the
objects*, by calling methods on them (`__hash__`, `__eq__`, `__lt__`). The given types simply count
those calls on the way past.

So the tally is not an estimate, and it is not instrumentation bolted onto your functions. It is the
exact number of questions your algorithm asked the data. `python-data-model` is where this is taught
properly.
</details>

## What's given — do not edit

```
given/
  round.py       check_round(), the type variable behind it, and the Round 2 query types
  probe.py       count_ops(), and the counting domain types
  catalog.py     the drop catalog (Round 5) — nodes and children, nothing else
  fixtures.py    seeded generators for trips, query workloads, and the catalog
tests/           one suite per round: correctness, then cost
src/             the five files you fill in
```

---

## Round 1 — "How many trips started at each station?" (~25 min)

**Query:** a `Station`. **Answer:** how many trips started there.

200,000 trips, 200 stations. The dashboard calls `serve` once per station on every page load.

**Required cost:** `serve` must be **O(1)** — its cost cannot grow with the number of trips.

**Gate:** `ops.comparisons <= 2 * len(queries)`. `prepare` is not measured.

**Predict before you run:** write down, in `ANSWERS.md`, how many comparisons a single `serve` would
perform if `prepare` handed it the raw list of trips untouched. Then run the test and compare.

---

## Round 2 — "Support has a receipt and needs the trip." (~30 min)

**Query:** a `ByStation`, or a `ByReceipt` (which carries the station *and* the trip id, both printed
on the customer's receipt). **Answer:** the trip count, or the `Trip` itself.

Round 1 shipped and it works. Now the support desk calls: a customer is disputing a charge, and reads
you the receipt. The dashboard has not gone away — it still needs Round 1's answer, at Round 1's cost.

This round's dataset is 200,000 trips spread across just **20** stations.

**Required cost:** both questions must be answered in **O(1)**. Neither may cost anything that grows
with the number of trips, or with the number of trips at a station.

**Gate:** `ops.comparisons <= 2 * len(queries)`, over a workload mixing both question kinds.

**Then answer in `ANSWERS.md` (3–5 sentences):** name the cost you took on in this round that Round 1
did not have. Then: a colleague proposes that `prepare` should build only what the support desk needs,
and that the dashboard's answer be recomputed on demand. Under what mix of the two question kinds is
she right?

---

## Round 3 — "The ten busiest, live on the wall display." (~30 min)

**Query:** an integer `k`. **Answer:** the `k` stations with the most metres ridden from them,
most-first.

5,000 stations. The display refreshes constantly, and `k` changes whenever someone drags the window
wider.

**This round measures `prepare` as well as `serve`**, and the gate is on the sum of the two. The totals
change often enough that anything `prepare` precomputes about their order is stale before the first
query arrives — so there is nowhere to hide the work.

**Required cost:** answering a query must cost **O(n)** orderings, not O(n log n).

**Gate:** `ops.orderings <= 3 * n_stations`, summed over `prepare` and `serve`.

Write it yourself rather than reaching for the standard library. It is a couple of dozen lines, and you
will understand it better than you would understand the library call.

---

## Round 4 — "Total distance of trips that started between 09:00 and 11:00." (~35 min)

**Query:** a half-open time range `[lo, hi)`. **Answer:** the total distance of every trip that started
inside it. Any range, hundreds of times a second.

200,000 trips. Nobody asks about an exact timestamp — every query is a span, and the spans differ each
time. Some match two hundred trips; some match forty thousand.

**Required cost:** two independent demands, and you must satisfy both.

1. *Finding* the range must cost **O(log n)**.
2. *Totalling* it must cost **O(1)** — the answer for a span matching 40,000 trips must cost what the
   answer for a span matching 200 costs.

**Gates:** `ops.orderings <= 4 * log2(n)` per query, **and** `ops.arithmetic <= 2` per query.

Mind the boundary: the range is half-open, `lo` is in and `hi` is out. An off-by-one here is a wrong
invoice.

**Then answer in `ANSWERS.md` (2–3 sentences):** `prepare` now costs more than it did in Round 1. Say
what it costs, and why the trade is worth it here and not there.

---

## Round 5 — "Which region is costing us the most storage?" (~30 min)

**Query:** nothing. **Answer:** the top-level region holding the most bytes, and how many.

The vendor reorganised the bucket. Drops no longer sit in one folder: they arrive under a catalog of
regions, regions sit inside regions (`emea` contains `uk` contains `london`), the nesting depth is not
fixed and not uniform, and only the leaves hold files. Finance wants the *top-level* region whose
subtree holds the most bytes in total.

`given/catalog.py` hands you the catalog already built. A node has a name, a size if it is a file, and
children if it is not. It has no other methods — no traversal, no search, no iteration. Those are yours.

Notice what has changed about this round: the previous four asked you to choose a structure and paid
you in speed. This one does not. The structure arrived with the data, and it is the only structure that
could have carried it. Ask yourself, before you write anything, what it would even *mean* to sort this
catalog — and what you would sort it by.

**Required cost:** none. This round is checked on correctness alone.

**Gate:** correctness on a six-level catalog containing an empty region, a region holding no file at
any depth, and a file whose name looks like a region's.

---

## Round 6 — Written, no code (~15 min)

In `ANSWERS.md`, for each of Rounds 1–5: name your `Round<N>Prepared` type in one line, and give the
**one property of the business demand** that forced it.

Then answer these two.

**(a)** Round 4's structure answers range queries in O(log n). So does a balanced binary search tree —
and the tree uses more memory, chases pointers, and is a great deal more code. Nobody builds one for a
workload like Round 4's. Yet balanced trees are everywhere in real systems, including inside the
database you loaded these trips into. Describe the one change to Round 4's workload that flips the
answer, and say precisely what Round 4's structure would then have to pay.

**(b)** Round 2's demand arrived *after* Round 1 shipped, and `Round1Prepared` had to change. Because
the structure was named by a `TypeAlias` and hidden behind `prepare` and `serve`, that change touched
three lines. Describe what you would have had to change in a codebase where the prepared structure was
passed around directly and every caller reached into it in-line.

This is the round that decides whether you learned anything.

---

## The size gate

`tests/test_size.py` fails if any function in `src/` exceeds **20 code lines** or any file exceeds
**250**. It will not fight you here — if one of these functions is over 20 lines, you are solving the
wrong problem.

## Done when

```bash
uv run pytest        # every round green: correctness AND cost
uv run mypy src/     # strict — this is what checks that prepare and serve agree
```

`ANSWERS.md` is filled in, everything is committed, and the branch is pushed.

## Why this matters

Nobody in your career will name a data structure for you. They will say *"this report takes four
hours,"* or *"support needs to look it up from the receipt,"* or *"just the top ten, but live,"* or
*"anything between nine and eleven."* The skill is hearing the data structure inside the sentence — and
noticing, without being told, when yesterday's right answer became today's wrong one.
