# Feature Specification: TradingView Connection Fix

**Feature Branch**: `007-tradingview-connection-fix`  
**Created**: 2026-05-02  
**Status**: Draft  
**Input**: User description: "Fix the connection issues in tradingview-mcp-jackson. The project fails to connect to port 9222 during E2E tests, which prevents the Model Context Protocol (MCP) server from interacting with the TradingView Desktop app."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reliable CDP Connection (Priority: P1)
As a trader using the MCP server, I want the system to automatically detect and connect to the TradingView Desktop debug port (9222) so that I can run my morning briefs and automated scripts without manual troubleshooting.

**Why this priority**: Core functionality of the project. Without a CDP connection, no tools will work.

**Independent Test**: Can be tested by running `tv_health_check` or `npm test` and verifying a successful connection log.

**Acceptance Scenarios**:
1. **Given** TradingView is running with the debug flag, **When** the MCP server starts, **Then** it establishes a stable WebSocket connection.
2. **Given** TradingView is NOT running, **When** a connection is attempted, **Then** the system provides a clear error message: "ECONNREFUSED - Please ensure TradingView is running with --remote-debugging-port=9222".

---

### User Story 2 - Sophisticated Retry & Fallback (Priority: P1)
As a user, I want the system to retry the connection if it fails initially (e.g., while TradingView is still loading) so that the server doesn't just crash on startup.

**Why this priority**: Enhances the robust nature of the client/server layer.

**Independent Test**: Can be tested by starting the MCP server *before* launching TradingView and verifying it eventually connects once the app is open.

**Acceptance Scenarios**:
1. **Given** a failed initial attempt, **When** retry logic is triggered, **Then** it uses exponential backoff to attempt reconnection up to 5 times.
2. **Given** 5 failed retries, **When** the threshold is met, **Then** it performs a fallback HTTP check to verify if the port is even reachable at a basic networking level.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST implement a WebSocket handler using the `ws` library or similar Node.js standard.
- **FR-002**: System MUST handle `ECONNREFUSED` and `ETIMEDOUT` errors specifically for port 9222.
- **FR-003**: System MUST implement exponential backoff for connection retries.
- **FR-004**: System MUST include a verification fallback that attempts a simple HTTP GET to `http://localhost:9222/json/version` to confirm if the CDP interface is active.
- **FR-005**: System MUST log all connection lifecycle events (Attempt, Success, Failure, Retry).

### Key Entities
- **Connection Manager**: The primary class responsible for the lifecycle of the WebSocket connection.
- **Debug Interface**: The Chrome DevTools Protocol endpoint provided by TradingView.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: 100% of E2E tests pass when TradingView is running in debug mode.
- **SC-002**: Reconnection occurs within 10 seconds of TradingView being launched if the server was already waiting.
- **SC-003**: Error logs provide a direct, clickable instruction for the user to resolve connection issues.

## Assumptions
- The user is running TradingView Desktop v2.14+.
- The Node.js environment has `npm` and `node` 18+ installed.
- The `launch_tv_debug_mac.sh` script is the intended way to start the app.
