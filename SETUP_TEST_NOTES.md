# Setup test: notes (continue on the MacBook)

Date: 2026-10-09. Nothing was installed and no video was edited. These are read-only check results from the Linux cloud container, not from the laptop.

## Container check results (for reference only)

| Item | Status |
|---|---|
| ffmpeg | OK 6.1.1 |
| Python 3 | OK 3.13.16 |
| Node.js | OK v22.22.0 |
| Playwright (Node) | OK 1.56.1, Chromium present |
| faster-whisper | missing |
| Text-to-speech | missing (no say/espeak) |
| IBM Plex Sans Arabic | missing (no ./fonts/) |
| ./.env | does not exist, so step 8 (ElevenLabs) is skipped |

Resources in the container: 4 cores, 15 GB RAM, no GPU, 30 GB free disk. 4K rendering is possible but slow there.

## Plan to run on the Mac

Rerun the same 10 steps on the MacBook. Differences from the container:
- TTS: use the built-in `say` (e.g. `say -o out/test_voice.aiff "Testing Claude Code one two three"`, then convert to wav with ffmpeg).
- Installs to ask approval for, one line each, before running: ffmpeg (brew), faster-whisper (pip, in a local venv, small model ~500 MB), Playwright + Chromium (npm), IBM Plex Sans Arabic .ttf into ./fonts/.
- Step 8 only if ./.env exists. Never print the key.
- Do not report any check as passed unless it was actually run (including the two-render pixel-identical determinism check and the font-loaded-before-frame-0 check).
- End with "Ready for editing ✅" only if everything passed, and report disk space used by the tools.
