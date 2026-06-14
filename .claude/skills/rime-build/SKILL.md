---
name: rime-build
description: Build, lint, and smoke-test the 雾凇拼音 (rime-ice) config. Use after editing any dictionary (cn_dicts/, en_dicts/, opencc/, others/cn_en.txt, others/emoji-map.txt), schema (*.schema.yaml), config (default.yaml, weasel.yaml, squirrel.yaml), or lua/*.lua file to generate/dedup/sort/validate and catch errors before committing.
---

# rime-build — build, lint & smoke-test rime-ice

This repo's CI (`.github/workflows/test.yml`, `release.yml`) drives three targets through
`others/script/Makefile`. **`make` is not installed on this Windows machine**, so invoke the
underlying scripts directly. All commands run from the repo root unless noted.

## 1. Build (generate / dedup / sort / check dicts + OpenCC)

Requires **Go** (present at `/d/GO/bin/go`). Regenerates derived files and validates them.

```bash
cd others/script && go mod tidy && go run . --rime_path "$(cd ../.. && pwd)" --auto_confirm
```

- **Takes ≥ 90 s.** Wait for it; do not assume it hung.
- What it does (`others/script/main.go`): updates Emoji from `others/emoji-map.txt` → `opencc/`,
  rebuilds cn/en mix from `others/cn_en.txt` → `en_dicts/*.txt`, auto-annotates pinyin for `ext`,
  sets weight 100 on `ext`/`tencent`, sorts & dedups, then runs `Check` / `CheckPolyphone`.
- **Warnings and errors from this build outrank the user request** (per AGENTS.md): you must fix
  what it reports before committing. Common checks — file `_type`: `8105`/`base`/`ext` need
  汉字+注音+权重; `tencent` needs 汉字+权重 and **must not** contain polyphones (多音字).
- Run it any time you touch a dictionary or a generated source. It auto-sorts/dedups, so you may
  add entries in any order and let the build normalize them.

## 2. Lint (YAML + Lua)

Requires `yamllint` and `luacheck` — **both missing locally**. Install first:

```bash
python3 -m pip install yamllint
luarocks install luacheck    # luarocks itself must be installed first
```

Then (works without `make`):

```bash
bash others/script/lint/run.sh all        # yaml + lua
bash others/script/lint/run.sh yaml-lint  # business YAMLs (skips *.dict.yaml, others/, .github/)
bash others/script/lint/run.sh lua-lint   # lua/**/*.lua via luacheck
```

Run lint after editing `default.yaml`, `weasel.yaml`, `squirrel.yaml`, any `*.schema.yaml`, or any
`lua/*.lua`. Lua **warnings** are tolerated (exit 0); Lua **errors** fail.

## 3. Smoke test (real Rime deployment via rime-cli)

```bash
bash others/script/smoke/run.sh rime_ice
```

Downloads `rime-cli` and deploys the config to catch load-time failures. In CI it's fed
`RIME_CLI_URL` / `RIME_CLI_CACHE_PATH`; locally it fetches the bundle on first run.

## Quick decision guide

| You edited…                                  | Run                          |
|----------------------------------------------|------------------------------|
| `cn_dicts/`, `en_dicts/`, `opencc/`, `others/cn_en.txt`, `others/emoji-map.txt` | build (then lint if also YAML) |
| `*.schema.yaml`, `default/weasel/squirrel.yaml` | lint                      |
| `lua/*.lua`                                   | lint                         |
| Anything before opening a PR                  | build + lint + smoke         |

Do **not** hand-edit generated files (`rime_ice.dict.yaml`, `melt_eng.dict.yaml`,
`en_dicts/*.txt`, `opencc/*.txt`); edit the source and rebuild. Never touch
`radical_pinyin.*` or `lua/search.lua` (synced from upstream `mirtlecn/rime-radical-pinyin`).
