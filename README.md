# master-thesis

> LaTeX sources for an M.Sc. dissertation on automatic image-quality assessment, the four papers built on the same work, and the reference material, poster and slides that go with them.

## What it is

Three top-level folders, 180 tracked files and 343 MB of tracked content (Gitea reports 320 MB; the working tree plus `.git` occupies 666 MB on disk). This is a LaTeX collection, not a program: nothing runs, everything compiles.

- **`thesis/`** (55 files, 60 MB) — the dissertation: *"Metrics of automatic Image Quality Assessment based on Human Perception — A comparative study and a proposal of a new metric"*, an M.Sc. in Electrical and Computer Engineering (University of Coimbra), **114 pages** when compiled. `thesis/main.tex` (270 lines) holds the preamble and the chapter order; the text lives in `thesis/chapters/` (7 files) and `thesis/appendix/` (4 files), the front matter in `thesis/misc/` (title page, abstract, resumo, acronyms, `references.bib` with 150 entries), and the 28 figures in `thesis/images/`. The committed `thesis/main.pdf` is the submitted PDF, `thesis/main_v0.pdf` is an earlier snapshot of the same 114 pages, and `thesis/thesis.pptx` (21.57 MB) is the defence presentation.
- **`papers/`** (96 files, 178 MB) — four self-contained LaTeX projects, each with its own document class, `.bib`, figures and compiled PDF. All four are by André Neto, three of them with Nuno Gonçalves (University of Coimbra) as co-author:
  - `papers/demographic-bias/` — *"Optimizing Image Quality Assessment metrics for subjective perception controlling demographic bias"*, IEEE (`IEEEtran.cls`, `ieeetr`), **6 pages**;
  - `papers/ibpria2025/` — *"Pseudo-MOS Learning: A Full-to-No-Reference FIQA Framework"*, Springer LNCS (`llncs.cls`, `splncs04`), **15 pages**;
  - `papers/ibpria-extended2025/` — the extended version of the same paper, LNCS, **15 pages**;
  - `papers/on-paper-data-aug/` — *"An On-Paper Data Augmentation Algorithm for Dataset Generation"*, LNCS, **7 pages**.
- **`documents/`** (25 files, 106 MB) — material around the thesis, not documents to compile: 24 literature PDFs on image-quality metrics and subjective assessment (TID2013, ITU-R BT.500, SSIM/PSNR surveys…), the CoDEEC poster and presentation (`documents/coDEEC/poster.pptx`, 42.73 MB, the largest single file in the repository) and `documents/notes.txt`. No `.tex` file exists here, so nothing here is built.

The 343 MB is content, not litter. By kind (at clone time, 180 files): PDFs 169.48 MB (59 files), slide decks `.pptx` 92.27 MB (5), images `.jpg`/`.png`/`.eps` 62.31 MB (53), one `.zip` 12.87 MB, LaTeX sources `.tex`/`.bib`/`.cls` 0.80 MB (50), three `-eps-converted-to.pdf` caches 5.52 MB, everything else 0.15 MB. The ten largest files are:

| MB | file |
|---|---|
| 42.73 | `documents/coDEEC/poster.pptx` |
| 39.70 | `papers/on-paper-data-aug/main.pdf` |
| 21.57 | `thesis/thesis.pptx` |
| 13.59 | `papers/ibpria-extended2025/ibpria.pptx` |
| 13.59 | `papers/ibpria2025/ibpria.pptx` |
| 13.27 | `thesis/main.pdf` |
| 13.03 | `thesis/main_v0.pdf` |
| 12.87 | `papers/ibpria2025.zip` |
| 12.48 | `papers/on-paper-data-aug/images/006.jpg` |
| 8.57 | `papers/demographic-bias/main.pdf` |

Nothing in the history is compilation junk: the only two build leftovers ever committed were the empty LibreOffice lock files `thesis/.~lock.thesis.pptx#` and `thesis/.~lock.thesis-arch.pptx#`, and they were removed from the index on 2026-10-08 (`.gitignore` now covers that pattern). The binaries above are deliverables — the submitted PDFs, the defence and conference slides, the high-resolution figures and the literature — so they stay.

