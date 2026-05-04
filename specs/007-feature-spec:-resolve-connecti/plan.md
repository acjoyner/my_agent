# Implementation Plan: TradingView Connection Fix

**Branch**: `007-tradingview-connection-fix` | **Date**: 2026-05-02 | **Spec**: [specs/007-feature-spec:-resolve-connecti/spec.md]

## Summary
The goal is to implement a robust connection management layer for the `tradingview-mcp-jackson` project. This involves refactoring the current connection logic into a `ConnectionManager` class that handles retries, exponential backoff, and provides a secondary health-check mechanism via HTTP to ensure TradingView Desktop is accessible on port 9222.

## Technical Context

**Language/Version**: Node.js (v18+)
**Primary Dependencies**: `ws` (WebSockets), `node-fetch` or built-in `fetch`.
**Storage**: N/A (Transient connection state).
**Testing**: `npm test` (E2E and unit tests).
**Target Platform**: macOS/Windows/Linux running TradingView Desktop.

## Architectural Design

### 1. ConnectionManager Class
A new class will be implemented to encapsulate the WebSocket lifecycle.
- **`connect(maxRetries = 5)`**: Main entry point. Initiates the connection sequence.
- **`_attemptConnection()`**: Private method using the `ws` library to reach `localhost:9222`.
- **`_handleError(error)`**: Detects `ECONNREFUSED` and triggers the backoff/retry loop.
- **`checkPortAccessibility()`**: Performs a `GET` request to `http://localhost:9222/json/version` as a diagnostic fallback.

### 2. Exponential Backoff Logic
- **Initial Delay**: 500ms
- **Multiplier**: 2.0
- **Max Delay**: 8000ms
- **Behavior**: If all retries fail, output a "Troubleshooting Guide" with instructions to launch TradingView with the `--remote-debugging-port=9222` flag.

## Constitution Check
- **Passes**: Maintains modularity by isolating connection logic. Follows "Protocol-Based Communication" by ensuring the CDP connection is reliable.

## Project Structure

### Documentation (this feature)
```text
specs/007-feature-spec:-resolve-connecti/
├── plan.md              # This file
├── spec.md              # Functional requirements
└── tasks.md             # Implementation steps
```

### Source Code (affected paths)
```text
/Users/anthonyjoyner/Documents/Projects/tradingview-mcp-jackson/
├── src/connection.js    # Primary refactor target
└── src/server.js        # Integration point
```

## Pseudo-code: ConnectionManager

```javascript
class ConnectionManager {
  async connect() {
    for (let i = 0; i < this.maxRetries; i++) {
      try {
        await this._attemptWebSocket();
        return true;
      } catch (e) {
        if (e.code === 'ECONNREFUSED') {
          await this._verifyWithHTTP();
          await this._wait(this.calculateBackoff(i));
        }
      }
    }
    throw new Error("Could not connect to TradingView.");
  }
}
```
