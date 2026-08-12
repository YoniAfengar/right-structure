# Answers

Fill this in as you go. It is checked, and it is where the actual understanding shows.

## Round 1 — prediction

How many comparisons would a single `serve` perform if `prepare` handed it the raw list of trips
untouched?

- My prediction: 

                About 200,000 comparisons, because serve would need to scan all 200,000 trips and compare each trip’s station with 
                the requested station.

- What the test reported: 

                The test passed and the number of comparisons was within the required limit.

- Why the difference (if any):

                Because prepare counts the trips for each station in advance, serve can get the result directly without going through all the trips again.
                
## Round 2 — the cost of the second question

Name the cost you took on in this round that Round 1 did not have:

                Round 2 uses more memory because we keep an additional dictionary with a lookup entry for every trip.

A colleague proposes that `prepare` should build only what the support desk needs, and that the
dashboard's answer be recomputed on demand. Under what mix of the two question kinds is she right?

                The colleague is right if ByStation queries are very rare compared to ByReceipt queries. In that case, it may be better to calculate the station count only when it is needed instead of storing it in advance.

## Round 4 — what `prepare` now costs

`prepare` costs more than it did in Round 1. Say what it costs, and why the trade is worth it here and
not there.

prepare now costs O(n log n) because it sorts all trips by start time before building the timestamp and prefix-sum lists. The extra cost is worth it because every range query can then find its boundaries in O(log n) and calculate the total distance in O(1). In Round 1, sorting would not help because a dictionary already gives direct O(1) station lookups.


## Round 6 — the five decisions

| round | `Round<N>Prepared` | the one property of the demand that forced it |
|---|---|---|
| 1 | `dict[Station, int]` | We needed repeated trip-count queries by station without scanning all trips every time, so we counted them once in `prepare()` and used direct lookups in `serve()`. |
| 2 | `tuple[dict[Station, int], dict[tuple[Station, TripId], Trip]]` | We needed to keep the station-count query while also supporting direct lookup of a specific trip by `(Station, TripId)`, so we prepared both indexes in advance. |
| 3 | `dict[Station, Distance]` | We needed the top `k` stations by total distance without sorting every station for each query, so we prepared the total distance per station and used a min-heap in `serve()` to keep only the top `k`. |
| 4 | `tuple[list[Timestamp], list[Distance]]` | We needed the total distance for trips in a time range without scanning all trips for every query, so we prepared sorted timestamps for fast boundary searches and prefix sums for constant-time range totals. |
| 5 | `tuple[str, int]` | The data was a tree of unknown depth, and a region's size depended on all files below it, so we recursively calculated each top-level region's total size and prepared only the largest region's name and size. |


### (a) Round 4 vs a balanced binary search tree

Describe the one change to Round 4's workload that flips the answer, and say precisely what Round 4's
structure would then have to pay.

If new trips were inserted continuously, Round 4's structure would become expensive to maintain. A new trip may need to be inserted in the middle of the sorted timestamps, which requires shifting later elements and updating all prefix sums after that position. This can make each insertion O(n), and we would pay that cost repeatedly as new trips arrive. A balanced search tree is a better fit when the workload includes frequent inserts as well as range queries.

### (b) The refactor that did not happen

Describe what you would have had to change in a codebase where the prepared structure was passed
around directly and every caller reached into it in-line.

If the prepared structure had been passed around directly, changing it in Round 2 would have required finding and updating every caller that accessed the old dictionary structure. Each caller would need to know about the new tuple and how to reach the correct dictionary inside it. By hiding the structure behind the `Round<N>Prepared` TypeAlias, `prepare()`, and `serve()`, the change stayed local instead of causing a refactor across the whole codebase.