# Testing

## Required Coverage

- Unit-test API transforms, request interceptors, Pinia stores, validation rules,
  and composables with Vitest.
- Use uni-automator for critical mini-program flows: login, tab navigation, form
  submission, upload, permission denial, and recovery from failed requests.
- Verify H5, App, and intended mini-program output for every platform-sensitive
  feature. Browser success is not evidence of mini-program or App compatibility.

## Verification Matrix

| Change | Minimum verification |
| --- | --- |
| Pure utility/composable | Type check and unit test |
| UI component | H5 plus one target mini-program visual/interaction check |
| Navigation or storage | H5, mini-program, and App smoke test |
| Camera, location, file, payment, sharing, permissions | Relevant real device and host application |
| Request/authentication | Success, timeout, offline, 401, and business failure paths |

Do not disable assertions or remove tests to make a pipeline pass. Record any
platform that could not be tested and the remaining risk in the delivery note.
