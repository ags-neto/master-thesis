#!/usr/bin/env bash
# Test suite for the master-thesis LaTeX collection.  See README.md, "Tests".
#
#   tests/run.sh            compile every main document and check it (slow)
#   tests/run.sh static     sources only, no compilation (fast)
#
# Exits non-zero if any check fails.

set -u

ROOT=$(cd "$(dirname "$0")/.." && pwd)
CHECK="$ROOT/tests/check.py"
CONF="$ROOT/tests/documents.conf"
MODE="${1:-full}"
case "$MODE" in full|static) ;; *) echo "usage: $0 [full|static]" >&2; exit 2 ;; esac

WORK=$(mktemp -d "${TMPDIR:-/tmp}/master-thesis-tests.XXXXXX")
cleanup() {
  case "$WORK" in /tmp/*|"${TMPDIR:-/tmp}"/*) rm -rf "$WORK" ;; esac
}
trap cleanup EXIT

CHECKS=0
FAILED=0
declare -a ROWS=()
declare -a DOCROWS=()

add_row() { # name | expectation | actual | ok
  ROWS+=("| $1 | $2 | $3 | $4 |")
  CHECKS=$((CHECKS + 1))
  [ "$4" = "yes" ] || FAILED=$((FAILED + 1))
}
add_doc() { # document | pages want/got | static | build | unresolved | result
  DOCROWS+=("| $1 | $2 | $3 | $4 | $5 | $6 |")
  CHECKS=$((CHECKS + 1))
  [ "$6" = "PASS" ] || FAILED=$((FAILED + 1))
}
summary() { sed -n 's/^  summary: //p' <<<"$1" | tail -1; }

echo "== master-thesis test suite =="
echo "root: $ROOT"
echo "mode: $MODE ($([ "$MODE" = full ] && echo 'compile + sources' || echo 'sources only'))"
echo "tex:  $(pdflatex --version 2>/dev/null | head -1)"
echo "tool: $(latexmk -v 2>/dev/null | head -1)"
echo
echo "-- main documents --"

while IFS='|' read -r dir main pages; do
  case "$dir" in ''|'#'*) continue ;; esac
  doc="$dir/$main"
  echo "### $doc"

  out=$("$CHECK" static "$ROOT/$dir" "$main" 2>&1); rc=$?
  ssum=$(summary "$out")
  echo "$out" | sed 's/^/    /'
  [ "$rc" = 0 ] && static="ok" || static="FAIL"

  build="n/a"; usum="n/a"; got="$pages"
  if [ "$MODE" = full ]; then
    out=$("$CHECK" build "$ROOT/$dir" "$main" "$pages" "$WORK/build/$dir" 2>&1); rc=$?
    echo "$out" | sed 's/^/    /'
    bsum=$(summary "$out")
    [ "$rc" = 0 ] && build="ok" || build="FAIL"
    got=$(sed -n 's/.*pages=\([0-9]*\)\/.*/\1/p' <<<"$bsum" | tail -1)
    [ -n "$got" ] || got="?"
    refs=$(sed -n 's/.*unresolved_refs=\([0-9]*\).*/\1/p' <<<"$bsum" | tail -1)
    cits=$(sed -n 's/.*unresolved_cites=\([0-9]*\).*/\1/p' <<<"$bsum" | tail -1)
    usum="refs ${refs:-?}/cites ${cits:-?} unresolved"
  fi

  if [ "$static" = ok ] && { [ "$MODE" = static ] || [ "$build" = ok ]; }; then res="PASS"; else res="FAIL"; fi
  add_doc "\`$doc\`" "${pages} -> ${got}" "$static" "$build" "$usum" "$res"
done < "$CONF"

echo
echo "-- negative and control checks --"

run_negative() { # name | expectation | command...
  local name="$1" expect="$2"; shift 2
  local out rc
  out=$("$@" 2>&1); rc=$?
  local actual ok
  if [ "$rc" != 0 ]; then actual="failed (exit $rc)"; else actual="passed (exit 0)"; fi
  if [[ "$expect" == *"must fail"* ]]; then
    ok=$([ "$rc" != 0 ] && echo yes || echo no)
  else
    ok=$([ "$rc" = 0 ] && echo yes || echo no)
  fi
  add_row "$name" "$expect" "$actual" "$ok"
  if [ "$ok" = no ]; then echo "    --- output of the failing check ---"; echo "$out" | sed 's/^/    /'; fi
}

run_negative "fixture: figure points at a file that does not exist" "static must fail" \
  "$CHECK" static "$ROOT/tests/fixtures/missing-figure" main.tex
run_negative "fixture: citation with no .bib entry" "static must fail" \
  "$CHECK" static "$ROOT/tests/fixtures/missing-cite" main.tex
run_negative "fixture: clean document (control)" "static must pass" \
  "$CHECK" static "$ROOT/tests/fixtures/ok" main.tex
run_negative "fixture: clean document compiles (control)" "build must pass" \
  "$CHECK" build "$ROOT/tests/fixtures/ok" main.tex 1 "$WORK/build/fixture-ok"
run_negative "fixture: wrong expected page count" "build must fail" \
  "$CHECK" build "$ROOT/tests/fixtures/ok" main.tex 99 "$WORK/build/fixture-pages"

# A used .bib entry removed from a copy of the real thesis sources.
cp -r "$ROOT/thesis" "$WORK/thesis-bib" 2>/dev/null
key=$(python3 "$CHECK" usedkeys "$ROOT/thesis" main.tex | head -1)
if [ -n "$key" ]; then
  python3 "$CHECK" drop-entry "$WORK/thesis-bib/misc/references.bib" "$key" >/dev/null 2>&1
fi
out=$(python3 "$CHECK" static "$WORK/thesis-bib" main.tex 2>&1); rc=$?
ok=no
[ -n "$key" ] && [ "$rc" != 0 ] && ok=yes
add_row "thesis copy: used .bib entry '$key' deleted" "static must fail" "exit $rc" "$ok"
[ "$ok" = yes ] || { echo "    --- output ---"; echo "$out" | sed 's/^/    /'; }

# The real thesis sources with no images on disk.
cp -r "$ROOT/thesis" "$WORK/thesis-fig" 2>/dev/null
rm -rf "$WORK/thesis-fig/images"
out=$(python3 "$CHECK" static "$WORK/thesis-fig" main.tex 2>&1); rc=$?
ok=no; [ "$rc" != 0 ] && ok=yes
add_row "thesis copy with images/ deleted" "static must fail" "exit $rc" "$ok"
[ "$ok" = yes ] || { echo "    --- output ---"; echo "$out" | sed 's/^/    /'; }

if [ "$MODE" = full ]; then
  # A real paper with one extra graphic that does not exist: the build must fail.
  cp -r "$ROOT/papers/demographic-bias" "$WORK/db-bad" 2>/dev/null
  python3 "$CHECK" inject-graphic "$WORK/db-bad/main.tex" images/DOES-NOT-EXIST.png >/dev/null 2>&1
  out=$(python3 "$CHECK" build "$WORK/db-bad" main.tex 6 "$WORK/build/db-bad" 2>&1); rc=$?
  add_row "real paper + \includegraphics to a missing file" "build must fail" "exit $rc" \
    "$([ "$rc" != 0 ] && echo yes || echo no)"
else
  echo "  (compile-level negative checks skipped in static mode)"
fi

echo
echo "-- documents --"
echo "| document | pages (want -> got) | static | build | unresolved | result |"
echo "|---|---|---|---|---|---|"
printf '%s\n' "${DOCROWS[@]}"
echo
echo "-- checks --"
echo "| check | expectation | actual | ok |"
echo "|---|---|---|---|"
printf '%s\n' "${ROWS[@]}"
echo
echo "checks: $CHECKS | failed: $FAILED"
if [ "$FAILED" = 0 ]; then echo "RESULT: PASS"; else echo "RESULT: FAIL"; fi
[ "$FAILED" = 0 ] || exit 1
exit 0
