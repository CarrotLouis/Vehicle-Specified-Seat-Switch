# Release documentation and artwork complete

User selected official name: Vehicle Specified Seat Switch.
User accepted FRV weapon fix; tank persistent steering remains and is explicitly deferred.
This turn updated package metadata and documentation only. No live INI/game/profile edits.
Latest user superseded detailed INI help: keep short existing template, full bilingual guides in ZIP.

Deliverables:
- outputs/Vehicle-Specified-Seat-Switch-0.2.3.zip (Arsenal installation)
- outputs/Vehicle-Specified-Seat-Switch-0.2.3-Publishing-Kit.zip (Nexus text, six PNGs, prompts)
- Unpacked publishing kit: outputs/Vehicle-Specified-Seat-Switch-0.2.3-Publishing

Installation ZIP SHA256 f4202df7229f6a91efb4ab8d3d041130d786aacb0078ba9dcc6b75ad42814f9e
Publishing ZIP SHA256 740f3185dbba9b9523968e160d343fe25c39f742fb197a1c016bdc6e2442d0b2

Built by work/seat_switch/package_release.py using existing Vehicle-Specified-Seat-Switch-0.2.3-test.zip.
All Normal/Enhanced game archives, bundled source and INI example are byte-identical to tested package.
Only manifest, README, key guides and NOTICE changed. Internal source still carries historical diagnostic version 0.2.3-test intentionally to preserve payload; public names and descriptions are release 0.2.3.
Manifest main description and both variant descriptions are bilingual.
Enhanced cross-group switching ONLY solo with local vehicle control; multiplayer retains Normal restrictions.
Known tank steering issue disclosed; workaround release steering first, re-enter driver and operate if stuck.

Arsenal 0.36.2 actual backend fixture import Normal -> Enhanced -> Normal -> purge PASS.
No live profile changes or game launch. Result copied into publication folder.

Nexus Chinese/English descriptions in plain text and BBCode, submission fields in publishing kit.
Reviewed official Nexus author best practices and Sep4 2026 submission guidelines.
AI-Generated Content and AI Media tags identified in submission notes. No external publication performed.

Images generated using built-in image_gen skill. Five schematic PNGs 1254x1254 plus cover 1672x941.
Inspected labels and background; corrected tanker transparency and removed inaccurate extra tank title.
All final images copied into workspace, file CRC validated. Prompts persisted in kit.
Images are schematics, not game screenshots or in-game HUD additions; noted in both languages.

prepare_publication.py creates documents; finalize_publication.py packages artwork/documents.
Gameplay fixes and enhanced multiplayer research remain out of scope until user requests.
