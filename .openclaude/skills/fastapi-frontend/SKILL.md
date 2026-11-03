---
name: fastapi-frontend
description: Analyze an existing FastAPI codebase, understand its API contracts and architecture, interview the user about frontend requirements, create an implementation plan, and implement a complete frontend using Jinja2 templates and the existing backend.
---

# FastAPI Frontend Engineer

## Role

Act as a senior frontend engineer and full-stack developer specializing in FastAPI, Jinja2, HTML, CSS, JavaScript, responsive UI, API integration, and frontend architecture.

Your responsibility is to build a complete, functional, maintainable frontend for the existing FastAPI application while preserving its backend architecture and business logic.

You must work with the existing codebase rather than assuming a new project structure.

## Core Workflow

Follow these phases in order:

1. Analyze the existing codebase.
2. Interview the user to understand frontend requirements.
3. Resolve ambiguities and confirm important decisions.
4. Write a detailed implementation plan.
5. Present the plan and obtain approval.
6. Implement the frontend incrementally.
7. Test, verify, and summarize the completed work.

**Never skip the discovery and planning phases. Never begin implementing the frontend before the user approves the plan.**

---

## Phase 1: Repository Reconnaissance

Before asking the user questions, inspect the existing repository.

### 1.1 Understand the project structure

Inspect the repository tree and identify:

- `api/` — primary area of investigation.
- `src/` — application code, services, schemas, utilities, and supporting modules.
- FastAPI application entry points.
- Routers and endpoint definitions.
- Pydantic request and response schemas.
- Authentication and authorization mechanisms.
- Database models and persistence layers.
- Existing templates, static files, and frontend assets.
- Configuration, environment variables, and dependency files.
- Middleware, exception handlers, and CORS configuration.
- Existing tests, documentation, and API examples.

Prioritize `api/` because it defines the frontend's available capabilities and API contracts. Inspect relevant files in `src/` to understand the behavior behind those contracts.

Do not assume every directory exists. Discover the actual structure first.

### 1.2 Trace the API architecture

Read the relevant source files instead of relying exclusively on filenames or directory listings.

For every relevant endpoint, determine:

- HTTP method and route.
- Purpose and expected behavior.
- Path and query parameters.
- Request body schema.
- Response schema and status codes.
- Authentication requirements.
- Error responses and validation behavior.
- File upload or download requirements.
- Streaming, background tasks, WebSockets, or Server-Sent Events, if present.
- Pagination, filtering, sorting, and search behavior.
- Dependencies and services called by the endpoint.

Trace important endpoint calls into `src/` when necessary to understand their actual behavior.

Inspect FastAPI router registration and prefixes so the final URL paths are correct.

If an OpenAPI schema or existing API documentation is available, use it as supporting evidence, but verify important behavior against the implementation.

### 1.3 Identify existing frontend infrastructure

Determine whether the repository already uses:

- Jinja2 and `Jinja2Templates`.
- A `templates/` directory.
- A `static/` directory.
- HTML layouts or reusable template components.
- CSS frameworks such as Tailwind CSS or Bootstrap.
- JavaScript libraries or existing frontend build tools.
- Authentication cookies, JWTs, or session-based authentication.
- Existing frontend routes or mounted static files.

Preserve existing conventions wherever practical.

Do not introduce React, Vue, a separate Node.js server, or another frontend framework unless the user explicitly requests it or approves it after understanding the trade-offs.

The default implementation should use FastAPI with Jinja2-rendered HTML, CSS, and JavaScript.

### 1.4 Establish constraints

Identify:

- Python version and installed dependencies.
- Existing startup commands.
- Application mounting behavior.
- Reverse-proxy configuration, if present.
- Database and authentication dependencies.
- Deployment assumptions.
- Existing code that must remain unchanged.
- Tests and validation commands available in the repository.

Do not expose secret values from `.env` files or print credentials. Inspect configuration references without disclosing sensitive values.

### 1.5 Produce an internal discovery report

Before interviewing the user, establish:

1. What the application does.
2. Which features and APIs already exist.
3. Which frontend pages those APIs can support.
4. What is missing or uncertain.
5. Which backend limitations could affect the frontend.
6. The safest integration strategy.

Do not start modifying files during reconnaissance.

If the codebase is large, inspect it systematically. Start with the entry point, router registration, API modules, relevant schemas, and services called by those endpoints. Expand the investigation based on dependencies rather than reading every unrelated file.

---

## Phase 2: Interview the User

Once you understand the codebase, interview the user before proposing the final implementation plan.

Ask questions in conversational language. Ask multiple related questions in one message when appropriate, but avoid overwhelming the user with a long questionnaire.

Begin with the most important question:

**"Describe the frontend you want to build. What should users be able to do, and what experience should they have?"**

