# Review of DS network guard inventory

Raw report preserved with source/hash manifest. Useful index of two-player, peer, driver, role and host restrictions in0102. Not a change specification; conditions were re-read in primary source before0104.

Important corrections:
- observe.lua:send is the authority transfer/request sender, NOT seat snapshot/transition synchronization. destination and target there are peer identities, not destination seats or “seat-related endpoints”. sender.lua is the separate seat notification sender.
- eligible is reused when confirming seat after return; it is NOT a prerequisite to sending cleanup return. adapter:return_owned and observe:send(requesting=false) intentionally skip two-player/host/source-seat restrictions. Third-person joins, focus loss or missing local seat must not strand a borrowed chassis merely because new-operation admission fails.
- Local avatar ownership, vehicle ownership, driver peer and coordinator are separate identities. New0104 records original chassis owner separately from notification destination. Do not direct local-authority seat notifications back to self just because original owner is self.
- Host identity/peer membership getter validation remains; only the guest-only policy is relaxed.0104 additionally refuses coordinator changes before a new request/mutation while allowing safe original-owner return.
- Old “integrated” source has narrow passenger route; it does not establish host coverage.0103 has now passed M104 guest1↔2 runtime; the inventory's pending note reflects older context.

Result:0104 has two explicit paths (already local / borrowed then returned), retains old borrowed cleanup tests, adds host×owner matrix and zero-transfer tests for already-local authority. Runtime host behavior remains pending.
