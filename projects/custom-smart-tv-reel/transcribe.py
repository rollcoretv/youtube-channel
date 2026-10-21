import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

path, out = sys.argv[1], sys.argv[2]
# decode with ffmpeg directly; the bundled PyAV rejects faster-whisper's open() args
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(raw, np.float32)
model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=4)
segments, info = model.transcribe(audio, language="ar", word_timestamps=True, beam_size=5,
                                  vad_filter=False, condition_on_previous_text=False)
data = []
for s in segments:
    data.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                 "words": [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2),
                            "p": round(w.probability, 2)} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}", flush=True)
json.dump(data, open(out, "w"), ensure_ascii=False, indent=1)
