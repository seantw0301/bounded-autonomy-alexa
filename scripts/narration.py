#!/usr/bin/env python3
"""prep: synthesize narration (macOS `say`) + durations. mux: mix audio at recorded cue times into the video."""
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
OUT = ART / "narration"
LANG = os.environ.get("NARRATION_LANG", "en")
VOICE = os.environ.get("NARRATION_VOICE", {"en": "Samantha", "zh": "Meijia"}[LANG])
RATE = os.environ.get("NARRATION_RATE", "165")


def prep():
    OUT.mkdir(parents=True, exist_ok=True)
    texts = json.loads((ROOT / "demo/narration.json").read_text())[LANG]
    manifest = {}
    for k, t in texts.items():
        f = OUT / f"{k}.aiff"
        subprocess.run(["say", "-v", VOICE, "-r", RATE, "-o", str(f), t], check=True)
        d = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                     "-of", "csv=p=0", str(f)], text=True)
        manifest[k] = round(float(d), 2)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print("narration prepared:", LANG, VOICE, f"{sum(manifest.values()):.0f}s of speech")


def mux():
    cues = json.loads((OUT / "cues.json").read_text())  # id -> seconds from video start
    src, dst = ART / "bounded-autonomy-demo.webm", ART / "bounded-autonomy-demo-narrated.webm"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src)]
    for k in cues:
        cmd += ["-i", str(OUT / f"{k}.aiff")]
    delays = ";".join(f"[{i+1}:a]adelay={int(t*1000)}|{int(t*1000)}[a{i}]" for i, t in enumerate(cues.values()))
    mix = "".join(f"[a{i}]" for i in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0[a]"
    cmd += ["-filter_complex", f"{delays};{mix}", "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "libopus", "-b:a", "96k", "-shortest", str(dst)]
    subprocess.run(cmd, check=True)
    print("wrote", dst.relative_to(ROOT))


{"prep": prep, "mux": mux}[sys.argv[1]]()
