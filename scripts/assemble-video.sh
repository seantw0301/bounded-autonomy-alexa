#!/usr/bin/env bash
# Joins the 30s opening to the narrated demo -> artifacts/bounded-autonomy-final.mp4 (H.264/AAC, loudness-normalised)
set -euo pipefail
cd "$(dirname "$0")/../artifacts"
INTRO=intro.mp4; MAIN=bounded-autonomy-demo-narrated.webm; OUT=bounded-autonomy-final.mp4
FADE=$(echo "$(ffprobe -v error -show_entries format=duration -of csv=p=0 $INTRO) - 0.35" | bc -l)
ffmpeg -y -loglevel error -i $INTRO -i $MAIN -filter_complex "
  [0:v]scale=1280:800,fps=30,format=yuv420p,fade=t=out:st=${FADE}:d=0.35[v0];
  [0:a]aresample=44100,aformat=channel_layouts=stereo[a0];
  [1:v]scale=1280:800,fps=30,format=yuv420p,fade=t=in:st=0:d=0.35[v1];
  [1:a]aresample=44100,aformat=channel_layouts=stereo[a1];
  [v0][a0][v1][a1]concat=n=2:v=1:a=1[v][ac];
  [ac]loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart $OUT
L=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT)
printf 'Wrote artifacts/%s — %dm%02ds\n' "$OUT" "$(echo "$L/60" | bc)" "$(echo "$L%60/1" | bc)"
