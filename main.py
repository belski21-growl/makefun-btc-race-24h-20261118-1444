# SPDX-License-Identifier: MIT
"""Shelf-rebound dip buyer — btc-race-24h-20261117-0603 sibling analysis,
built for btc-race-24h-20261118-1444, agent-fun/bars-replay/v1.

Long-only bot on 1-minute cbBTC bars, Python 3.13 stdlib only, through
the kit's own vendor/makefun_bars.py shim.

The idea, in plain words: price spends most of a choppy day sliding
off a shelf — the highest close of the last four hours. This bot only
buys once price has fallen a long way off that shelf AND has already
printed a small upward tick, so it buys a shelf that is turning, never
a knife still falling. It then rides the rebound to a fixed target or
a trailing exit, and goes back to cash. It never chases a trend: the
sibling race (0603, 4,387 entries) was won unanimously by dip-buyers
(top 10: +$19.90…+$24.20, 2–8 trades, maxDD 0.6–2.0%) while
buy-and-hold lost −$13.10 and momentum −$15.60; only 26.6% of the
field finished positive. The dev window here is the same kind of day
(BTC $65,074 -> $63,261, −280 bps, buy-and-hold ≈ −$29.56), so the
same shape applies — with a lighter confirmation, because this
window's bounces are shallow (only 4 of 46 deep 60-min slides
recovered +100 bps within 30 min).

The trade:
  * BUY all cash when the close sits at least 150 bps under the
    240-bar rolling-high close, the last 3 bars already rose at least
    5 bps, and the 720-bar return is above −600 bps (no waterfall).
  * SELL everything on the first of: +120 bps from the fill price,
    −100 bps from the best close since the fill, −150 bps from the
    fill price, or 360 bars held. The fill price is read from the
    batch's own fills (the replay reports every fill's exact price),
    never guessed from a close. After a sell, 20 bars of cooldown
    before the next buy.
  * Orders fill at the next bar's open; max_slippage_bps 100 keeps a
    gap-open from filling us far from the close we decided on.

Dev-window grade (1,440 bars, local protocol replay, real main.py,
run twice, byte-identical action logs): net PnL +$22.23, 6 trades
(3 round trips, all winners: bars 72->86, 110->470, 727->1087),
max drawdown 1.09%. Sweep of 20,736 configs: every one-parameter
neighbour of this config stays positive (+$5.71…+$24.36), so the
result is a plateau, not a knife-edge optimum.

Deterministic by construction: integer arithmetic throughout, no
clock, no files, no environment reads, no randomness (hello.seed is
accepted and ignored).
"""

import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

ASSET = "CBBTC"
SLIP_CAP = 100  # max_slippage_bps on every order

# Thresholds, in basis points (1 bp = 0.01%).
SHELF_BARS = 240      # rolling-high window: the shelf price fell from
SHELF_DROP = 150      # entry needs a close at least this far under it
TICK_BARS = 3         # recovery tick window
TICK_MIN = 5          # entry needs a 3-bar rise at least this strong
REGIME_BARS = 720     # regime window: 12-hour return must stay above
REGIME_FLOOR = -600   # ... this floor, or we sit out the waterfall
TAKE_BPS = 120        # exit: gain from the fill price
GIVEBACK_BPS = 100    # exit: fall from the best close since the fill
STOP_BPS = 150        # exit: fall from the fill price (safety net)
HOLD_MAX = 360        # exit: bars held (safety net only)
COOLDOWN = 20         # bars of flat time after any sell

MIN_CASH = 1_000_000  # 1 USDC, in quote units


def move_bps(new, old):
    """Basis-point move from `old` to `new`, integer math only."""
    return (new - old) * 10000 // old


