# API Client Contract

## Client

Create one luch-request instance in `src/service/http.ts`. It owns base URL,
timeout, request IDs, authentication headers, response normalization, refresh-token
coordination, and transport error mapping. Feature API modules call that instance.

```ts
// api/user.ts
export const getProfile = () => http.get<Profile>('/profile')
```

Pages and components must not call `uni.request`, build URLs, or append tokens.

## Request Rules

- Read the base URL from a public `VITE_*` environment variable. Public variables
  must never contain secrets.
- Keep request and response DTOs in TypeScript types. Convert server DTOs into view
  models in the API/composable layer when required.
- Use `uni.uploadFile` or luch-request upload support for files; do not force binary
  uploads through a JSON client.
- Preserve cancellation handles for search-as-you-type, page unload, and duplicate
  requests where applicable.

## Error Handling

- Normalize network failure, timeout, 401, 403, validation, and business errors in
  the HTTP layer.
- Refresh authentication only once for concurrent 401 responses; replay only safe,
  authenticated requests after refresh succeeds.
- Business pages translate stable error `code` values into actionable messages.
  They must not branch on natural-language `message` values.
