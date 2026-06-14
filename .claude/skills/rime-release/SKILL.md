---
name: rime-release
description: Package and release the 雾凇拼音 (rime-ice) config — how the nightly and stable GitHub releases are produced, the [build] commit trigger, the zip artifact layout, and how to cut a release tag. Use when asked to build release artifacts, cut a version, or understand/modify the release pipeline.
---

# rime-release — packaging & releasing rime-ice

Releases are produced by `.github/workflows/release.yml` (job *Test and Release*) on
`ubuntu-24.04`, gated to `github.repository == 'iDvel/rime-ice'`. Pipeline order:
**lint → smoke → (optional) build → pack zips → publish release → (optional) commit built files.**

## Triggers

- **Push to `main`** → runs lint + smoke + pack, publishes/updates the **`nightly`** release
  (`make_latest: true`). This is what end users download as `full.zip`.
- **Push a tag matching `[0-9]+.*`** (e.g. `1.2.0`) → publishes a **draft stable** release for
  that tag. Edit the draft's notes, then publish manually.
- **`workflow_dispatch`** → manual run (also forces the Go build step).

## The `[build]` trigger

The Go regeneration step (`go run . --rime_path … --auto_confirm`) only runs when the head commit
message contains ` [build]` **or** the run is `workflow_dispatch`. When it runs and produces
changes, CI commits them back as `build(ci): auto build for -> <msg> <-` and pushes.
→ Append ` [build]` to a commit message when your change requires regenerating derived dict files
in CI. Routine dict edits that you already rebuilt locally don't need it.

## Artifact layout (the zips)

Built into `dist/` and attached to the release:

| Zip                              | Contents                                                        |
|----------------------------------|----------------------------------------------------------------|
| `full.zip`                       | all root `*.lua`/`*.yaml`/`*.txt` + `cn_dicts en_dicts lua opencc LICENSE` |
| `all_dicts.zip`                  | `cn_dicts en_dicts opencc radical_pinyin.dict.yaml`            |
| `cn_dicts.zip` / `en_dicts.zip` / `opencc.zip` | the respective dict dirs                         |
| `fcitx5_rime_js-rime_ice.zip`    | `build lua opencc custom_phrase.txt` (for fcitx5-rime.js)     |

## Cutting a stable release

```bash
git tag 1.2.0          # tag name must match ^[0-9]+.*
git push origin 1.2.0  # CI builds the draft stable release
gh release list        # find the draft, edit notes, then publish
```

Update `others/docs/Changelog.md` for user-facing changes before tagging.

## Local packaging (rare)

CI uses `zip`, which is **not installed on this Windows machine**. To pack locally use PowerShell
`Compress-Archive` instead, or rely on CI. Releasing itself requires `gh` (present) with push
rights to `iDvel/rime-ice`; on a fork CI is skipped by the `repository` guard.

Validate with **rime-build** (lint + smoke must pass) before tagging — CI runs them first and will
fail the release otherwise.
