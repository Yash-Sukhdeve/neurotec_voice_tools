#!/usr/bin/env bash
# set -euo pipefail
# shopt -s nullglob

# ROOT="/home/lab2208/Desktop/SPEAD-20250828T143007Z-1-001/SPEAD"

# for dir in "$ROOT"/sub*/; do
#   sub="$(basename "$dir")"
#   ref="$dir/reference.wav"
#   wav="$dir/${sub}.wav"

#   [[ -f "$ref" && -f "$wav" ]] || { echo "Skipping $sub (missing wavs)"; continue; }

#   echo ">>> $sub"
#   python3 neurotec_voice_verifier.py "$ref" "$wav"
#   python3 neurotec_voice_verifier.py "$ref" "$ref"
# done

# #!/usr/bin/env bash
# set -euo pipefail
# shopt -s nullglob

# ROOT="/home/lab2208/Desktop/SPEAD-20250828T143007Z-1-001/SPEAD"
# PYTHON="python3"
# SCRIPT="neurotec_voice_verifier.py"   # adjust path if needed

# for dir in "$ROOT"/sub*/; do
#   sub="$(basename "$dir")"                 # e.g., sub82
#   ref="$dir/reference.wav"                 # e.g., sub82/reference.wav
#   wav="$dir/${sub}.wav"                    # e.g., sub82/sub82.wav

#   [[ -f "$ref" && -f "$wav" ]] || { echo "Skipping $sub (missing wavs)"; continue; }

#   ref16="$dir/reference_16K.wav"
#   wav16="$dir/${sub}_16K.wav"

#   # Resample to 16 kHz; do NOT set -ac, so channel count is preserved.
#   # For WAV, pcm_s16le is standard; resampling requires re-encoding (cannot -c:a copy).
#   ffmpeg -hide_banner -loglevel error -y -i "$ref" -ar 16000 -c:a pcm_s16le "$ref16"
#   ffmpeg -hide_banner -loglevel error -y -i "$wav" -ar 16000 -c:a pcm_s16le "$wav16"

#   echo ">>> $sub"
#   "$PYTHON" "$SCRIPT" "$ref16" "$wav16"
#   "$PYTHON" "$SCRIPT" "$ref16" "$ref16"
# done
# # Cleanup resampled files
# rm -f "$ROOT"/sub*/sub*_16K.wav "$ROOT"/sub*/reference_16K.

#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

ROOT="/home/lab2208/Desktop/SPEAD-20250828T143007Z-1-001/SPEAD"
PYTHON="python3"
SCRIPT="neurotec_voice_verifier.py"
OUT="$ROOT/voice_verification_summary.csv"

# Header once
if [[ ! -f "$OUT" ]]; then
  echo "Subject,reference_vs_reference,reference_vs_deepfake,similarity_percent(deepfake/ref_ref)" > "$OUT"
fi

for dir in "$ROOT"/sub*/; do
  sub="$(basename "$dir")"            # e.g., sub100
  ref="$dir/reference.wav"
  wav="$dir/${sub}.wav"
  [[ -f "$ref" && -f "$wav" ]] || { echo "Skipping $sub (missing wavs)"; continue; }

  ref16="$dir/reference_16K.wav"
  wav16="$dir/${sub}_16K.wav"

  # Resample to 16 kHz (keep channel count)
  ffmpeg -hide_banner -loglevel error -y -i "$ref" -ar 16000 -c:a pcm_s16le "$ref16"
  ffmpeg -hide_banner -loglevel error -y -i "$wav" -ar 16000 -c:a pcm_s16le "$wav16"

  echo ">>> $sub"

  out_rd="$("$PYTHON" "$SCRIPT" "$ref16" "$wav16")"
  out_rr="$("$PYTHON" "$SCRIPT" "$ref16" "$ref16")"

  # Extract the numeric score from "Verification Score: N"
  rd=$(awk -F': ' '/Verification Score:/ {print $2; exit}' <<< "$out_rd")
  rr=$(awk -F': ' '/Verification Score:/ {print $2; exit}' <<< "$out_rr")

  if [[ -z "${rr:-}" || -z "${rd:-}" ]]; then
    echo "Parse failure for $sub (rr='$rr', rd='$rd')" >&2
    continue
  fi

  # similarity = deepfake/reference * 100
  if [[ "$rr" -eq 0 ]]; then
    pct="NA"
  else
    pct=$(awk -v rr="$rr" -v rd="$rd" 'BEGIN{printf "%.2f", (rd/rr)*100}')
  fi

  echo "$sub,$rr,$rd,${pct}%" >> "$OUT"
done

echo "Wrote: $OUT"
# Cleanup resampled files
rm -f "$ROOT"/sub*/sub*_16K.wav "$ROOT"/sub*/reference_16K.wav      