#!/usr/bin/env bash
# Full pipeline: neural narration -> 30s opening -> narrated demo -> final mp4.
set -e
cd "$(dirname "$0")/.."
python3 scripts/narration.py prep
(cd demo && node record-intro.mjs)
NARRATE=1 scripts/record-demo.sh
scripts/assemble-video.sh
