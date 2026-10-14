# Security

## Configuration and Credentials

- Commit `.env.example`, never `.env` files containing credentials.
- All `VITE_*` values are public in the H5 bundle and must contain only public
  configuration.
- Do not log access tokens, passwords, phone numbers, identity data, or raw API
  responses containing personal data.

## Session Storage

- Keep access tokens short-lived. Store only what the platform requires and clear
  session data on logout or token invalidation.
- Treat `uni.setStorageSync` as device-local, not as a secure enclave. Avoid storing
  high-value secrets there when a platform-specific secure storage solution exists.
- Centralize token attachment and 401 handling in the luch-request client.

## Native Permissions and Data

- Request camera, location, album, microphone, and notification permissions only
  at the moment a user invokes the feature, with an explanation and fallback.
- Validate file size, MIME type, extension, and server-side content. Never trust a
  client-provided filename or MIME type.
- Conditional compilation must not expose development endpoints, test accounts, or
  debug menus in production targets.
