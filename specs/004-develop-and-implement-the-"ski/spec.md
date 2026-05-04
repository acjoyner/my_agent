# Feature Specification: Skills Analytics

**Feature Branch**: `004-skills-analytics`  
**Created**: 2026-04-30  
**Status**: Draft  
**Input**: User description: "Develop and implement the 'Skills Analytics' feature. Track skill growth in SQLite (dashboard.db), identify 'Trending Skills' across job searches, and provide a JSON endpoint for dashboard visualization."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Skill Growth Tracking (Priority: P1)
As a user, I want the system to automatically log the skills mentioned in my job searches and analyses so that I can track my competency development over time.

**Why this priority**: Core persistence requirement that enables all other analytics.

**Independent Test**: Can be tested by running a skill gap analysis and verifying a new entry appears in the `skill_log` table in SQLite.

**Acceptance Scenarios**:
1. **Given** a new skill gap report is generated, **When** processed by the system, **Then** an entry is added to `skill_log` with skill name, level, and timestamp.

---

### User Story 2 - Trending Skills Identification (Priority: P1)
As a user, I want to see a list of the most frequently required skills from my recent job searches so that I know what to focus my learning on.

**Why this priority**: Provides the primary "Intelligence" value of the feature.

**Independent Test**: Can be tested by calling the analytics endpoint and verifying it returns a count-based ranking of skills found in the `output/jobs` folder.

**Acceptance Scenarios**:
1. **Given** multiple job search result files exist, **When** analytics is triggered, **Then** the system returns a JSON object of skills ranked by frequency.

---

### User Story 3 - Analytics JSON Endpoint (Priority: P2)
As a developer, I want a standardized JSON API that provides pre-aggregated skills data so that I can render a "Skills Progress" chart on the dashboard.

**Why this priority**: Decouples the frontend visualization from the complex backend aggregation logic.

**Independent Test**: Can be tested by hitting `GET /dashboard/analytics/skills` and verifying the JSON structure matches the dashboard's requirements.

**Acceptance Scenarios**:
1. **Given** historical data exists in the database, **When** the analytics endpoint is queried, **Then** it returns a time-series or ranked list of skills.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST create and manage a `skill_log` table in `dashboard.db` using SQLModel.
- **FR-002**: System MUST implement a Python utility to parse all JSON files in `output/jobs/` and `output/skills/`.
- **FR-003**: System MUST identify "Trending Skills" by calculating the occurrence frequency of skill keywords across all search records.
- **FR-004**: System MUST provide a new FastAPI route `/analytics/skills` under the dashboard skill prefix.
- **FR-005**: All output MUST be in a standardized JSON format.

### Key Entities
- **Skill Entry**: A record of a single skill detection (skill_name, source, timestamp).
- **Skill Report**: An aggregated summary of skill trends and user gaps.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Aggregation of 100 job search records completes in under 2 seconds.
- **SC-002**: Analytics endpoint successfully identifies the top 10 most frequent skills with 100% accuracy based on stored records.
- **SC-003**: Data persistence is verified with 0% data loss across session restarts.

## Assumptions
- The system will use the existing `dashboard.db` SQLite file.
- The `Vanilla-First` principle applies: visualization will use native HTML/CSS or lightweight SVG (no heavy React-based charting libraries).
- Skills are extracted from the `matched_skills` and `missing_skills` fields of existing JSON output.
