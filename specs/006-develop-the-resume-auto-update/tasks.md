# Tasks: Resume Auto-Updater

**Input**: Design documents from `/specs/006-develop-the-resume-auto-update/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

## Phase 1: Foundational Setup (GitHub & Doc Processing)

- [ ] T001 Install dependencies: `python-docx`, `pypdf`, `PyGithub`.
- [ ] T002 Implement `fetch_github_projects(username)` in `skills/resume_updater.py`.
- [ ] T003 Create `skills/resume_updater.py` and register it in `skills/__init__.py`.

## Phase 2: User Story 1 - GitHub Project Sync

- [ ] T004 Implement logic to extract repository names, descriptions, and primary languages from GitHub.
- [ ] T005 [P] Implement the `list_my_github_projects` tool for the agent to show fetched data.

## Phase 3: User Story 2 - Document Modification & Review Gate

- [ ] T006 Implement `propose_resume_bullets(repo_data)` using Gemma4 to generate professional descriptions.
- [ ] T007 [P] Implement the `update_resume_docx(bullets)` logic using `python-docx` to find and update the "Projects" section.
- [ ] T008 Implement the "Review Gate" tool `approve_resume_update` to manage user confirmation before writing to disk.

## Phase 4: Multi-Platform Export & Sync (PDF, Drive, Web)

- [ ] T009 Implement `export_to_pdf(docx_path)` to generate a mirrored PDF version.
- [ ] T010 [P] Integrate with existing Google Drive tools to upload both the `.docx` and `.pdf` files.
- [ ] T011 [Web] Implement `update_web_resume(project_data)` to modify `Projects.tsx` in the `resume-app` directory.
- [ ] T012 [Web] Implement `deploy_to_firebase()` to trigger `npm run build` and `firebase deploy` within the `resume-app` folder.
- [ ] T013 Create a "Resume Status" widget in `static/dashboard/index.html` to show the last update timestamp.

## Phase 5: Verification & Polish

- [ ] T014 Verify formatting preservation in the updated Word document.
- [ ] T015 [P] Test the full flow: Fetch -> Propose -> User Approve -> Save -> Sync to Drive -> Sync to Web.
- [ ] T016 Ensure the "Vanilla-First" principle is maintained for the dashboard widget.