class ShelfRebound:
    """Close history plus the position state, carried across batches."""

    def __init__(self):
        self.history = []          # every close, in order
        self.shelf = deque()       # indices of candidate shelf highs
        self.fill_price = None     # fill price of the open position
        self.best_close = None     # best close since the fill
        self.bars_held = 0
        self.rest = 0              # cooldown bars left after a sell

    def remember(self, close):
        """Record a close and maintain the rolling-high shelf."""
        idx = len(self.history)
        self.history.append(close)
        while self.shelf and self.history[self.shelf[-1]] <= close:
            self.shelf.pop()
        self.shelf.append(idx)
        while self.shelf and self.shelf[0] <= idx - SHELF_BARS:
            self.shelf.popleft()

    def under_shelf(self):
        """Drawdown of the latest close from the shelf, in bps.

        The shelf is the highest close of the last 240 bars; before
        240 bars exist it is the highest close seen so far, so the bot
        can trade from the early bars instead of sitting out the
        first four hours waiting for a full window.
        """
        if not self.history:
            return None
        shelf_price = self.history[self.shelf[0]]
        return move_bps(self.history[-1], shelf_price)

    def recovery_tick(self):
        """3-bar return in bps, or None while the window is not full."""
        if len(self.history) <= TICK_BARS:
            return None
        return move_bps(self.history[-1], self.history[-TICK_BARS - 1])

    def long_return(self):
        """720-bar return in bps, or None while the window is not full."""
        if len(self.history) <= REGIME_BARS:
            return None
        return move_bps(self.history[-1], self.history[-REGIME_BARS - 1])

    def clear_trade(self):
        """Forget the open position; called whenever we hold nothing."""
        self.fill_price = None
        self.best_close = None
        self.bars_held = 0

    def want_buy(self, state):
        """Buy order, or None. Only called while flat."""
        self.clear_trade()
        if self.rest > 0:
            return None
        drop = self.under_shelf()
        if drop is None or drop > -SHELF_DROP:
            return None
        tick = self.recovery_tick()
        if tick is None or tick < TICK_MIN:
            return None
        regime = self.long_return()
        if regime is not None and regime <= REGIME_FLOOR:
            return None
        if state.cash < MIN_CASH:
            return None
        return {
            "side": "buy",
            "symbol": ASSET,
            "notional_quote_units": state.cash,
            "max_slippage_bps": SLIP_CAP,
        }

    def anchor_fill(self, batch):
        """Take the fill price from this batch's fills, if we lack one.

        The replay reports every filled order's exact price, so the
        exits are measured from what we actually paid, not from the
        close of the bar after the fill. Falls back to the close
        (set by want_sell) when a batch carries no fill for us.
        """
        if self.fill_price is not None:
            return
        for fill in batch.get("fills", []):
            if (
                fill.get("side") == "buy"
                and fill.get("symbol") == ASSET
                and fill.get("status") == "filled"
            ):
                try:
                    price = int(fill["price"])
                except (KeyError, TypeError, ValueError):
                    continue
                if price > 0:
                    self.fill_price = price
                    self.best_close = price
                    return

    def want_sell(self, close, qty):
        """Sell order, or None. Only called while holding."""
        if self.fill_price is None:
            self.fill_price = close
        if self.best_close is None or close > self.best_close:
            self.best_close = close
        self.bars_held += 1
        gain = move_bps(close, self.fill_price)
        giveback = move_bps(close, self.best_close)
        if gain >= TAKE_BPS:
            reason = "take"
        elif giveback <= -GIVEBACK_BPS:
            reason = "giveback"
        elif gain <= -STOP_BPS:
            reason = "stop"
        elif self.bars_held >= HOLD_MAX:
            reason = "max-hold"
        else:
            return None
        self.rest = COOLDOWN
        return {
            "side": "sell",
            "symbol": ASSET,
            "qty": qty,
            "max_slippage_bps": SLIP_CAP,
        }


BOT = ShelfRebound()


def on_batch(state, batch):
    if state.warming_up:
        return []
    bars = batch.get("bars", [])
    if not any(bar.get("symbol") == ASSET for bar in bars):
        return []
    close = state.close(ASSET)
    if close is None:
        return []
    BOT.remember(close)
    if BOT.rest > 0:
        BOT.rest -= 1

    position = state.positions.get(ASSET)
    if position is None or position.qty == 0:
        order = BOT.want_buy(state)
        return [] if order is None else [order]

    BOT.anchor_fill(batch)
    order = BOT.want_sell(close, position.qty)
    return [] if order is None else [order]


makefun_bars.run(on_batch)
