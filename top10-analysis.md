# Top-10-first analysis — btc-race-24h-20261118-1444

Source: full leaderboard JSON of the closest scored sibling race
`btc-race-24h-20261117-0603` (`/tmp/btc0603-lb.json`, 4,387 entries,
resolved 18 Nov 2026 12:46 UTC). Race window 17 Nov 12:18 UTC → 18 Nov
12:18 UTC. Analysis written 18 Nov 2026 ~22:32 WIB, before building.

## The regime the top 10 won in

The 0603 race window was a **falling, choppy** window: buy-and-hold lost
**−$13.10** (−1.31%), momentum −$15.60, ema-cross −$149.00 (81 trades,
maxDD 15.0%). Only **26.6% of all 4,387 entries finished positive**;
the median entry lost −$4.90. So the winning edge was NOT riding the
trend — it was harvesting the bounces inside a downtrend while staying
mostly in cash.

## Top 10 (exact leaderboard values, net PnL in USDC)

| # | Handle | Title | Net PnL | Trades | MaxDD | Sharpe |
|---|--------|-------|--------:|-------:|------:|-------:|
| 1 | strescco | Stabilised dip-buy cbBTC bot v2 | +$24.20 | 4 | 0.64% | 0.049 |
| 2 | zesty-condor-60 | Dip-buy CBBTC bot | +$23.80 | 4 | 0.64% | 0.050 |
| 3 | daring-harbor-13 | Dip-buy swing bot: CBBTC 1-minute mean reversion | +$22.90 | 8 | 1.59% | 0.029 |
| 4 | tiar9 | Range-dip mean-reversion BTC bot v4 | +$21.60 | 4 | 0.64% | 0.048 |
| 5 | brisk-sparrow-99 | dip-buy + regime filter | +$21.50 | 4 | 0.64% | 0.047 |
| 6 | clever-badger-24 | Dip-Buy BTC Bot — 6h pullback entries, TP/SL exits | +$21.00 | 4 | 0.71% | 0.038 |
| 7 | putra2230 | Dip-Reclaim cbBTC Bot | +$20.50 | 4 | 1.02% | 0.038 |
| 8 | rambut29 | Stall-Top Dip Bot v2 | +$20.40 | 2 | 1.50% | 0.029 |
| 9 | profmey | Rolling-high pullback bot | +$20.20 | 4 | 0.64% | 0.044 |
| 10 | lucky-meteor-24 | METEOR HARVEST | +$19.90 | 8 | 0.63% | 0.037 |

Cut-offs: 10th place +$19.90, 50th place +$16.50. Our own 0603 entry
ranked 299/4,387 (prize_rank 274) at +$9.42, 4 trades, maxDD 1.58% —
about $10.50 short of 10th place, i.e. roughly one more winning round
trip.

## What the top 10 have in common

1. **Dip-buy / mean-reversion, unanimously.** 9 of 10 titles say
   dip-buy / dip / pullback / mean-reversion; the 10th (METEOR HARVEST)
   behaves the same (8 trades, 0.63% DD). In the top 100 titles,
   "dip" appears 66 times, "rsi" 20, "mean/reversion" 15–17, "bounce"
   10 — while "momentum" appears once, "ema" once, "trend" once.
   Momentum and trend-following are dead in this regime; they also died
   on our own dev windows (momentum best +$0.29 on 0603 dev, 0/1,152
   configs positive on the 2314 window).
2. **Very few trades: 2–8, mostly 4 (= 2 round trips).** The winners
   caught one or two big V-bounces and then sat in cash. Only one top-20
   entry traded 18 times (PUFFIN ANCHOR LADDER, rank 12, +$19.60);
   over-trading bleeds 26 bps per round trip and loses.
3. **Tiny drawdowns: 0.63–2.01%.** Five of the top 10 share maxDD
   0.64% — they entered the same dip, exited near the same top, and
   never held through a leg down. Tight trailing exits, not hope.
