# 0.9.1: the probe now reports its own failure

## What 0.9.0's log showed

The user's 0.9.0 run produced **no `probe_layout` line at all** - but the same log contains an `integrated_state` whose detail carries `"local_ready":true`. That detail is built from `s~=nil`, so a native snapshot **did** exist, which means the probe **ran and threw**, and the `pcall` I wrapped it in swallowed it. The defect was mine: I added a `pcall` for safety without surfacing the failure, so the run produced silence instead of information.

## The fix

`adapter.lua`:

- emits `probe_layout_begin` **before any read**, so "never ran" and "ran and failed" are distinguishable;
- every memory read goes through `rd()`, which absorbs a throw and returns nil, so one bad address cannot abort the dump;
- every candidate goes through `safe_one()`, so a failing candidate records `{error=...}` without hiding the others;
- the outer call site records `probe_layout_error` with the message if `probe_layout` still throws.

`test_layout_probe.lua` gained the matching assertions: the begin event is emitted, no outer error occurs in the healthy case, and - the class of failure that cost us a round - **a throwing read must still produce a `probe_layout` result** rather than disappearing into the outer pcall.

## Incident this round (must not repeat)

To fix one line in `build.py` I used a `Get-Content -Raw | Set-Content -NoNewline` round-trip. That **re-encoded the file** and mangled its metadata strings: the `'Name'` value lost its closing quote and `build.py` stopped parsing entirely. Recovery: read the pristine copy from the **user's project directory** (read-only, never modified) and re-apply the 0.9.x edits, with the description written as **ASCII only** so no round-trip can ever corrupt it again. `build.py` now parses and carries `RELEASE='0.9.1'`, the 0.9.1 destination assert and the probe test wiring.

Lesson: never rewrite a UTF-8 source file through a `pwsh` `Get-Content`/`Set-Content` pipeline. Use the edit/write tools, which preserve the encoding.

## Artifact and verification

outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.9.1.zip bytes 378863 SHA256 e70b7396a48191499096cbcd1f412c1316fb52b20433cd2a776460ba3e4efb5f; helper sha unchanged 6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3. Full offline suite PASS on both preserved captures. Arsenal coexistence fixture manager-fixture-3b10d139-4e11-4c9c-88d2-0e1e0bc9451a/result.json: 4/4 variant-order combinations with exact payloads, purge_empty true, live_profile_changed false, game_launched false.

## The user's next run

Identical to 0.9.0 and still solo, two minutes: replace all diagnostics with 0.9.1, keep gameplay 0.2.4 **Normal**, start a mission, board an M-102, wait 3-5 seconds, exit. This time **every** outcome carries information - `probe_layout` (data), `probe_layout_error` (reason), or only `probe_layout_begin` (all reads failed).

## Judgement unchanged

Exactly one candidate whose layout matches -> evidence for calling `owner_enter` directly, and the crash risk is confirmed with the user before anything is built. None matching -> the context is constructed another way, and the route moves to locating the engine's own seat-change entry point rather than guessing a pointer. 0.8.4 must not be run again.
