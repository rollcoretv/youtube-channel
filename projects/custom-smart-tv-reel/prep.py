"""Builds timeline.json: corrected transcript words with start times snapped to measured speech pauses."""
import json, re, subprocess, sys, os

D = os.path.dirname(os.path.abspath(__file__))
segs = json.load(open(f"{D}/input/words.json"))

# Whisper mishearings, checked by ear against the recording (flagged for Mohammad's review)
FIX = {"القوام": "القوائم", "نسممه": "نصممه", "جهست": "جهّزت", "البرومت": "البرومبت",
       "وتحديدا": "وتحديداً"}
words = []
for s in segs:
    for w in s["words"]:
        words.append({"w": FIX.get(w["w"], w["w"]), "s": w["s"], "e": w["e"]})
# "تبت جرب" -> "تبي تجرب" (two tokens kept, text fixed)
for i, w in enumerate(words):
    if w["w"] == "تبت" and words[i + 1]["w"] == "جرب":
        w["w"], words[i + 1]["w"] = "تبي", "تجرب"

out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f"{D}/input/voice.m4a", "-af",
                      "silencedetect=noise=-40dB:d=0.35", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
ts = [float(x) for x in re.findall(r"silence_(?:start|end): ([0-9.]+)", out)]
sil = list(zip(ts[0::2], ts[1::2]))
# whisper glues the pause before a word onto the word; move its start to where speech resumes
for w in words:
    for a, b in sil:
        if a - 0.05 <= w["s"] < b < w["e"]:
            w["s"] = round(b, 3)

json.dump({"words": words, "silences": sil}, open(f"{D}/timeline.json", "w"), ensure_ascii=False, indent=1)
for i, w in enumerate(words):
    print(i, w["w"], w["s"], w["e"])

# ---- pause tightening (requested by Mohammad after preview v03) ----
# Any pause longer than MAXP is cut down to TAIL after the speech + HEAD before the next phrase.
MAXP, TAIL, HEAD, HOLD = 0.45, 0.18, 0.14, 2.0
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            f"{D}/input/voice_leveled.wav"], capture_output=True, text=True).stdout)
speech_end = sil[-1][0]
cuts = [(a + TAIL, b - HEAD) for a, b in sil if b - a > MAXP and a > 0.1 and b < dur - 0.01]
keep, pos = [], 0.0
for a, b in cuts:
    keep.append((pos, a)); pos = b
keep.append((pos, min(dur, speech_end + 0.4)))
segs_map, n = [], 0.0
for a, b in keep:
    segs_map.append([round(a, 3), round(b, 3), round(n, 3)]); n += b - a

def M(t):
    for a, b, s in segs_map:
        if t < a: return s            # inside a removed gap: snap to the cut point
        if t <= b: return s + t - a
    return segs_map[-1][2] + segs_map[-1][1] - segs_map[-1][0] + (t - segs_map[-1][1])

for w in words:
    w["s"], w["e"] = round(M(w["s"]), 3), round(M(w["e"]), 3)
end = round(M(speech_end) + 0.4 + HOLD, 3)
json.dump({"words": words, "map": segs_map, "end": end}, open(f"{D}/timeline.json", "w"), ensure_ascii=False, indent=1)
json.dump({"keep": keep, "end": end, "sfx": {k: round(M(v), 3) for k, v in
           {"click": 0.98, "t1": 59.78, "t2": 60.32, "t3": 61.1, "t4": 61.86, "w1": 2.7, "w2": 15.9, "w3": 29.9}.items()}},
          open(f"{D}/edit.json", "w"), indent=1)
print("cuts:", len(cuts), "new speech length:", round(n, 2), "end:", end, "removed:", round(dur - n, 2))
