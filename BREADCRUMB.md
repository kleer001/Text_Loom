fresh

## Summary

Security sweep of Text_Loom, driven by the Dependabot alert backlog. All work is
committed and pushed to branch `claude/dependabot-security-updates-3hccjk`
(3 commits, `d341018` → `7c7a25a`, based on `main` @ `3a46ed6`).

Done and verified:
- Cleared all 10 npm advisories in `src/GUI` (7 high, 1 moderate, 2 low) via
  `npm audit fix`. Lockfile-only change; `package.json` untouched.
- Hardened GitHub Actions, Docker, and added a Dependabot config.
- Fixed 2 tests that hung on an interactive prompt. Suite is now 73/73 green.

The remaining items below are things I could **not** verify or complete in the
remote container. They need a local machine.

## Todos

### Parallel

- [ ] #1 **Verify the Docker image actually builds and runs.** No Docker daemon
  was available in the remote session, so every `docker/Dockerfile` and
  `docker/docker-compose.yml` change is **unverified**. Run:
  `docker build . -f docker/Dockerfile -t textloom-verify`
  then `cd docker && docker compose up`.
  Confirm: the build succeeds, the app starts as user `textloom` (not root),
  and `curl http://127.0.0.1:8000/` responds.

- [ ] #2 **Watch for a `/workspace` volume permission failure.** The container
  now runs as unprivileged `textloom` (uid/gid 1000) instead of root, and
  `chmod 777 /workspace` was removed. Docker preserves the ownership of a
  *pre-existing* named volume, so an old `textloom-workspace` volume created
  under the root image will still be root-owned and the new user may not be
  able to write to it. If you hit permission errors:
  `docker volume rm textloom-workspace` and let it be recreated.
  Only relevant if you have run the old image before.

- [ ] #3 **Decide whether the localhost port binding is right for you.**
  `docker-compose.yml` now publishes `127.0.0.1:8000:8000` and
  `127.0.0.1:5173:5173` instead of binding all interfaces. This intentionally
  breaks LAN/remote access to the container. If you need to reach it from
  another machine, revert those two lines — but read #5 first, because the API
  has no authentication.

- [ ] #4 **Close Dependabot PR #115.** It bumps only axios/yaml/postcss, and its
  axios target (1.15.0) is itself vulnerable now. Fully superseded by `d341018`,
  which took axios to 1.19.0 and cleared all 10 alerts.
  https://github.com/kleer001/Text_Loom/pull/115

- [ ] #5 **Add authentication to the FastAPI server.** Not started — this is
  design work, not a quick fix. There is currently **no auth of any kind** on
  `src/api`: no `Depends`, no API key, no session check. Combined with
  `GET /api/v1/files/browse`, which lists the server user's home directory,
  anything that can reach port 8000 can browse your filesystem. Binding to
  loopback (#3) is a mitigation, not a fix. This matters the moment the API is
  meant to run anywhere but localhost.

- [ ] #6 **Confirm CI is green on the branch.** `.github/workflows/main.yml` was
  rewritten and has not run yet — see Context for why it never actually ran
  before. Expect `pytest src/tests` → 73 passed. If it fails, it is most likely
  a `PYTHONPATH` issue in the Actions runner rather than a real test failure.

### Sequential

- [ ] #7 (needs: #1) **Open a PR for the branch** if you want one. I did not
  create one — no PR has been opened for this work. Worth landing #1 first so
  the Docker changes are known-good before review.

## Context

**Branch:** `claude/dependabot-security-updates-3hccjk` — pushed, 3 commits ahead
of `main`. No PR opened.

**Commits:**
- `d341018` — npm advisories. axios 1.13.6→1.19.0 (direct), plus transitive
  vite 7.3.2→7.3.6, postcss 8.5.6→8.5.26, esbuild→0.28.2, form-data→4.0.6,
  js-yaml→4.3.1, nanoid→3.3.18, brace-expansion, yaml→1.10.3, @babel/core.
  Verified: `npm audit` → 0 vulnerabilities; `npm run build` produced
  byte-identical bundle hashes; `npm run lint` unchanged at 23 pre-existing errors.
- `2963fec` — CI/Docker hardening + new `.github/dependabot.yml`.
- `7c7a25a` — test fix.

**Both GitHub workflows were silently broken before this branch** — worth knowing
because it means the PR test gate has never actually run:
- `main.yml` installed from `path/to/requirements-file.txt` (literal placeholder,
  does not exist) and ran `src/corelauto_testing.py` (does not exist; the real
  file is `src/core/auto_testing.py`).
- `docker-image.yml` built `--file Dockerfile`, but the Dockerfile lives at
  `docker/Dockerfile`. That workflow is also effectively dead — it triggers on
  branch `"mainXXX"`, which looks deliberate. **Left as-is; change it if you want
  Docker builds gated in CI.**

Both now declare `permissions: contents: read` and `persist-credentials: false`.

**`npm install` → `npm ci` in the Dockerfile** matters more than it looks: with
`npm install`, image builds could resolve fresh versions and quietly bypass the
security pins in the lockfile.

**Test fix approach (`7c7a25a`):** `test_reset_tokens` and `test_repl_workflow`
called `reset_tokens()`, which prompts via `input()` at
`src/repl/helpers.py:254`. Under pytest's output capture that raises
`OSError: reading from stdin while output is captured`. The prompt is *correct*
behaviour for an interactive REPL helper, so the tests mock it rather than
changing production code — a `confirmed_reset_prompt()` context manager patching
`builtins.input` to `'y'`. `src/repl/helpers.py` was not modified. The file's
standalone `main()` entry point still runs clean at 5/5.

**Verified clean, no action needed** (checked, so don't re-scan): no committed
secrets — `.env.example` is placeholders only; CORS uses a fixed localhost origin
list, not a wildcard; `/files/browse` correctly `resolve()`s then
`relative_to(home)` and validates symlink targets; workspace import/export uses
temp files with no user-controlled paths; no `dangerouslySetInnerHTML` in the
frontend; no `pickle` / `yaml.load` / `shell=True`; `pip-audit` on
`requirements.txt` is clean (all `>=` specifiers, resolves to current versions).

**Local test setup:** the container's system Python could not install
`requirements.txt` (`Cannot uninstall PyJWT 2.7.0, RECORD file not found` —
Debian-managed package). Used a venv instead. To reproduce:
`python -m venv .venv && .venv/bin/pip install -r requirements.txt pytest`
then `PYTHONPATH=$PWD/src .venv/bin/python -m pytest src/tests -q`.

**Pre-existing issues left alone** (out of scope, not regressions): 23 eslint
errors in `src/GUI/src` (`no-explicit-any`, react-refresh) — identical count
before and after the dependency bumps; several `DeprecationWarning: invalid
escape sequence` in `src/core` (`chunk_node.py:10`, `section_node.py:283`) —
`src/core` is protected by CLAUDE.md, so these are **reported, not fixed**.

## Next Step

Start with #1 — build the Docker image locally. It is the only change in this
branch that could not be verified at all, and #7 depends on it.

/home/user/Text_Loom
