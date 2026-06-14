---
name: rime-develop
description: Conventions for editing the 雾凇拼音 (rime-ice) Rime config — where to place new Chinese/English/emoji words, schema/config/lua edits, word-frequency rules, and Conventional Commit format. Use when adding or modifying dictionary entries, input schemas, symbols, or lua extensions in this repo.
---

# rime-develop — editing conventions for rime-ice

Authoritative source: `AGENTS.md`. This skill condenses the rules you must follow. After any
edit, validate with the **rime-build** skill.

## Hard rules

- **Never delete files.** **Never edit `README.md`.**
- Never edit `radical_pinyin.*.yaml` or `lua/search.lua` (upstream-synced; fix issues upstream).
- Don't hand-edit generated files — edit the source, then rebuild:
  - Chinese mix `en_dicts/*.txt` ← edit `others/cn_en.txt`
  - `opencc/*.txt` (emoji etc.) ← edit `others/emoji-map.txt`
  - `rime_ice.dict.yaml` / `melt_eng.dict.yaml` are aggregators — add words to the sub-dicts.
- `*.dict.yaml` files are huge: read the first ~100 lines, then grep to locate; modify by
  find/replace/append, never whole-file rewrite.

## Where new words go

**Chinese — `cn_dicts/`** (never edit `rime_ice.dict.yaml` directly):
- `8105` — common single characters
- `41448` — large/rare character table (off by default)
- `base` — core: two-char words & common words. **All two-char words go here.** Needs 注音 + 词频.
- `ext` — extended; needs 注音 + 词频. **All entries containing polyphones (多音字) go here.**
- `tencent` — large dict. **No 注音.** Weight optional (build fills it). **No polyphones.**

**English — `en_dicts/`** (never edit `melt_eng.dict.yaml` directly):
- `en` — core English words
- `en_ext` — net slang, product names, special abbreviations, proper names

**Mixed CN/EN** → edit only `others/cn_en.txt`, then build.
**Emoji / special output** → edit only `others/emoji-map.txt`, then build.

## Word frequency

Default weight is **100**. If there's a 重码 (same encoding collision), tune the weight up/down
to match everyday usage priority.

## Recommended edit sequence

1. `grep -r "目标词" <dict-dir>/` to check if the entry already exists.
2. Write the edit to the correct file with complete format (order doesn't matter).
3. Run the build (rime-build skill) — it auto-sorts & dedups. Fix any reported error.

## Schema / config / symbols / lua

- `*.schema.yaml` — input schemas (spelling, translators, filters, dict refs).
- `default.yaml` — global defaults & enabled schemas. `weasel.yaml` (Weasel/Windows),
  `squirrel.yaml` (Squirrel/macOS) — frontend config.
- `symbols_v.yaml` / `symbols_caps_v.yaml` — `v`/`V` symbol input.
- `lua/` — librime-lua extensions. Lint after editing (rime-build → lint).

## Commit format (Conventional Commits, body in Chinese)

Types: `feat`, `fix`, `refactor`, `ci`, `build`, `docs`, `chore`. Project scopes:
- `dict(cn)`, `dict(en)`, `dict(radical)`, `dict(opencc)`
- `config` (e.g. `config(schema)`, `config(weasel)`), `lua` (e.g. `feat(lua)`)

Breaking changes: add `!` after type/scope (e.g. `refactor(lua)!:`) and update
`others/docs/Changelog.md`. Keep the working tree limited to files relevant to the task —
no stray reformatting or generated output.
