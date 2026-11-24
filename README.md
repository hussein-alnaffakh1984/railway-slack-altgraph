# railway-slack-altgraph

Code, data and solver logs for the paper

> **Bottleneck-Targeted Timetable Slack in Alternative-Graph Train Rescheduling: Validation on a Published Station Instance** (ISCKU 2026, revised version).

The paper studies where a fixed total *early-departure allowance* (the flexibility of a flexible timetable) should be
placed in an alternative-graph rescheduling model. Every number in the revised paper and its supplement is regenerated
by the scripts in `code/revision/`.

## Requirements

Python 3.13 and `pip install -r requirements.txt` (`pulp==3.3.2`, which bundles CBC 2.10.3; `scipy`, `networkx`,
`matplotlib`, `python-docx` is not needed). All runs are deterministic: fixed seeds, one solver thread.

## Run order and expected output (revised paper)

Run from `code/revision/`.

| step | command | expected output | time |
|---|---|---|---|
| 1 | `python test_engine.py` | `MILP == enumeration (values and binding tests) on all grid points of the published instance` | 30 s |
| 2 | `python published_events.py` | `event times compared: 9 inputs + 33 model outputs; secondary delays compared: 15; all equal: True` | 1 s |
| 3 | `python published_budget_scan.py` | `budgets 1..50: targeted = optimal allocation in 50; certificate holds in 50` | 1 min |
| 4 | `python slack_experiments.py station` | `results_station.csv` (564 cases) | 5 min |
| 5 | `python slack_experiments.py junction` | `results_junction.csv` (140 cases) | 12 min |
| 6 | `python slack_experiments.py corridor` | `results_corridor.csv` (60 cases) | 13 min |
| 7 | `python analyse.py; python make_tables.py` | counts of Table 6 and shares of Figure 4 (`summary.json`) | 1 s |
| 8 | `python bigM_check.py; python bigM_check_slack.py` | `all 20 instances: M valid and optimum independent of M and equal to branch-and-bound: True` | 1 min |
| 9 | `python stats_revised.py` | descriptive statistics and the FCFS-AMCC comparison of Section 7 | 1 s |
| 10 | `python bnb_table.py; python scale_proof2.py` | supplement tables S6a, S6b | 2 + 12 min |
| 11 | `python figures_static.py; python figure_families.py` | Figures 1-4 (`fig/`) | 30 s |
| 12 | `python compare_runs.py` | `both runs identical: True` (compares with the second run stored in `run2/`) | 1 s |

Key numbers to expect: published instance 41 / 31 / 18 s; equal-budget table 36/31, 31/23, 28.5/18; synthetic study
764 cases, condition (H) certified in 631, targeted vs. uniform in certified cases 206 better / 425 equal / 0 worse.

## Layout

| path | content |
|---|---|
| `code/revision/ag.py` | generic alternative-graph engine: exact longest paths, MILP on integer-scaled data, exact test "some optimal selection has a binding departure arc", optimal allocation, finite certificate |
| `code/revision/families.py` | instance families: published station, perturbed stations, junction, corridors |
| `code/revision/slack_experiments.py` | the four allocation policies and the certificate for every case |
| `code/revision/results_*.csv`, `run2/` | per-case results of the two independent runs |
| `code/revision/logs/` | CBC logs of the larger corridors (proof status is read from these logs) |
| `code/railsched.py` | corridor generator, plain and propagation branch-and-bound, AMCC, FCFS |
| `code/*.py` (other) | scripts of the first submission, kept for the record; superseded by `code/revision/` (see supplement S9) |
| `results/`, `figures/`, `logs/` | files of the first submission |

## What changed with respect to the first submission

See supplement S9. In short: the binding test of the corridor experiment referred to the makespan instead of the
maximum lateness and is corrected; sampled checks of the theorem's condition are replaced by an exact certificate;
two instance families, a third budget and the optimal allocation are added; significance tests against the optimum
are removed.

## License

MIT (see `LICENSE`).
