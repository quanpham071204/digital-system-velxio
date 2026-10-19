#!/usr/bin/env bash
# Xuất README.md của một bài thành PDF để nộp.
#   Cách dùng:  tools/build_pdf.sh B01-kiem-tra-IC
# Cần: pandoc + Chromium/Chrome (headless).
set -euo pipefail
dir="${1:?Truyen ten thu muc bai, vd B01-kiem-tra-IC}"
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root/$dir"
chrome="${CHROME:-$(command -v chromium || command -v google-chrome || command -v chrome || echo /opt/pw-browsers/chromium-1194/chrome-linux/chrome)}"
pandoc README.md -s --metadata title="$dir" --css "$root/tools/report.css" \
  --embed-resources -o /tmp/"$dir".html
"$chrome" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$root/$dir/$dir.pdf" "file:///tmp/$dir.html" 2>/dev/null
echo "Da xuat $dir/$dir.pdf"
