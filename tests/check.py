#!/usr/bin/env python3
"""Checks for the master-thesis LaTeX collection (see README.md, "Tests").

Sub-commands
------------
static <project-dir> <main.tex>
    Follows the \\input/\\include tree of <main.tex> and checks, from the
    sources alone:
      * every \\includegraphics argument resolves to a file on disk;
      * every \\cite key has an entry in the project's .bib file.
    Unused .bib entries are reported but never fail the run.

build <project-dir> <main.tex> <expected-pages> [outdir]
    Runs `latexmk -pdf` (output to <outdir>, or a fresh temporary directory)
    and checks the PDF exists, has exactly <expected-pages> pages, and that
    the final pass reports no fatal error, no unresolved reference, no
    unresolved citation and no missing input file.  Overfull/underfull boxes
    are reported as information.

usedkeys <project-dir> <main.tex>      one cited key per line
drop-entry <bib-file> <key>            removes one entry from a .bib file
inject-graphic <main.tex> <path>       inserts \\includegraphics{<path>} before \\end{document}

Exit status is 0 only when every check of the sub-command passed.
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

CITE_RE = re.compile(
    r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear|Cite|parencite|textcite"
    r"|autocite|footcite|smartcite|nocite)\*?(?:\[[^\]]*\])*\s*\{([^}]*)\}"
)
GRAPHICS_RE = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}")
INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]*)\}")
ADDBIB_RE = re.compile(r"\\addbibresource(?:\[[^\]]*\])?\s*\{([^}]*)\}")
BIBLIO_RE = re.compile(r"\\bibliography\s*\{([^}]*)\}")
ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")
GRAPHIC_EXTS = ("", ".pdf", ".png", ".jpg", ".jpeg", ".eps", ".ps", ".PNG", ".JPG")


def fail(msg):
    print("  FAIL: " + msg)


def note(msg):
    print("  note: " + msg)


def strip_comments(text):
    out = []
    for line in text.splitlines():
        res, i = "", 0
        while i < len(line):
            if line[i] == "%" and (i == 0 or line[i - 1] != "\\"):
                break
            res += line[i]
            i += 1
        out.append(res)
    return "\n".join(out)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return strip_comments(fh.read())


def input_tree(project, main):
    """All .tex reachable from <main> through \\input/\\include (LaTeX order)."""
    seen, order = set(), []

    def walk(rel):
        path = os.path.join(project, rel)
        if not os.path.isfile(path) or os.path.abspath(path) in seen:
            return
        seen.add(os.path.abspath(path))
        order.append(rel)
        text = read(path)
        for raw in INPUT_RE.findall(text):
            target = raw.strip()
            if not target or "\\" in target:  # macro or \input{|cmd}
                continue
            if not os.path.splitext(target)[1]:
                target += ".tex"
            walk(target)

    walk(main)
    return order


def bib_entries(project, rel_files):
    """{key: (bib file, index)} for every entry of the project's .bib files."""
    entries, files = {}, []
    for rel in rel_files:
        text = read(os.path.join(project, rel))
        for bib in ADDBIB_RE.findall(text) + BIBLIO_RE.findall(text):
            for name in bib.split(","):
                name = name.strip()
                if not name:
                    continue
                name = name if name.endswith(".bib") else name + ".bib"
                if name not in files:
                    files.append(name)
    for name in files:
        path = os.path.join(project, name)
        if not os.path.isfile(path):
            fail("declared bibliography %s does not exist" % name)
            continue
        raw = open(path, encoding="utf-8", errors="replace").read()
        for m in ENTRY_RE.finditer(raw):
            entries.setdefault(m.group(1).strip(), (name, raw))
    return entries, files


