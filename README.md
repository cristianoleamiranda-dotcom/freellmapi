FreeLLMAPI v0.12.0 lets ChatGPT and other MCP clients ask the router for answers, adds provider key management to the CLI and first-run setup from a config file, and brings a batch of routing, security and provider fixes.

New
Ask the router over MCP. A new ask_freellmapi tool lets ChatGPT (Developer mode, through OpenAI's secure tunnel) or any MCP client send a prompt through your own fallback chain. It still requires MCP to be switched on and the unified key. (#1302, thanks @tripstar6000)
Provider keys from the terminal. freellmapi keys add | list | remove | test manages provider keys without opening the dashboard. Keys are never printed. (#1276, closes #1226, thanks @yzhkali)
Declarative first-run setup. Self-hosters can create the admin account and activate a Premium license from the startup config, so a fresh server never sits on the setup screen. License keys are validated with freellmapi.co before they are stored. (#1291, thanks @levonk)
Jump to rank. On the Fallback page in manual mode, click a model's rank number and type where it should go instead of dragging it past 100+ rows. (#1324, closes #1317)
Rename a custom chain in place. (#1284, closes #1179)
Direct signup links on the onboarding checklist chips. (#1299, closes #1225)
Routing and failover
Output length that fits. When a client asks for more max_tokens than the chosen model has room for after the prompt, the request is lowered to fit instead of being rejected by the provider. (#1217, thanks @chongjiazhen)
Late in-band errors. A provider that stays silent for most of the retry budget and then errors is benched for five minutes, so later requests stop waiting on it. (#1268, thanks @suantea)
402 in a token count no longer benches a whole provider for 24 hours; ACLIDE errors now fail over. (#1282)
Budget sort no longer reads "40 RPM" as a 40M-token budget. (#1292)
Retry-After from the upstream is passed to the client on embeddings and on image, video, speech and transcription requests. (#1311, #1312)
Security
Login brute-force throttling now covers both paths that were left unthrottled. (#1286)
A reverse proxy on the same host can no longer waive the setup code. (#1287)
Revoking the unified API key now asks for a second confirmation, and the revoked key never flashes on screen. (#1316)
Providers
Speka chat and embeddings. (#1323)
Moondream hosted vision. (#1307)
Septor Labs and CLōD get a User-Agent, and a Cloudflare challenge counts as inconclusive rather than a dead key. (#1301, closes #1298)
A truncated Gemini stream is reported as truncated instead of a clean stop. (#1288)
A failed Gemini or Ollama emulation request no longer exits the process. (#1285)
Dashboard and data
Request history remembers the exact model. Each request now records the model entry that served it, so editing or deleting a custom provider key no longer rewrites which relay old requests are credited to. Existing history is backfilled on upgrade. (#1212, thanks @suantea and @nicyoong)
Response cache hit counts are written in batches instead of once per hit. (#1319, thanks @suantea)
Auth and timeout errors no longer land in "Other" on the error chart. (#1308)
CSV import keeps key labels on a round trip, and no longer drops rows whose quoted label contains a comma or quote. (#1303, #1290)
The CLI says "needs Node 20" instead of crashing on older Node. (#1295, closes #1283)
Updating
Download the installer for your platform below, or use ghcr.io/tashfeenahmed/freellmapi:v0.12.0 for Docker. The latest Docker tag also points to this release. Desktop users on v0.11.1 will see this update in the Updates panel.

Existing keys and profiles are retained. This release has one database migration: it adds a model reference to request history and backfills it on first start. Back up your data before updating a self-hosted instance.

Thanks also to everyone newly added to the contributors list in the README (#1325).

Full changelog

⭐ Like the free router? Go Premium, the live signed catalog, $19/yr, cancel anytime.