Four things are duplicated or vestigial. They are left in place, because deciding what is content and what is waste is not a decision for a cleanup commit:

- `papers/ibpria-extended2025/` is **byte-for-byte identical** to `papers/ibpria2025/`: `diff -rq` reports no difference at all and both trees are 35,011,632 bytes. The two committed PDFs differ only in their PDF identifiers. The "extended" paper is therefore a copy of the regular one, and one copy is redundant.
- `papers/ibpria2025.zip` (12.87 MB) is an archive of the `papers/ibpria2025/` folder that is already in the tree.
- `papers/on-paper-data-aug/aux.tex` (173 lines) is the unmodified Springer LNCS `samplepaper.tex`: it is not reachable from `main.tex`, and its `\includegraphics{fig1.eps}` points at a file that was never committed — the only missing figure in the repository. The 70 `\includegraphics` of the five main documents all resolve (thesis 29, each IBPria paper 13, demographic-bias 6, on-paper-data-aug 9).
- `thesis/main_v0.pdf` (13,659,246 bytes) is an earlier snapshot of `thesis/main.pdf` (13,911,763 bytes); both are 114 pages.

Two content defects are recorded here and were **not** corrected, because the text and the bibliography are the author's:

- `thesis/misc/references.bib` uses the month macros `September` and `April` unbraced (lines 346 and 354), so `biber` warns `undefined macro`; lines 1035 and 1047 carry stray characters ("13 characters of junk seen at toplevel", "1 character of junk"). All 146 cited keys do resolve, and the three remaining `.bib` warnings per paper are of the same kind.
- Four entries of `thesis/misc/references.bib` are never cited (`liu2012gssim`, `neto2025pseudo`, `svr`, `tutuncu2018steganography`); `papers/ibpria2025/references.bib` has 31 uncited entries of 94 and `papers/demographic-bias/references.bib` 36 of 71. Unused entries are reported by the tests, never treated as a failure.

## Requirements

- A TeX Live installation with `pdflatex`, `latexmk`, `bibtex` and `biber`, and these Debian packages: `texlive-latex-base`, `texlive-latex-recommended`, `texlive-latex-extra`, `texlive-fonts-recommended`, `texlive-science`, `texlive-pictures`, `texlive-bibtex-extra`, `texlive-publishers`, `texlive-lang-portuguese`, `lmodern`, `latexmk`, `biber`.
  - `biber` (2.20) is required by `thesis/main.tex`, which loads `biblatex` with `backend=biber`.
  - `texlive-lang-portuguese` provides the `portuguese` language and hyphenation patterns the thesis asks `babel` for.
  - `texlive-publishers` provides `splncs04.bst`, the Springer LNCS bibliography style used by the three LNCS papers. Without it `bibtex` stops with `I couldn't open style file splncs04.bst`, no `.bbl` is produced and every citation stays undefined.
- `make` for the test and build targets.
- `python3` for `tests/check.py`, and `pdfinfo` (`poppler-utils`) to count PDF pages.

Tested on Debian 13 (arm64, Raspberry Pi 5) with TeX Live 2025.

## Install / Build

```sh
sudo apt-get install -y texlive-latex-base texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended texlive-science texlive-pictures texlive-bibtex-extra \
    texlive-publishers texlive-lang-portuguese lmodern latexmk biber make python3 poppler-utils
```

Each document is built with `latexmk`, which runs `pdflatex`/`biber`/`bibtex` as many times as the cross-references need. Run it from the document's directory and keep the output out of the repository, so the committed PDFs are never overwritten by a test run:

```sh
cd thesis && latexmk -pdf -outdir=/tmp/build/thesis main.tex                 # 114 pages, ~50 s cold
cd papers/ibpria2025 && latexmk -pdf -outdir=/tmp/build/ibpria2025 main.tex   # 15 pages
```

