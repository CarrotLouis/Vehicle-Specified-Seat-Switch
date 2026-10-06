# Review of DeepSeek six-vehicle matrix — 2026-09-30

Raw MD/JSON preserved with source paths, lengths and SHA256 in manifest.json. Not merged into implementation.

Accepted as reference: seat order/default keys/role and restore arrays agree with primary profile/policy; vehicle-specific local branches agree with native.lua. Tanker lacks a direct pose profile; this does not imply normal tanker switching fails (native next/previous path is separate). Offline receiver matrix excludes tanker and stubs action dispatch.

Corrections / not established:
- Existence of next/previous/route functions does not prove connectivity for all vehicles/seats. The report calls five named functions “six”, another reason not to import prose as structured authority.
- Primary frozen 0.10.1 VehicleSeatSwitch.log lines7–12 already contain all six seat_adjacency arrays. Missing extraction is not missing source data. Requested DS follow-up to decode row sizes and -1 terminators, distinguish adjacency / graph reachability / actual next-previous selection.
- Restore action value0 cannot be declared “no action” from profile.lua alone. Require native dispatch evidence. Nonzero tanker driver restore is a difference, not itself a defect.
- Different cleanup branches are not evidence of missing required steps. Keep speculative tank rotation/preparation concerns as unverified.
- 0.10.1 success applies to two-player guest M102 front passenger/gunner with unmodded friend host/driver, based on user report plus primary frozen log. No all-vehicle/host/3–4-player claim.

Manual follow-up request: outputs/DeepSeek-辅助任务-原生路由交叉核对.txt. No DSH control or prompt sent this turn.