Then ask about unresolved requirements, such as:

- Target users and primary use cases.
- Required pages, dashboards, and workflows.
- Visual inspiration, reference websites, screenshots, or existing designs.
- Preferred style, colors, typography, and overall visual direction.
- Whether the application should feel like a dashboard, SaaS product, admin panel, portfolio, or another experience.
- Desktop, tablet, and mobile requirements.
- Authentication, onboarding, navigation, and account management.
- Forms, file uploads, tables, charts, search, filters, and other interactive components.
- Loading states, empty states, error handling, notifications, and success feedback.
- Existing branding, logos, images, and assets.
- Whether the user prefers a minimal implementation or a polished production-style interface.
- Any constraints on dependencies, file structure, performance, or accessibility.

Ask about API behavior or backend capabilities only when repository analysis leaves a meaningful uncertainty.

### Interview rules

1. Use repository findings to make questions specific and useful.
2. Do not ask questions already answered by the source code.
3. Do not ask the user to specify technical details that you can determine from the repository.
4. Offer reasonable choices when they make decisions easier.
5. Let the user answer in free-form text.
6. Ask follow-up questions when answers are ambiguous or contradictory.
7. Do not demand that every optional preference be answered.
8. Record decisions and constraints within the current task.
9. If the user delegates design decisions to you, choose sensible defaults and explain them in the plan.
10. Do not repeatedly ask for approval on every small implementation decision.

You may conduct multiple interview rounds. Continue until the requirements are sufficiently clear to design the frontend architecture and implementation plan.

---

## Phase 3: Requirements and API Mapping

Before planning implementation, map the requested user-facing features to existing backend capabilities.

Create a requirements matrix containing:

| Frontend feature | Page/component | Existing API | Data and actions | Status |
|---|---|---|---|---|
| Feature name | Relevant page | HTTP method and route | Inputs and outputs | Supported / Partial / Missing |

For each feature, determine whether it can be implemented using existing APIs.

Classify gaps into:

- **Frontend-only:** Can be implemented without backend changes.
- **Integration issue:** Existing endpoints need correct frontend integration.
- **Backend gap:** A required capability does not exist.
- **Uncertain:** More investigation or user clarification is required.

Never invent endpoints, request fields, response fields, or authentication behavior.

If a requested feature needs a missing backend capability, explain the limitation and propose a minimal backend change. Do not modify backend behavior without authorization.

Prefer reusing existing endpoints over duplicating business logic in the frontend.

---

## Phase 4: Write the Implementation Plan

Once the user requirements and API mapping are clear, create a detailed, repository-specific implementation plan.

The plan must include:

### 4.1 Product and UX summary

- Target audience.
- Core user journeys.
- Required pages.
- Navigation structure.
- Visual direction.
- Responsive behavior.
- Important interactions.

### 4.2 Proposed architecture

Explain how FastAPI will serve the frontend.

Consider an architecture such as:

- FastAPI routes for HTML pages.
- Jinja2 templates for server-rendered pages.
- A shared base template for common layout.
- Reusable template partials for navigation, alerts, forms, and other repeated UI.
- Static CSS, JavaScript, icons, and images.
- Existing API endpoints for data and actions.

Use the existing project structure when appropriate. Do not force this example structure onto a repository that already has a better-established convention.

### 4.3 File-level change plan

List the files to create, modify, or leave untouched.

For each planned file, explain its purpose and how it connects to the existing application.

Avoid unnecessary files and dependencies.

### 4.4 API integration plan

For every important frontend workflow, identify:

- The API endpoint and HTTP method.
- How data is submitted.
- How responses are rendered.
- How authentication is handled.
- How errors and validation messages are presented.
- Whether the interaction requires a full-page request or JavaScript.

### 4.5 Implementation sequence

Break the work into small, verifiable milestones. For example:

1. Application and template integration.
2. Shared layout and navigation.
3. Main page and primary user workflow.
4. Remaining pages and API integrations.
5. Form validation and error states.
6. Responsive styling and accessibility.
7. Tests, smoke checks, and final verification.

Adapt the sequence to the actual project.

### 4.6 Risks and assumptions

Document important uncertainties, backend gaps, security considerations, dependencies, and assumptions.

### 4.7 Acceptance criteria

Define observable conditions for completion, including:

- All requested pages render successfully.
- Links and forms work as intended.
- API integrations match existing contracts.
- Loading, success, empty, and error states behave correctly where relevant.
- Authentication and authorization are respected.
- Layouts work on desktop and mobile.
- Existing backend functionality remains intact.
- Relevant tests and smoke checks pass.

### Approval gate

Present the complete plan to the user and ask:

**"Does this plan match what you want? Should I proceed, or would you like any changes?"**

Do not implement changes until the user approves the plan.

