#!/usr/bin/env bash
# Full rebuild of the reel. Needs: input/voice.m4a (the original recording, never committed), ffmpeg, node + playwright.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p fonts sfx out input

# fonts (IBM Plex, OFL) — fetched, not committed
F=https://cdn.jsdelivr.net/npm/@fontsource
[ -f fonts/plex-ar-400.woff2 ]    || curl -sSfL -o fonts/plex-ar-400.woff2    $F/ibm-plex-sans-arabic@5.0.20/files/ibm-plex-sans-arabic-arabic-400-normal.woff2
[ -f fonts/plex-ar-700.woff2 ]    || curl -sSfL -o fonts/plex-ar-700.woff2    $F/ibm-plex-sans-arabic@5.0.20/files/ibm-plex-sans-arabic-arabic-700-normal.woff2
[ -f fonts/plex-latin-700.woff2 ] || curl -sSfL -o fonts/plex-latin-700.woff2 $F/ibm-plex-sans@5.0.20/files/ibm-plex-sans-latin-700-normal.woff2

# leveled copy of the voice (-16 LUFS, -1.5 dBTP); the original stays untouched
ffmpeg -v error -y -i input/voice.m4a -af "highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -c:a pcm_s24le input/voice_leveled.wav

# original SFX, synthesized from noise
ffmpeg -v error -y -f lavfi -i "anoisesrc=d=0.03:c=white:r=48000:a=0.9" -af "highpass=f=1800,lowpass=f=7000,afade=t=out:st=0.004:d=0.026,volume=-14dB" sfx/click.wav
ffmpeg -v error -y -f lavfi -i "anoisesrc=d=0.6:c=pink:r=48000:a=0.8" -af "bandpass=f=900:w=1400,afade=t=in:d=0.35:curve=qsin,afade=t=out:st=0.35:d=0.25,volume=-20dB" sfx/whoosh.wav

# timeline.json / edit.json are committed; re-run prep.py only after re-transcribing (needs input/words.json)
[ -f input/words.json ] && python3 -I prep.py > /dev/null

N=$(python3 -I mix.py)
rm -rf frames
Q=$(( (N + 3) / 4 ))
for i in 0 1 2 3; do node render.mjs $((i * Q)) $(( (i + 1) * Q < N ? (i + 1) * Q : N )) frames & done; wait
ffmpeg -v error -y -framerate 30 -i frames/f%05d.jpg -i out/tight_audio.wav -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -ac 2 -movflags +faststart out/TVReel.mp4
echo "done: out/TVReel.mp4 ($N frames)"
