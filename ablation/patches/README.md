# Patches against the SWE-Debate fork

`swe-debate/` is gitignored, so the instrumented fork's own history is not backed up by
this repository. Every change made to it is exported here as a patch so the fork can be
reconstructed from upstream and so chat can read what was changed without the working copy.

Upstream: https://github.com/YerbaPage/SWE-Debate
Base commit: `8a7d46263e7bea4cd6563c19166b7592ac386b13` ("renew supplementary")
Local branch: `a3062-instrumented`

To rebuild the fork from scratch:

```bash
git clone https://github.com/YerbaPage/SWE-Debate swe-debate
cd swe-debate
git checkout -b a3062-instrumented 8a7d46263e7bea4cd6563c19166b7592ac386b13
git am ../ablation/patches/swe-debate-instrumentation.patch
```

Regenerate the patch after committing further changes in the fork:

```bash
cd swe-debate && git format-patch --stdout 8a7d462..HEAD > ../ablation/patches/swe-debate-instrumentation.patch
```

| patch | what it does |
|---|---|
| `swe-debate-instrumentation.patch` | Makes the hardcoded LLM endpoint, model name and cache paths environment-configurable (see notes/deviations.md 2026-09-20). No algorithm changes. |
