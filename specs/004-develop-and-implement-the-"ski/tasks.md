# Tasks: Skills Analytics

**Input**: Design documents from `/specs/004-develop-and-implement-the-"ski/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

## Phase 1: Data Persistence (Foundational)

- [ ] T001 [US1] Define `SkillLog` model in `skills/dashboard.py` using SQLModel.
- [ ] T002 [US1] Update `init_db()` in `dashboard.py` to ensure the `skill_log` table is created.
- [ ] T003 [US1] Implement a function `log_skills(skill_list, source)` to persist skill data to SQLite.

## Phase 2: Backend Aggregation Logic

- [ ] T004 [US2] Create a utility function in `skills/dashboard.py` to scan the `output/` directory for JSON files.
- [ ] T005 [US2] Implement frequency analysis using `collections.Counter` to identify trending skills.
- [ ] T006 [US3] Create the FastAPI endpoint `GET /dashboard/analytics/skills` to return the aggregated data.

## Phase 3: Dashboard Integration (Frontend)

- [ ] T007 [US3] Add a "Trending Skills" widget container to `static/dashboard/index.html`.
- [ ] T008 [US3] Update `static/dashboard/main.js` to fetch data from the new analytics endpoint.
- [ ] T009 [US3] Implement a `renderSkillChart(data)` function to visualize trends using simple CSS bars or SVG.

## Phase 4: Verification & Polish

- [ ] T010 Verify that running a new job search automatically updates the analytics feed.
- [ ] T011 [P] Ensure the UI remains responsive and follows the Indigo/Dark theme.
- [ ] T012 Run a final performance check on the aggregation logic with 10+ JSON files.