def check_static(project, main, quiet_ok=False):
    project = os.path.abspath(project)
    rels = input_tree(project, main)
    failures = 0

    if not rels:
        fail("main file %s not found under %s" % (main, project))
        return 1

    print("  input tree: %d .tex files (%s)" % (len(rels), ", ".join(rels[:6]) +
          (", ..." if len(rels) > 6 else "")))

    # ---- figures -------------------------------------------------------
    total = missing = 0
    missing_list = []
    for rel in rels:
        for raw in GRAPHICS_RE.findall(read(os.path.join(project, rel))):
            name = raw.strip()
            if not name or "\\" in name:
                continue
            total += 1
            base = os.path.join(project, name)
            candidates = [base + e for e in GRAPHIC_EXTS]
            if not any(os.path.isfile(c) for c in candidates):
                missing += 1
                missing_list.append("%s -> %s" % (rel, name))
    if missing:
        failures += 1
        fail("%d of %d \\includegraphics do not exist on disk" % (missing, total))
        for item in missing_list[:10]:
            print("        " + item)
        if len(missing_list) > 10:
            print("        ... and %d more" % (len(missing_list) - 10))
    elif not quiet_ok:
        print("  figures: %d/%d \\includegraphics resolve" % (total - missing, total))

    # ---- citations -----------------------------------------------------
    used = set()
    for rel in rels:
        for field in CITE_RE.findall(read(os.path.join(project, rel))):
            for key in field.split(","):
                key = key.strip()
                if key and key != "*":
                    used.add(key)
    entries, bibfiles = bib_entries(project, rels)
    absent, unused = [], []
    if not bibfiles:
        if used:
            failures += 1
            fail("%d citation keys but no .bib is declared by the main tree" % len(used))
        else:
            note("no bibliography declared and no citations used")
    else:
        absent = sorted(k for k in used if k not in entries)
        if absent:
            failures += 1
            fail("%d \\cite keys have no entry in %s: %s"
                 % (len(absent), ", ".join(bibfiles), ", ".join(absent[:8])))
        else:
            print("  citations: %d/%d \\cite keys found in %s"
                  % (len(used), len(used), ", ".join(bibfiles)))
        unused = sorted(k for k in entries if k not in used)
        if unused:
            note("%d .bib entries are never cited (reported, not a failure): %s%s"
                 % (len(unused), ", ".join(unused[:8]), " ..." if len(unused) > 8 else ""))

    # ---- stray .tex files (not part of the main tree) -------------------
    on_disk = {os.path.relpath(p, project) for p in
               glob.glob(os.path.join(project, "**", "*.tex"), recursive=True)}
    stray = sorted(on_disk - set(rels))
    if stray:
        note("not reachable from %s (ignored by these checks): %s"
             % (main, ", ".join(stray)))

    print("  summary: figures=%d figures_missing=%d cites=%d cites_missing=%d "
          "bib_entries=%d bib_unused=%d"
          % (total, missing, len(used), len(absent), len(entries), len(unused)))
    return failures


