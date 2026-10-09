# 0.4.5 checkpoint — 2026-10-10

## Request and scope

User requested non-modifier chords such as MOUSE4+W/S/A/D/F. During implementation the user explicitly narrowed scope to recognition only: gameplay input conflicts are the user's responsibility. Do not add prefix suppression, gameplay quiet-check exemptions or special driver-key cleanup for these chords.

src/config.lua now interns free chords in a descriptor table. The low 16 bits preserve legacy primary/modifier encoding, the upper 16 bits identify the canonical ordinary-key prerequisite set. All existing supported keyboard/mouse names can be ordinary prerequisites; final key is the down-edge trigger. Preceding order and aliases normalize; case/whitespace insensitive. No five-key limit (bounded 255 tokens, sufficient for the supported unique names). Repeated keys and duplicate modifier groups remain invalid; WIN is prefix-only, Fn/wheel/firmware-only inputs remain unsupported. Extra modifier groups do not match; unrelated ordinary keys are allowed. Exact duplicate bindings still restore vehicle defaults; free chords are not rejected merely for overlap, but simultaneous seat triggers are refused. Legacy modifier-only overlap checks remain.

api.chords connects parsed descriptors to the actual poller and native gate. Only configured keys plus existing modifier groups are polled. No process-memory scan, background capture or new file category is added. Configuration defaults remain F1-F5 and existing user INIs remain untouched. This extension is for INI only; ModBindingsMenu scope is unchanged.

## Native integration

Input helper ABI3 passes held_count + held[255] in each of at most five armed items. The native matcher validates ordinary prerequisites at message time, preserving 40-byte record IDs, source/generation/expiry checks and existing primary-key suppression. Prefix messages are forwarded untouched. Existing multiplayer release/quiet/occupancy/authority guards are unchanged; recognized chords can therefore wait for conflicting held gameplay controls to be released. Solo gameplay path and physics/seat transactions are unchanged.

Input DLL: 11264 bytes, SHA-256 319aaaa11c5a7221da05c9779ffea1e6098a140cb8711caf05c6555bb0924cbd; imports Kernel32/MSVCRT/User32, entry point zero, unsigned. Exact rebuild verification passes. Transport unchanged: 16245 bytes, SHA-256 7c533e1b812b0be2cf58e418ac397d5025b3b71ebea8d41530a53a830534437f. Cache/loading guarantees from 0.4.4 remain. Updating creates one new input-helper cache filename; old files are not automatically deleted.

## Packaging and evidence

Per the preceding source-folder discussion, formal ZIP omits Source/. Public source, tests and build scripts remain on GitHub. Keep visible Native/, SECURITY.md, SHA256SUMS.txt and NATIVE_HELPERS.json with repository provenance. No changelog/history or validation caveats in player introductions. User manages Releases. Prior published ZIPs untouched; an undelivered 0.4.5 candidate was preserved under build/superseded before correcting its static-import disclosure.

37 offline groups pass. Includes all five requested bindings, normalized aliases/order, final-modifier/long-chord matching, focus/hold/release protection, exact bundled entry wiring, native gate descriptors/lifecycle, and real compiled hidden-window plus separate GUI-thread tests. Native game/physics/network effects remain declared test doubles. New native helper cache loads/ABIs verified outside game. Isolated Arsenal 0.36.2 import/deploy/purge passes, exactly three payload files, no live profile change. New key behavior still needs user in-game confirmation; no game launched.

ZIP outputs/Vehicle-Specified-Seat-Switch-0.4.5.zip
Bytes 233439
SHA-256 65342c8d874718dc703edfdcc37c4a1311d7ec776f00b1e4212f7fa2405945c5
Lua SHA-256 3446dbacec9835ed7ff64bd7f981506ab04c3797732684f02df51c4f3e85c0f9

## Pending unrelated issues

Reported 0.4.3 Bastion-only failure: `Bastion overlay state count changed` in pose.lua:74, expected layer8 count332 from tank_spec.lua. Guard refuses before mutation; other vehicles work. Actual remote count/resource unavailable. Asked for user game version/mod list and minimal-dependency reproduction; no fix claimed or implemented. Upgrading 0.4.4/0.4.5 does not fix that guard.

Earlier exact live boundaries: performance-data filter and Unicode loader integration still lack explicit live confirmation; four-player-specific validation remains unreported. Keep these separate from offline evidence. Do not request extra multiplayer gatherings merely to check parsing. Native caches may leave temporary .tmp files if interrupted during creation; no automatic old-cache deletion. No DeepSeek/delegation.
