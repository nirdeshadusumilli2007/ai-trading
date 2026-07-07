# ai-trading

This repo drives an autonomous public-disclosure equity-trading routine on Robinhood.

- **PROMPT.md** is the master prompt: the agent's full instructions, signal sources,
  scoring rules, and hard risk limits. When running the trading routine, follow it
  exactly — the hard limits are never negotiable.
- Broker access is via the `robinhood-trading` MCP connector (configured in
  `.mcp.json`; requires one-time interactive `/mcp` authentication by the user).
- `edgar.py` (stdlib-only) fetches new SEC Form 4 open-market insider buys:
  `python -c "import edgar, json; print(json.dumps([edgar.to_dict(b) for b in edgar.fetch_new_insider_buys()]))"`
- State lives in `data/`: `robinhood_positions.json` (position ledger),
  `robinhood_trades.log` (append-only action log), `edgar_seen.json` (Form 4
  filings already reported). In ephemeral/remote sessions, commit and push `data/`
  changes after a trading run — otherwise ledger state is lost with the container.
- Trade only on public information. Never act on material non-public information.