`make build` compiles all five documents the same way into `build/` (git-ignored) and prints where the PDFs are.

## Usage

```sh
make build        # all five documents into build/<document>/main.pdf
make clean        # remove build/
```

To build one document by hand, `cd` into its folder and call `latexmk` with an `-outdir=...` outside the repository, e.g.

```sh
cd papers/demographic-bias && latexmk -pdf -outdir=/tmp/db main.tex
```

`documents/` contains no `.tex` file: it is reference material and slide decks, and there is nothing to compile there. `papers/on-paper-data-aug/aux.tex` is a stray LNCS sample that no build uses; `latexmk -pdf aux.tex` on it fails, correctly, because the `fig1.eps` it asks for does not exist.

## Tests

`make test` (equivalently `tests/run.sh full`) compiles all five main documents into a temporary directory with `latexmk` and checks the result; `make test-static` (`tests/run.sh static`) runs only the source checks, in a few seconds. The suite exits non-zero if anything fails.

`tests/check.py static` follows the `\input`/`\include` tree of each main file and asserts, from the sources alone, that every `\includegraphics` resolves to a file on disk and that every `\cite` key has an entry in the project's `.bib` (unused entries are reported, not fatal). `tests/check.py build` adds the compiled checks: the PDF exists, has exactly the expected number of pages (`tests/documents.conf`), and the final pass has no fatal error, no unresolved reference, no unresolved citation and no missing input file. Overfull and underfull boxes are reported as information.

The suite also carries negative checks, which must fail for the suite to be green: a figure pointing at a file that does not exist (both as a fixture and injected into the real `papers/demographic-bias` before building), a citation with no `.bib` entry, a real thesis copy with a used `.bib` entry deleted, a real thesis copy with `images/` removed, and a build whose expected page count is wrong. Two control checks (a clean fixture that must pass static and build) prove the negative checks are not failing for the wrong reason.

The whole suite on the committed tree (`make test`; the per-document headings and the compile logs are trimmed here):

```text
| document | pages (want -> got) | static | build | unresolved | result |
|---|---|---|---|---|---|
| `thesis/main.tex` | 114 -> 114 | ok | ok | refs 0/cites 0 unresolved | PASS |
| `papers/ibpria2025/main.tex` | 15 -> 15 | ok | ok | refs 0/cites 0 unresolved | PASS |
| `papers/ibpria-extended2025/main.tex` | 15 -> 15 | ok | ok | refs 0/cites 0 unresolved | PASS |
| `papers/demographic-bias/main.tex` | 6 -> 6 | ok | ok | refs 0/cites 0 unresolved | PASS |
| `papers/on-paper-data-aug/main.tex` | 7 -> 7 | ok | ok | refs 0/cites 0 unresolved | PASS |

| check | expectation | actual | ok |
|---|---|---|---|
| fixture: figure points at a file that does not exist | static must fail | failed (exit 1) | yes |
| fixture: citation with no .bib entry | static must fail | failed (exit 1) | yes |
| fixture: clean document (control) | static must pass | passed (exit 0) | yes |
| fixture: clean document compiles (control) | build must pass | passed (exit 0) | yes |
| fixture: wrong expected page count | build must fail | failed (exit 1) | yes |
| thesis copy: used .bib entry 'abed2025fiqabiometric' deleted | static must fail | exit 1 | yes |
| thesis copy with images/ deleted | static must fail | exit 1 | yes |
| real paper + \includegraphics to a missing file | build must fail | exit 1 | yes |

checks: 13 | failed: 0
RESULT: PASS
```

The five documents then build to **114, 15, 15, 6 and 7 pages** — the same page counts as the committed PDFs — with 0 fatal errors, 0 unresolved references, 0 unresolved citations and 0 missing files each; 6 overfull and 4 underfull boxes in the thesis, 1 overfull in `on-paper-data-aug` and 1 underfull box in `demographic-bias` are the only typesetting warnings. The 70 `\includegraphics` and 307 `\cite` keys of those documents all resolve. A full run takes about 70 seconds on the Pi 5 (a cold run on a fresh TeX installation is slower, because the fonts are generated the first time).

