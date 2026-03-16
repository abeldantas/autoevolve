# Design Concepts

## Origin: autoresearch

Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) lets an AI agent autonomously run ML research experiments: modify training code, train for 5 minutes, check if the model improved, keep or discard, repeat overnight. You wake up to a log of experiments and a better model.

The core loop is simple:

```
mutate -> run -> evaluate -> keep or discard -> repeat
```

autoevolve takes this loop and applies it to **agent behavior files** instead of neural network training code.

## Key differences

| Dimension | autoresearch | autoevolve |
|---|---|---|
| What mutates | `train.py` (model code) | Agent instruction files (AGENTS.md, etc.) |
| What's fixed | `prepare.py` (eval harness) | IDENTITY.md, USER.md, framework |
| Fitness metric | val_bpb (deterministic, numeric) | Composite signal (noisy, subjective) |
| Iteration time | 5 minutes | 3 days (configurable via `eval_window_days`) |
| Evaluation | Automated (run script, read number) | Semi-automated (collect signals, compute score) |
| Decision | Automated (lower = better) | Human-in-the-loop (always review) |
| Risk | Low (bad model gets discarded) | Medium (personality drift damages trust) |
| Autonomy | "NEVER STOP" (fully autonomous) | Human-gated (you control the cadence) |

## Why the differences matter

**Fitness is noisy.** A training loss is deterministic — same code, same data, same number. Human reactions are context-dependent, mood-dependent, and sparse. This means:
- We need longer evaluation windows (days vs 5 minutes; default 3 days)
- We can't make binary keep/discard decisions on single data points
- Scores are **per-signal weighted averages** (not raw sums), so windows with different signal volumes are still comparable — a quiet week and a busy week produce scores on the same scale
- We use a threshold for revert decisions: 10% of the absolute pre_score with a minimum floor of 0.5, so near-zero scores don't cause spurious reverts

**Safety is higher stakes.** A bad ML experiment produces a bad model that gets discarded. A bad personality mutation can make the agent annoying, tone-deaf, or untrustworthy. Rebuilding trust is harder than retraining a model. This means:
- Human always reviews mutations before they're applied
- Certain files and sections are immutable
- Mutations are small (max 20 lines) and atomic (one change at a time)

**The search space is different.** Hyperparameters are continuous and numeric. Agent instructions are natural language — the space of possible changes is unbounded. This means:
- Signal analysis matters more than random exploration
- Mutations should be evidence-driven (based on actual feedback patterns)
- The simplicity criterion is even more important (less instruction = less confusion)

## Core principles

1. **One mutation at a time.** Change one thing, measure its impact, decide. Don't bundle changes.
2. **Signal-driven, not random.** Every mutation should be justified by observed feedback patterns.
3. **Simplicity wins.** Removing an unhelpful instruction is as valuable as adding a helpful one.
4. **Human in the loop.** The agent proposes, the human disposes. Trust is earned over time.
5. **Everything is logged.** experiments.tsv is the audit trail. Every mutation, every decision, traceable.
6. **Reversible by design.** Git commits are the mechanism. Any mutation can be reverted instantly.
