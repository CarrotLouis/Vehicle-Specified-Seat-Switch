# Current architecture

## Runtime and inputs

`src/entry.lua` composes one resident Enhanced controller and the existing multiplayer dispatcher. `mode_policy.lua` restricts seat pairs when Normal is selected; switching modes does not reload native interfaces. `input_source.lua` selects either independent INI keys or five native menu actions. It resets held-key edges on source/focus/member changes and cancels unsent intents. Issued transactions finish before settings change.

`menu.lua` uses public registration/get APIs. ModOptionsMenu is required. Without optional ModBindingsMenu, strategy remains INI and no strategy choice is registered. Labels consult current applied settings directly. `bingus_text.lua` stays byte-identical to upstream; `i18n.lua` resolves actual missing regional codes locally. `menu_locales.lua` is generated from authored strings.

## Seat transactions and recovery

The retained core validates the avatar, vehicle, seat occupancy/reservations, ownership and native interface contracts. Owned switches use `owned_transaction.lua`; remote-owned vehicles use the reservation/probe/dispatcher routes. Receive-only helper sources live in `native/`. Release builds disable continuous packet recording. Unknown Enhanced contracts retain a separately checked Normal fallback.

Tank-driver exit uses `steering_reset.lua`. An owned seated driver may already have its active flag cleared; the native exit remains idempotent. Both valid starting states are accepted while identity/ownership checks and neutral-steering postconditions remain enforced. It does not alter vehicle velocity or another player's input.

`solo_native.lua` catches read-only preparation refusal and returns it to the controller without disabling future requests. Errors after mutation may indicate incomplete state and are not treated as harmless. Entry isolates menu service from gameplay service; an unexpected Enhanced fault drains input intents, stops the Enhanced transport and keeps guarded Normal actions and menu changes available until restart. It does not automatically resume a possibly incomplete Enhanced transaction.

## Optional performance shortcut filter

`performance_data.lua` uses the native Keyboard closure's device pointer and validates two small lookup-function bodies plus dictionary bounds, public key IDs and writable non-executable rows. It edits only four numeric values in the name dictionary for F2–F5. Existing native action maps retain their separately cached numeric IDs. Opening a native modal menu, losing input focus, disabling the option or shutting down restores the original values with compare-before-write guards.

The new saved option ID is `block_perf_data`, default false. Old `block_perf=true` cannot opt users into it. OFF performs no lookup or memory inspection; ON follows four bounded dictionary chains at activation and never scans the process or repeatedly edits the map. Unknown pointers/layouts leave this feature unavailable while seat controls remain usable. Restore failures preserve foreign changes and request a restart in the log. Real native binding and anti-cheat outcomes still need live verification; the cached-action test is an explicit fixture model.

The earlier `performance.lua`/`code_byte.lua` executable-instruction approach remains only in historical archives and is absent from this package.

## Building and historical records

Current build and checks use `scripts/`; output goes to ignored `build/` and the sibling `outputs/`. `research/archive/` retains original experiments and accepted baselines; `docs/history/` retains their dated notes. Those notes preserve old paths so their timeline is not silently rewritten. Downloaded tools/dependencies and private captures stay in ignored `vendor/`/`local_data/`, and are never shipped or pushed.

## Current read-only menu probe

menu_probe.lua/menu_probe_entry.lua are a separate one-shot diagnostic, not part of the formal runtime. It has an independent resource/GUID and delegates to the previous update/shutdown callbacks. It compares the profiler registry with the Lua keyboard device and records only bounded keyboard metadata and this mod's native action records. It declares read/query APIs only. See STATUS for the outstanding performance-filter evidence.
