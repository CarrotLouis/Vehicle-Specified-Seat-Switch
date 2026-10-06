# Project instructions from the user

- This `work` directory is the Git repository root. Remote: `https://github.com/CarrotLouis/Vehicle-Specified-Seat-Switch.git` (public).
- At the end of each conversation that produces new source, tests or documentation, commit and push the finished work once. The user has authorized this recurring workflow. Do not create GitHub Releases; the user handles releases.
- Do not sync the sibling `outputs` directory, nested outputs, local authentication files, raw game modules/assets, captures/logs, downloaded tool binaries, dependencies or generated packages. Keep the curated `.gitignore` in force. Review staged filenames before pushing.
- Use the existing signed-in GitHub CLI/config through `github_sync.py` where available; never print or commit credentials. Ask the user when authentication or an unresolved repository issue needs their input.
- Preserve published versions and accepted research baselines. Current active menu integration: `seat_release_041`. Read `STATE_MENU_REVISION_20261007.md` and `TASK_STATE.md` before continuing. 0.4.0 has a GameGuard forced-exit report after its profiler instruction patch was enabled; do not re-enable that feature. 0.4.1 removes it and uses resident Enhanced with Lua-only Normal restrictions. Live retest is pending.
- Do not send more work to DeepSeek. The user ended that delegation.
- Only the installing player may need the enhanced mod; host/guest and unmodded teammates remain supported. Stay aboard, honor occupied/reserved seats and retain movement/pose/driver cleanup.
- Minimize runtime work. No periodic whole-process scans or diagnostic recording in releases. Unknown interfaces refuse the affected feature.
- Distinguish offline checks and user-reported live results. Four-player live validation and the new 0.4.0 menu/HUD features are not yet live-confirmed.
