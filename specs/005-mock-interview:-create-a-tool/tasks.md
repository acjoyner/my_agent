# Tasks: Automated Interview Preparation

**Input**: Design documents from `/specs/005-mock-interview:-create-a-tool/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

## Phase 1: Foundational (Database & Infrastructure)

- [ ] T001 Define `InterviewHistory` model in `skills/dashboard.py` using SQLModel.
- [ ] T002 Update `init_db()` in `dashboard.py` to ensure the `interview_history` table is created.
- [ ] T003 Create `skills/interview_prep.py` and register it in `skills/__init__.py`.

## Phase 2: User Story 1 - Tailored Question Generation

- [ ] T004 Implement `get_trending_skills()` logic in `interview_prep.py` by querying `SkillLog`.
- [ ] T005 Implement the `generate_mock_interview` tool using Gemma4 to create 5 questions based on trending skills.
- [ ] T006 [P] Create a tool `start_interview_session` to initialize a new attempt in the database.

## Phase 3: User Story 2 - Voice-Enabled Interview Mode

- [ ] T007 Update `static/index.html` to add an "Interview Mode" toggle/overlay.
- [ ] T008 Implement the JS controller to sequence questions: Speak Question -> Activate Mic -> Capture Answer.
- [ ] T009 [P] Add a "Next Question" voice trigger or button to proceed through the 5-question set.

## Phase 4: User Story 3 - Performance Scoring

- [ ] T010 Implement the `score_interview_answer` tool using Gemma4 to compare user input against `RESUME_TEXT`.
- [ ] T011 Create the backend logic to aggregate the 5 scores into a final "Interview Readiness" report.
- [ ] T012 [P] Store the final score and AI feedback in the `interview_history` table.

## Phase 5: Dashboard Integration & Polish

- [ ] T013 Create an "Interview Performance" widget in `static/dashboard/index.html`.
- [ ] T014 Update `static/dashboard/main.js` to render the history of scores and feedback.
- [ ] T015 Run a final E2E test: Start Interview -> Answer via Voice -> View Score on Dashboard.
