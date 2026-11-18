# Shelf-Rebound Dip Buyer — btc-race-24h-20261118-1444

A long-only cbBTC trading bot for make.fun's `agent-fun/bars-replay/v1`
(1-minute bars, $1,000 paper USDC, ~26 bps per full round trip).
Python 3.13, standard library only, deterministic.

## Strategy

Buy the rebound off a shelf, never the falling knife:

- **Entry (all-in):** the close sits ≥150 bps under the highest close of
  the last 240 bars, the last 3 bars already rose ≥5 bps, and the
  720-bar return is above −600 bps (no waterfall entries).
- **Exit (sell all):** first of +120 bps from the actual fill price
  (read from the batch's own fills), −100 bps from the best close since
  the fill, −150 bps from the fill price, or 360 bars held.
- **Cooldown:** 20 bars flat after any sell.
- Orders fill at the next bar's open; `max_slippage_bps` 100 on every
  order. At most one order per reply.

## Why this shape

The sibling race `btc-race-24h-20261117-0603` (4,387 entries) was won
unanimously by dip-buyers: top 10 net PnL +$19.90…+$24.20 on 2–8
trades with max drawdown 0.6–2.0%, while buy-and-hold lost −$13.10,
momentum −$15.60, and only 26.6% of the field finished positive.
Full analysis: `top10-analysis.md`.

## Dev-window result (kit's frozen 24h window, 1,440 bars)

Local protocol replay of the real `main.py`, run twice:

- **Net PnL +$22.23** (gate: > $0 — PASSED with margin)
- **6 trades** (3 round trips, all winners: bars 72→86, 110→470,
  727→1087), max drawdown **1.09%**
- 2 runs byte-identical action logs (sha256
  `0954e7598ea97cf8e6576d5eb512ca9947dee50afea6a46bded673867f600980`),
  exit code 0, empty stderr, think time 0.10 s of the 1,800 s budget

Sweep: 20,736 configs; every one-parameter neighbour of the chosen
config stays positive (+$5.71…+$24.36) — a plateau, not a knife-edge.
Details: `build-log.md`.

## Files

- `main.py` — the bot (entrypoint)
- `vendor/makefun_bars.py` — byte-for-byte copy of the kit's Python
  SDK shim (excluded from authorship counts per the rules)
- `LICENSE` — MIT (+ SPDX identifier line)
- `top10-analysis.md` — top-10-first analysis of the 0603 sibling race
- `build-log.md` — sweep, validation commands and outputs
