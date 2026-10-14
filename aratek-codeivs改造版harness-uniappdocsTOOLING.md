# Tooling

The repository uses pnpm. The current `package.json` is an initialization stub;
the following scripts are the required target interface after bootstrap.

| Purpose | Target script |
| --- | --- |
| H5 development | `pnpm dev:h5` |
| WeChat mini-program development | `pnpm dev:mp-weixin` |
| App development | `pnpm dev:app` |
| Production builds | `pnpm build:h5`, `pnpm build:mp-weixin`, `pnpm build:app` |
| Type check | `pnpm typecheck` |
| Lint and formatting check | `pnpm lint`, `pnpm format:check` |
| Unit tests | `pnpm test:unit` |
| Mini-program automation | `pnpm test:e2e` |

Use the UniApp CLI and Vite plugin supplied by the project. HBuilderX may be used
for App packaging and device debugging, but versions must be documented when they
affect output or compatibility. Do not add a tool solely for H5 if its behavior
cannot be verified on the supported mini-program and App targets.
