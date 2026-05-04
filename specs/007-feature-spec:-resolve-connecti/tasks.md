# Tasks: TradingView Connection Fix

**Input**: Design documents from `/specs/007-feature-spec:-resolve-connecti/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

## Phase 1: Foundational (ConnectionManager Implementation)

- [ ] T001 [US1] Define `ConnectionManager` class in `src/core/ConnectionManager.js` (or refactor `src/connection.js`).
- [ ] T002 [US1] Implement `_attemptConnection()` using the `ws` library to target `localhost:9222`.
- [ ] T003 [US1] Implement `checkPortAccessibility()` using Node's `http` module to ping `http://localhost:9222/json/version`.

## Phase 2: User Story 1 - Reliable CDP Connection

- [ ] T004 [US1] Integrate `ConnectionManager` into `src/server.js` to replace the current direct connection logic.
- [ ] T005 [US1] Implement basic error logging that instructs the user to check the `--remote-debugging-port` flag.
- [ ] T006 [US1] Add a `tv_health_check` command to the CLI to trigger a manual connection test.

## Phase 3: User Story 2 - Sophisticated Retry & Fallback

- [ ] T007 [US2] Implement the exponential backoff algorithm in `ConnectionManager.connect()`.
- [ ] T008 [US2] Configure retry limits (default 5) and backoff timings (500ms initial, 2.0x multiplier).
- [ ] T009 [US2] [P] Implement the diagnostic HTTP fallback if all WebSocket retries fail.

## Phase 4: Verification & Polish

- [ ] T010 Run `npm test` and verify that `tests/e2e.test.js` passes when TradingView is running.
- [ ] T011 Verify that a clear "ECONNREFUSED" guide is shown when TradingView is NOT running.
- [ ] T012 Commit all changes and push to GitHub using the new `git_commit_and_push` skill.
