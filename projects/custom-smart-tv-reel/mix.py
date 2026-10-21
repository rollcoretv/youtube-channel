"""Cuts the long pauses out of the leveled voice (per edit.json) and lays the subtle SFX on top."""
import json, subprocess

E = json.load(open('edit.json')); end = E['end']
parts, labels = [], []
for i, (a, b) in enumerate(E['keep']):
    fo = max(0, b - a - 0.008)
    parts.append(f"[0]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={fo:.3f}:d=0.008[s{i}]")
    labels.append(f"[s{i}]")
fc = ";".join(parts) + f";{''.join(labels)}concat=n={len(labels)}:v=0:a=1,apad=whole_dur={end}[v]"
ins = ['-i', 'input/voice_leveled.wav']; chains = []; mixl = ['[v]']
for j, (k, t) in enumerate(E['sfx'].items(), start=1):
    ins += ['-i', 'sfx/whoosh.wav' if k.startswith('w') else 'sfx/click.wav']
    vol = ',volume=-4dB' if k.startswith('t') else ''
    chains.append(f"[{j}]adelay={int(t * 1000)}:all=1{vol}[x{j}]"); mixl.append(f"[x{j}]")
fc += ";" + ";".join(chains) + f";{''.join(mixl)}amix=inputs={len(mixl)}:duration=first:normalize=0,atrim=0:{end}[a]"
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[a]', '-ar', '48000', '-ac', '1',
                'out/tight_audio.wav'], check=True)
print(round(end * 30))
