# Daily pre-plan — for the next trading session (Monday 2026-07-13)

Written 2026-07-11 (Saturday) per Step 5B. Every item below is a hypothesis to
re-verify with fresh data at the start of the run (Step 0B) — nothing here is a
pre-authorized order.

## 1. Held positions — exit review first (Step 1)

| Ticker | Entry | Days held Mon | Target / Stop | Monday action to check |
|---|---|---|---|---|
| NVDA | 2026-07-08 @ $197.33 | 5 of 5 | — / −15% | **PLANNED HOLD EXPIRES: days held ≥ planned_hold_days (5) → SELL due per Step 1** unless fresh research finds a concrete reason it was extended. Last seen $210.48 (+6.7%). |
| ALMS | 2026-07-08 @ $29.82 | 5 of 15 | $34.70 / $27.40 | Stop nearly hit Friday (intraday low $27.45 vs stop $27.40) on below-average volume. Check fresh price FIRST — if ≤ $27.40, sell. Also place/maintain the GTC limit sell at $34.70 (standing-target rule, position > 1 day old). |
| SMFG | 2026-07-10 @ $25.80 | 3 of 18 | $30.35 / $23.50 | Now ≥ 1 day old → place the standing GTC limit sell at $30.35. Watch for the pending 2-for-1 split (adjust ledger + orders if it executes). Earnings 7/31 — hold plan clears before. |
| SPY (sweep) | lots 7/08 + 7/10 | exempt | — | Both lots past min hold as of 7/11 → fully available to fund qualified buys. Never sweep new cash into SPY before the same-session A+B scans (standing rule). |

Options: `options_cash_allocation` = $20.00. Check `option_level` on account
953941390 at run start; if still unapproved, log and skip Step 3C.

## 2. Watchlist — triggers to re-test (Step 0B → Step 3B)

- **SKHY** (SK Hynix ADR — ticker changes from when-issued SKHYV to SKHY at
  regular-way open Mon 7/13; day-1 close $168.01, +13% vs $149 pricing):
  DO NOT chase the IPO pop. Buyable only via (a) a multi-day base then a
  volume-confirmed closing breakout, or (b) a pullback toward the Seoul-parity
  zone (~$149–155) that holds and turns. Fundamentals are elite (56.4% HBM
  share, first to HBM4, ~5.5× fwd P/E vs MU ~6.7×) — the wait is about entry
  structure, not quality. Re-score each cycle once indicators exist.
- **SOFI** ($18.80): trigger = confirmed CLOSE > $19.20 on ≥ 1.5× volume.
  Caveats: below 200-SMA ($22.08) so B1 still fails until reclaimed; ADX 25.3
  borderline; Friday printed a shooting-star candle. Earnings **7/29** — no
  fresh entry 7/27–7/29. Catalysts on file: Goldman PT $21, small-business
  loans launch, Composer acquisition, SpaceX-IPO retail distribution mention.
- **ONDS** ($7.28): downtrend — trigger = reclaim of the $9.40–9.50 SMA cluster
  on expanding volume with ADX ≥ 25. Catalysts on file: $875M DZYNE
  acquisition, 2026 revenue target raised $390M→$525M, Lockheed/Sentrycs
  integration, analyst PT $10→$16. Story strong, chart broken — no early entry.
- **CIFR** ($22.10): AI-datacenter landlord, $11.4B contracted leases (AWS +
  Fluidstack/Google), ~27% off June high. Trigger = B-qualifying closing
  breakout back above ~$23.50–24 on volume, or a tested base above $20.
  Risks: Fluidstack Sept-2026 completion deadline (180-day termination right),
  $5.2B debt, revenue ramp only from late 2026.
- **MU** (~10/15 borderline Friday): re-check reaction now that the SK Hynix
  listing has settled; still needs a real breakout + volume expansion.
- **U** (Unity, $31.43): above 20/50/100-day MAs; trigger = close above the
  200-day SMA (~2.3% overhead Friday), which clears the B1 dual-SMA fail.

## 3. Scheduled events gating entries (Step B5)

- Check Monday's macro calendar at run start (CPI/FOMC/jobs — verify this
  week's dates before any fresh B entry).
- Earnings: SOFI 7/29, SMFG 7/31, NVDA 8/26.

## 4. Carry-over notes

- Market regime check (B11: SPX/NASDAQ above 20-day MAs) required before any
  Strategy B buy.
- Fresh EDGAR Form 4 + Congress PTR sweep still required every run (Step 2) —
  the watchlist above supplements, never replaces, the daily A-scan.
- Commit `data/` after the run (ephemeral-session rule).