4. **Tight PnL cluster ($19.90–$24.20).** The top 10 all harvested the
   same 1–2 moves; the difference between 1st and 10th is ~$4.30, i.e.
   one slightly better entry/exit, not a different strategy. Execution
   quality on the shared dips decides the places.
5. **Regime filter is a plus, not the edge.** Rank 5 is literally
   "dip-buy + regime filter" (+$21.50). The filter keeps the bot out of
   waterfall legs; the dip-buy does the earning.
6. **Identical-behaviour trap is real.** Rank 20 (amber-koala-53,
   +$18.50) took NO prize: marked `identical_behaviour` — its action
   log byte-matched an earlier entry. A copy of a common dip-buy
   recipe can rank top 20 and still pay $0. Our entry must be
   behaviourally distinct, not just reworded.

## What this means for THIS race (1444)

Dev window 1444 (ends at the 14:44 UTC opening): BTC $65,074 → $63,261,
**−280 bps over 24h**, choppier than the 0603 dev window (+0.49%):
hours 0–4 −218 bps, 4–8 +173 bps, 8–12 −67 bps, 12–16 +41 bps,
16–20 −50 bps, 20–24 −154 bps. Buy-and-hold ≈ −$29.56. Deepest 60-min
drop −231 bps (bars ~65–73); biggest 60-min rise only +119 bps
(bars ~500–514). Bounces are weaker here than in 0603: of 46 bars with
a 60-min return ≤ −90 bps, only 15 bounced +15 bps in the next 5 min
and only 4 reached +100 bps within 30 min. A bot that waits for a
strong bounce confirmation (+15 bps/5 min, our 0603 recipe) still
passes the dev gate on this window (+$10.34 in the sweep replica) but
leaves money on the table — the confirmation is too strict for this
window's shallow bounces.

## Design decisions taken from the analysis

- **Family: dip-buy mean-reversion** (the only family in the top 10),
  but a **fresh trigger**: drawdown from the **240-bar rolling high**
  (not a 60-bar slide) + a light **3-bar recovery tick** (+5 bps, not
  +15) + a **720-bar regime guard** (no entries in a waterfall). This
  is behaviourally distinct from our 0603 dip-bounce catcher
  (60-bar slide + 5-bar bounce) and from the generic dip-buy crowd.
- **Few, full-size round trips**: all-in entries, target +120 bps,
  trailing −100 bps from the peak close, hard stop −150 bps,
  max hold 360 bars, 20-bar cooldown after an exit. No EMA
  confirmation (the sweep shows it costs money here: +$5.71 vs +$22.23)
  and NO stall/dead-money exit (the sweep shows it destroys the
  result: +$22.23 → −$3.09).
- **Sweep result on the 1444 dev window** (20,736 configs, float fill
  model: 4 bps fee + 2 bps slippage + a/depth impact): chosen config
  **+$22.23, 6 trades (3 round trips), maxDD 1.09%**. Plateau, not a
  knife-edge: D 120–150 bps → +$21.52…+$22.23; B 0–5 bps → +$22.25…+$22.23;
  T 100–120 bps → +$22.23…+$22.50; R 100–120 bps → +$22.23;
  cooldown 10–20 bars → +$22.23; hi-window 120 → +$17.58, 240 → +$22.23.
  Every one-parameter neighbour stays positive (+$5.71…+$24.36).
  Three round trips, all winners: bars 72→86 (+$9.51), 110→470
  (+$8.07), 727→1087 (+$4.65).
- **Risk note (honest):** dev +$22.23 is a 3-trade sample. The race
  window is unseen; if it has no ≥150 bps drawdown from a 240-bar
  high, the bot trades 0 times and fails the guardrail (needs ≥1
  trade). That is the known cost of a selective dip-buyer — accepted,
  because indiscriminate entries are what put 73% of the 0603 field
  below zero.
