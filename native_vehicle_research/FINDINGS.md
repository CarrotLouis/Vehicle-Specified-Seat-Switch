# Native vehicle investigation

This subtask performed read-only static inspection of the user's existing game installation and public source. It did not launch the game, load native game code, attach to a process, or modify the installation.

## Verified local evidence

The source image is `F:/SteamLibrary/steamapps/common/Helldivers 2/data/game/game.dll`:

- File size: 15,582,312 bytes.
- SHA-256: `cc75948d90fdfde259dcb519e9933db7ffa3ccb281ce4fb89e6b1b011557470c`.
- PE machine: AMD64; preferred image base: `0x180000000`; image size: `0x3a6b000`.
- Entry RVA `0x3554058` belongs to `.boot`.
- Original first executable section has virtual size `0x1e5d3d3` but raw size `0x83c600`; original sections have blank names. `.vm_sec`, `.winlice`, and `.boot` are present.
- The only named PE export is `get_plugin_api`.
- No ASCII string of length at least 6 containing vehicle, seat, passenger, occupant, or SwitchSeat was found in the on-disk image.

These findings strongly indicate a protected/packed disk image rather than ordinary directly disassemblable original game code. They do not prove that static recovery is impossible. They do mean that simply mapping the published runtime RVAs to file offsets is insufficient to identify the original implementation.

The exact section metadata and entropy values are in `pe_evidence.json`. `inspect_pe.py` reproduces the evidence using only Python's standard library.

## Public source evidence

`work/VanillaPlusMegapack/components/ControllableHoverPack/src/hover_data.lua` contains build-specific runtime pointers for the local avatar and equipment. It provides useful patterns for identity guards, bounded map lookups, and rejecting inconsistent snapshots. It does not expose a vehicle seat manager, occupancy array, target-seat transition API, or authority request ABI.

`work/BingusSharedLoader/docs/TECHNICAL.md` describes startup/module discovery and log support. Loader API 1 is not a gameplay vehicle API. A listed optional module name `vehicle_stability` is not evidence of a seat-switching interface.

The public searches performed on September 21, 2026 found ordinary cycling key `SwitchSeatNext` discussed by players, but no verifiable primary source with a native direct-target seat operation. A cycling binding alone cannot implement idempotent F1/F2/F3 seat selection and cannot certify the requested occupancy behavior.

## Unverified requirements

No offset or native function signature was established for any of the following:

1. Local player's current vehicle and seat association.
2. Exact dynamic occupant/reservation state for all seats.
3. Native request to move into a specified seat.
4. Host/client authority and synchronized rejection when another teammate occupies or simultaneously claims the target.

Do not substitute guessed memory writes or an invented Lua vehicle API. Configuration, policy tests, and a manager-compatible ZIP cannot validate these missing runtime operations. A current-build unpacked image or live read-only observations plus controlled in-game tests would be needed to establish them.
