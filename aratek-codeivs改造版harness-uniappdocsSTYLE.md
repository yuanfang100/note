# Style Guide

## TypeScript and Vue

- Use TypeScript strict mode, `<script setup lang="ts">`, Composition API, and
  explicit types at module boundaries.
- Use `PascalCase` for components/types, `camelCase` for variables/functions, and
  `UPPER_SNAKE_CASE` for constants.
- Use `kebab-case` for files and directories. Page components may use `index.vue`
  inside a clear route directory.
- Do not use unexplained `any`, `@ts-ignore`, empty catches, or debug logging.

## UnoCSS

- UnoCSS handles layout, spacing, typography, colors, and responsive utilities.
- Use `unocss-applet` so generated styles are transformed for mini-program targets.
- Keep utility classes static. Use a mapping object for variants, for example
  `const statusClass = { active: 'text-primary', disabled: 'text-gray-400' }`.
- Put design tokens, reset rules, and cross-platform CSS fixes in `src/styles` or
  `uni.scss`, not in scattered page styles.

## Platform-Safe Styling

- Prefer `rpx`, flex, and UniApp-safe CSS. Avoid relying on H5-only selectors,
  `position: sticky`, viewport units, and unsupported CSS functions without a
  platform fallback.
- Do not target uview-plus private DOM structure. Use documented props, slots,
  variables, or a local wrapper component.
