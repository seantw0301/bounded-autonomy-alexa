#!/usr/bin/env python3
"""Narration pipeline.
  prep: synthesize every line in demo/narration.json + durations (artifacts/narration/manifest.json)
  mux : mix the lines at recorded cue times into the silent demo video

Engines (NARRATION_ENGINE): "kokoro" (default if the model env is found) = open neural TTS, runs locally;
"say" = macOS voice. Kokoro env: KOKORO_ENV (venv containing kokoro_onnx + model/ dir).
"""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
OUT = ART / "narration"
LANG = os.environ.get("NARRATION_LANG", "en")
KENV = Path(os.environ.get("KOKORO_ENV", ROOT.parent / "IntentChain/video/tts-env"))
ENGINE = os.environ.get("NARRATION_ENGINE", "kokoro" if (KENV / "bin/python").exists() and LANG == "en" else "say")
VOICE = os.environ.get("NARRATION_VOICE", {"kokoro": "af_heart", "say": {"en": "Samantha", "zh": "Meijia"}[LANG]}[ENGINE])
SPEED = os.environ.get("NARRATION_SPEED", "1.0")  # kokoro speed
RATE = os.environ.get("NARRATION_RATE", "165")  # say rate
EXT = "wav" if ENGINE == "kokoro" else "aiff"

# spellings the neural voice reads correctly
SPOKEN = [(r"\bMCP\b", "M C P"), (r"\bStoreA\b", "Store A"), (r"\bStoreB\b", "Store B"), (r"\bAlexa\+", "Alexa Plus")]


def spoken(t):
    for a, b in SPOKEN:
        t = re.sub(a, b, t)
    return t


def clip(k):
    return next(p for p in (OUT / f"{k}.wav", OUT / f"{k}.aiff") if p.exists())


def synth(text, f, speed=None):
    if ENGINE == "kokoro":
        py = KENV / "bin/python"
        subprocess.run([str(py), "-I", str(ROOT / "scripts/tts.py"), str(KENV / "model"), VOICE, str(speed or SPEED), str(f)],
                       input=spoken(text), text=True, check=True)
    else:
        subprocess.run(["say", "-v", VOICE, "-r", RATE, "-o", str(f), text], check=True)


def seconds(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(f)], text=True))


def prep():
    OUT.mkdir(parents=True, exist_ok=True)
    texts = json.loads((ROOT / "demo/narration.json").read_text())[LANG]
    manifest = {}
    for k, t in texts.items():
        f = OUT / f"{k}.{EXT}"
        synth(t, f)
        manifest[k] = round(seconds(f), 2)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"narration prepared: {LANG} {ENGINE}/{VOICE}, {sum(manifest.values()):.0f}s of speech")


def mux():
    cues = json.loads((OUT / "cues.json").read_text())  # id -> seconds from video start
    src, dst = ART / "bounded-autonomy-demo.webm", ART / "bounded-autonomy-demo-narrated.webm"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src)]
    for k in cues:
        cmd += ["-i", str(clip(k))]
    delays = ";".join(f"[{i+1}:a]aresample=44100,adelay={int(t*1000)}:all=1[a{i}]" for i, t in enumerate(cues.values()))
    mix = "".join(f"[a{i}]" for i in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0[a]"
    cmd += ["-filter_complex", f"{delays};{mix}", "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "libopus", "-b:a", "96k", "-shortest", str(dst)]
    subprocess.run(cmd, check=True)
    print("wrote", dst.relative_to(ROOT))


{"prep": prep, "mux": mux}[sys.argv[1]]()
