# Tasks: Personal Dashboard UI Upgrade

**Input**: Design documents from `/specs/003-ui-upgrade-for-the-personal-da/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

## Phase 1: Setup & Foundation

- [ ] T001 Create `static/dashboard/` directory for the new UI assets.
- [ ] T002 Update `skills/dashboard.py` to serve the new static directory using `StaticFiles`.
- [ ] T003 [P] Define the Indigo/Dark CSS variables in `static/dashboard/style.css` (#4f46e5 primary, #111827 background).

## Phase 2: User Story 1 - Visual Overview (Responsive Grid)

- [ ] T004 Create `static/dashboard/index.html` with a base layout and a `<div id="dashboard-grid">` container.
- [ ] T005 Implement the CSS Grid layout in `style.css` (3-column desktop, 1-column mobile).
- [ ] T006 Add the "System Status" widget to the grid showing agent uptime.

## Phase 3: User Story 2 - Recent Jobs Feed (Interactive Cards)

- [ ] T007 Create `static/dashboard/main.js` to fetch data from `/dashboard/jobs`.
- [ ] T008 Implement the `renderJobCards(jobs)` function to dynamically create HTML cards for each job result.
- [ ] T009 [P] Style the `.job-card` component with hover effects and clear typography for title/company.

## Phase 4: User Story 3 - Widget Interaction

- [ ] T010 Add `onclick` handlers to job cards to open the source URL in a new tab.
- [ ] T011 [P] Implement a "Refresh" button on the jobs widget to trigger a re-fetch without reloading the page.

## Phase 5: Polish & Validation

- [ ] T012 Verify responsiveness across mobile, tablet, and desktop breakpoints.
- [ ] T013 [P] Ensure all code follows the "Vanilla-First" principle (no external JS libraries).
- [ ] T014 Run a final performance check to ensure the dashboard loads in <500ms.