## Structure

```
thesis/main.tex                      270 lines; preamble, chapter order, bibliography (biblatex, biber)
thesis/main.pdf                      114 pages; the submitted dissertation
thesis/main_v0.pdf                   114 pages; earlier snapshot of the same thesis
thesis/thesis.pptx                   21.57 MB; defence presentation
thesis/chapters/                     7 files; introduction to conclusion
thesis/appendix/                     4 files; screening, full reference list, regression models, environment
thesis/misc/                         title page, abstract, resumo, acronyms, UC logos, references.bib (150 entries)
thesis/images/                       28 figures
thesis/README.md                     the upstream template's README, kept as it came (see License)
papers/demographic-bias/             IEEE paper, IEEEtran.cls + references.bib (71 entries), 6 pages
papers/ibpria2025/                   LNCS paper, llncs.cls + references.bib (94 entries), 15 pages
papers/ibpria-extended2025/          byte-identical copy of papers/ibpria2025/, 15 pages
papers/on-paper-data-aug/            LNCS paper, 7 pages; aux.tex is a stray LNCS sample
papers/ibpria2025.zip                12.87 MB; archive of papers/ibpria2025/
documents/methods/, metrics/, surveys/   24 literature PDFs
documents/coDEEC/                    poster.pptx (42.73 MB) and apresentacao.pptx
documents/notes.txt                  working notes
tests/run.sh, tests/check.py         the test suite
tests/documents.conf                 the five main documents and their expected page counts
Makefile                             test, test-static, build, clean
.gitignore                           LaTeX build products, editor and office leftovers
```

## License

Por definir — trabalho académico com orientação e co-autoria.

No `LICENSE` file exists in this repository and none was added on 2026-10-08. The dissertation's title page names a supervisor (Nuno Miguel Mendonça da Silva Gonçalves) and a co-supervisor (João de Sena Baptista Pimentel Marcos), and three of the four papers are co-authored with Nuno Gonçalves. Choosing a licence for someone else's academic work is not a decision one of the authors can take alone, so until all of them agree, all rights are reserved and no licence is granted.

That decision does not extend to the third-party material, which keeps its own origin and terms and is not covered by any licence of this repository.

### Provenance of the template and the document classes

- `thesis/` is built on **`latex-dissertation-template`**, a public M.Sc. dissertation template by Mário Cristóvão (<https://github.com/mjpc13/latex-dissertation-template>). `thesis/main.tex` says so in its header ("A work by Mário Cristóvão, based on an example by Gonçalo Martins and José Faria") and `thesis/README.md` is that project's README, kept verbatim. The template follows the University of Coimbra / FCTUC visual identity, uses the standard `book` class, and carries no licence notice of any kind in this repository; it is kept here because the thesis does not compile without it.
- `papers/ibpria2025/llncs.cls`, `papers/ibpria-extended2025/llncs.cls` and `papers/on-paper-data-aug/llncs.cls` are **Springer's LNCS document class** (`LLNCS DOCUMENT CLASS -- version 2.24 (29-Jan-2024)`), vendored per paper. They are pinned, not taken from the TeX distribution: they differ from the TeX Live copy at `/usr/share/texlive/texmf-dist/tex/latex/llncs/llncs.cls`. The two `ibpria*` copies are identical to each other; the `on-paper-data-aug` copy is a different revision.
- `papers/demographic-bias/IEEEtran.cls` is the **IEEE** class for IEEE Transactions papers (`IEEEtran.cls 2015/08/26 version V1.8b`, <http://www.michaelshell.org/tex/ieeetran/>, <https://www.ieee.org/>).
- The three `*-eps-converted-to.pdf` files in `papers/demographic-bias/images/` were produced by `epstopdf` from the `.eps` files next to them; they regenerate at build time and could be dropped from the index if the author prefers.
