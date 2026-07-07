# ai-trading — Multi-Signal Public-Disclosure Trading Agent

An autonomous equity-trading routine for Claude Code that acts **only on public
information**: SEC Form 4 insider buys, STOCK Act Congressional trade disclosures, and
already-public news catalysts. It trades a single designated Robinhood cash account
through the official `robinhood-trading` MCP connector, under hard risk limits.

The complete agent behavior lives in **[PROMPT.md](PROMPT.md)** — paste it as the
routine/session prompt. It is self-contained.

## Setup

### 1. Add the Robinhood Trading MCP connector

This repo ships a project-scoped [.mcp.json](.mcp.json), so any Claude Code session
opened in this directory already sees the server. To add it globally instead, run:

```
claude mcp add robinhood-trading --transport http https://agent.robinhood.com/mcp/trading
```

Then enter `/mcp` in Claude Code, select `robinhood-trading`, and authenticate
(one-time interactive OAuth — this must be done by a human).

### 2. Set an EDGAR User-Agent

The SEC requires a descriptive User-Agent with contact info on automated requests:

```
export EDGAR_USER_AGENT="Your Name you@example.com"
```

(In a Claude Code remote environment, set this as an environment variable in the
environment configuration.)

### 3. Run the routine

Start a session in this repo and paste [PROMPT.md](PROMPT.md), or create a scheduled
routine with PROMPT.md as its prompt (e.g., once per market day). The prompt assumes
zero prior context.

## Repository layout

| Path | Purpose |
| --- | --- |
| `PROMPT.md` | The master prompt — the agent's full instructions and hard limits |
| `.mcp.json` | Project-scoped MCP config for the `robinhood-trading` connector |
| `edgar.py` | Stdlib-only SEC EDGAR helper: new Form 4 open-market insider buys ≥ $100k |
| `data/robinhood_positions.json` | Position ledger: ticker, entry_date, planned_hold_days, thesis |
| `data/robinhood_trades.log` | Append-only action log, one timestamped line per action |
| `data/edgar_seen.json` | Runtime state: Form 4 accession numbers already reported |

## EDGAR helper

```
python edgar.py                     # new insider buys ≥ $100k, as JSON
python edgar.py --include-seen      # include filings already seen in prior runs
python -c "import edgar, json; print(json.dumps([edgar.to_dict(b) for b in edgar.fetch_new_insider_buys()]))"
```

Each result includes the insider's role, whether the buy is a pre-planned 10b5-1
purchase (these deserve low conviction), total value, average price, footnotes, and
the filing URL for verification. No third-party dependencies.

## Position ledger schema

`data/robinhood_positions.json` is a JSON array; the agent appends one object per buy:

```json
{
  "ticker": "ABC",
  "entry_date": "2026-07-07",
  "planned_hold_days": 30,
  "avg_buy_price": 12.34,
  "thesis": "CEO bought $450k open-market (Form 4, non-10b5-1)"
}
```

## Hard limits (from PROMPT.md — never violated)

- Public information only. No material non-public information, ever.
- Equities only; the single designated cash account only. No options, no crypto.
- Max 10 positions; 5% of account value per position.
- No sale of a position held < 5 calendar days; −15% stop loss after that;
  60-day maximum hold.

## Disclaimer

This is experimental software that places real-money trades. Equity trading involves
substantial risk of loss, and an autonomous agent can lose money quickly. Nothing in
this repository is financial advice. The account owner bears full responsibility for
all trades placed under this routine.