def check_build(project, main, expected_pages, outdir=None):
    project = os.path.abspath(project)
    failures = 0
    temp = None
    if outdir is None:
        temp = tempfile.mkdtemp(prefix="master-thesis-build-")
        outdir = temp
    os.makedirs(outdir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(main))[0]
    log_path, pdf_path = os.path.join(outdir, stem + ".log"), os.path.join(outdir, stem + ".pdf")

    cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-file-line-error",
           "-outdir=" + outdir, main]
    print("  $ (cd %s && %s)" % (os.path.relpath(project), " ".join(cmd)))
    proc = subprocess.run(cmd, cwd=project, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    out = proc.stdout + proc.stderr
    if proc.returncode != 0:
        failures += 1
        fail("latexmk exited %d" % proc.returncode)
        for line in out.splitlines():
            if line.startswith("Latexmk:") and ("rror" in line or "ailed" in line):
                print("        " + line.strip())
    if not os.path.isfile(pdf_path):
        failures += 1
        fail("no PDF produced at %s" % pdf_path)
        print("  summary: pages=0/%d unresolved_refs=0 unresolved_cites=0 "
              "missing_files=0 fatal_errors=0 latexmk_rc=%d"
              % (expected_pages, proc.returncode))
        if temp:
            shutil.rmtree(temp, ignore_errors=True)
        return failures

    if not os.path.isfile(log_path):
        failures += 1
        fail("no .log produced at %s" % log_path)
        return failures
    log = open(log_path, encoding="utf-8", errors="replace").read()

    errors = re.findall(r"(?m)^! (.*)$", log)
    if errors:
        failures += 1
        fail("%d fatal error(s) in the final pass: %s" % (len(errors), errors[0].strip()))
    missing = sorted({m for m in re.findall(r"File `([^']*)' not found", log)})
    if missing:
        failures += 1
        fail("missing input file(s): %s" % ", ".join(missing[:6]))
    undef_refs = sorted({m for m in re.findall(r"Reference `([^']*)' on page", log)})
    if undef_refs:
        failures += 1
        fail("%d unresolved reference(s): %s" % (len(undef_refs), ", ".join(undef_refs[:8])))
    undef_cites = sorted({m for m in re.findall(r"Citation `([^']*)' on page", log)})
    if undef_cites:
        failures += 1
        fail("%d unresolved citation(s): %s" % (len(undef_cites), ", ".join(undef_cites[:8])))

    info = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout
    m = re.search(r"(?m)^Pages:\s+(\d+)", info)
    pages = int(m.group(1)) if m else 0
    if pages != expected_pages:
        failures += 1
        fail("PDF has %d pages, expected %d" % (pages, expected_pages))
    else:
        print("  pages: %d (expected %d), %d bytes"
              % (pages, expected_pages, os.path.getsize(pdf_path)))

    if not errors and not missing and not undef_refs and not undef_cites:
        print("  log: 0 fatal errors, 0 unresolved references, 0 unresolved citations")
    overfull = len(re.findall(r"Overfull \\hbox", log))
    underfull = len(re.findall(r"Underfull \\hbox", log))
    note("%d overfull and %d underfull boxes (typesetting, not failures)"
         % (overfull, underfull))
    print("  summary: pages=%d/%d unresolved_refs=%d unresolved_cites=%d "
          "missing_files=%d fatal_errors=%d latexmk_rc=%d"
          % (pages, expected_pages, len(undef_refs), len(undef_cites),
             len(missing), len(errors), proc.returncode))
    return failures


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "static":
        return 1 if check_static(argv[2], argv[3] if len(argv) > 3 else "main.tex") else 0
    if cmd == "build":
        outdir = argv[5] if len(argv) > 5 else None
        bad = check_build(argv[2], argv[3], int(argv[4]), outdir)
        return 1 if bad else 0
    if cmd == "usedkeys":
        project, main = os.path.abspath(argv[2]), argv[3] if len(argv) > 3 else "main.tex"
        used = set()
        for rel in input_tree(project, main):
            for field in CITE_RE.findall(read(os.path.join(project, rel))):
                for key in field.split(","):
                    key = key.strip()
                    if key and key != "*":
                        used.add(key)
        print("\n".join(sorted(used)))
        return 0
    if cmd == "drop-entry":
        bib, key = argv[2], argv[3]
        raw = open(bib, encoding="utf-8", errors="replace").read()
        pattern = re.compile(r"@\w+\s*\{\s*" + re.escape(key) + r"\s*,[\s\S]*?(?=\n@|\Z)")
        new, n = pattern.subn("", raw, count=1)
        if not n:
            print("  FAIL: no entry %r in %s" % (key, bib))
            return 1
        open(bib, "w", encoding="utf-8").write(new)
        print("  dropped entry %r from %s" % (key, bib))
        return 0
    if cmd == "inject-graphic":
        path, target = argv[2], argv[3]
        raw = open(path, encoding="utf-8", errors="replace").read()
        idx = raw.rfind("\\end{document}")
        if idx < 0:
            print("  FAIL: %s has no \\end{document}" % path)
            return 1
        raw = raw[:idx] + "\\includegraphics{%s}\n" % target + raw[idx:]
        open(path, "w", encoding="utf-8").write(raw)
        print("  injected \\includegraphics{%s} into %s" % (target, path))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