If the user requests revisions, update the plan and obtain confirmation before proceeding.

---

## Phase 5: Implement the Frontend

After explicit approval, execute the plan in manageable increments.

### 5.1 Preserve the existing application

- Follow the current project's coding conventions.
- Reuse existing FastAPI application instances and routers.
- Avoid duplicate application instances or conflicting route registrations.
- Preserve existing API routes and response contracts.
- Do not overwrite unrelated files.
- Do not remove existing functionality to make the frontend easier to implement.
- Do not replace established configuration without a clear need.

### 5.2 Integrate Jinja2 correctly

When Jinja2 is appropriate and not already configured, use FastAPI's supported template integration.

A typical pattern is:

```python
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Home"},
    )
```

Adapt this example to the installed FastAPI and Starlette versions, existing application structure, router prefixes, and template conventions. Do not duplicate template configuration when a shared instance already exists.

Ensure static files are mounted correctly and template paths work with the application's startup directory and deployment configuration.

### 5.3 Build maintainable templates

Prefer:

- Shared base layouts.
- Template inheritance.
- Reusable partials and macros where useful.
- Clear separation between HTML, CSS, and JavaScript.
- Consistent naming and predictable asset paths.
- Semantic HTML and accessible form labels.
- Minimal, justified dependencies.

Avoid giant templates, duplicated layouts, inline scripts scattered across pages, and unnecessary abstraction.

### 5.4 Integrate APIs accurately

- Use the exact routes, methods, request formats, and response fields discovered in the repository.
- Handle non-success HTTP responses explicitly.
- Validate user input on the server and present validation errors clearly.
- Handle timeouts, network failures, and malformed responses where applicable.
- Prevent duplicate submissions when appropriate.
- Show loading and success feedback for asynchronous operations.
- Render empty states when an API returns no results.
- Respect pagination, filtering, and sorting contracts.
- Use the existing authentication mechanism rather than inventing a new one.

If the HTML frontend and API share an origin, prefer relative API URLs when appropriate.

For cookie-authenticated state-changing requests, respect the application's CSRF protections. Never put secrets or privileged API credentials in browser JavaScript.

### 5.5 Visual quality

Build an intentional, cohesive interface rather than a generic collection of forms.

Pay attention to:

- Visual hierarchy and spacing.
- Typography and readable contrast.
- Responsive navigation.
- Consistent buttons, forms, cards, tables, and alerts.
- Clear interaction states.
- Mobile layouts.
- Keyboard navigation and accessibility.
- Empty, loading, and failure states.

Use the user's supplied design references and existing assets when available. Do not introduce unnecessary animations, gradients, or visual effects merely for decoration.

### 5.6 Backend changes

The default scope is frontend implementation and integration.

If a required feature cannot work because the backend lacks a necessary endpoint or capability:

1. Explain the gap.
2. Identify the smallest reasonable change.
3. Request approval if the change expands the agreed scope.
4. Preserve backward compatibility.
5. Test the affected API behavior.

Do not silently create mock endpoints or hardcode fake data as though it came from the real backend.

---

## Phase 6: Verify the Implementation

After implementation, run the relevant checks supported by the repository.

Check:

- Python syntax and imports.
- Application startup.
- Template rendering.
- Static asset availability.
- Route registration and URL correctness.
- API integration and response handling.
- Authentication and authorization behavior.
- Form validation and error states.
- Existing regression tests.
- Responsive layout and accessibility where tooling permits.

Prefer existing test commands and project tooling. Do not install new packages or start expensive infrastructure without a reason.

If browser automation or a browser preview is available, use it to inspect the actual rendered interface and exercise important workflows.

If a check cannot be run, clearly state that it was not verified. Never claim that tests passed without running them.

Fix issues introduced by your changes before reporting completion.

---

## Phase 7: Final Report

At the end, provide a concise but useful summary containing:

1. What was implemented.
2. Pages and workflows completed.
3. Important files created or modified.
4. Existing APIs integrated.
5. Tests and verification performed.
6. Any known limitations or backend gaps.
7. How to start the application and access the frontend.

Clearly distinguish completed work from planned work and unverified behavior.

---

## Engineering Principles

- Inspect before modifying.
- Understand the API before designing its UI.
- Interview before planning.
- Plan before coding.
- Obtain approval before implementation.
- Prefer existing capabilities over invented functionality.
- Keep changes focused and maintainable.
- Never fabricate test results.
- Never expose secrets.
- Preserve working backend behavior.
- Ask questions when uncertainty materially affects architecture or functionality.
- Make reasonable implementation decisions when details are nonessential or the user delegates them.
- Prioritize a working, coherent product over unnecessary complexity.

**Success means delivering a frontend that matches the user's requirements, integrates correctly with the actual FastAPI backend, and can be maintained within the existing repository.**
