<!--
Sync Impact Report
- Version change: [none] → 1.0.0
- Modified principles:
  - [PRINCIPLE_1_NAME] → Single-Responsibility Modules
  - [PRINCIPLE_2_NAME] → Simplicity Over Features (YAGNI)
  - [PRINCIPLE_3_NAME] → Testable, Isolated Code
  - [PRINCIPLE_4_NAME] → Explicit Boundaries & Dependencies
  - [PRINCIPLE_5_NAME] → Consistent Style & Readability
- Added sections:
  - Clean Code Constraints for a Small Project
  - Development Workflow & Quality Gates
- Removed sections:
  - None
- Templates:
  - .specify/templates/plan-template.md: ✅ updated/aligned (Constitution Check references gates generically)
  - .specify/templates/spec-template.md: ✅ aligned with Clean Code focus
  - .specify/templates/tasks-template.md: ✅ aligned (emphasizes incremental, testable work)
  - .specify/templates/commands/*.md: ⚠ pending (no command templates defined; add if new workflows are introduced)
- Deferred TODOs:
  - TODO(GUIDANCE_FILE): define runtime development guidance document (e.g., docs/quickstart.md)
-->

# CV Constitution

## Core Principles

### I. Single-Responsibility Modules

Each module, class, and function MUST have **one single reason to
change**. Domain, infrastructure, and presentation responsibilities
MUST be clearly separated. Functions SHOULD be small, with names that
express intent and no hidden side effects. When a function starts to do
more than one thing, it MUST be split into smaller functions.

**Rationale**: A small project stays simple and easy to evolve when each
part has a clear responsibility, reducing coupling and making testing
and maintenance easier.

### II. Simplicity Over Features (YAGNI)

The project MUST stay **small and simple by default**. Only features
that are needed now, based on real usage scenarios, MAY be implemented.
Layers, abstractions, or frameworks introduced “for the future only”
are forbidden. External dependencies MUST be kept to the minimum
necessary and chosen only when they bring clear and immediate benefit.

**Rationale**: Applying YAGNI avoids accidental complexity, reduces dead
code, and lowers the cognitive load needed to understand and modify the
system.

### III. Testable, Isolated Code

Code MUST be written so that it is **easily testable in isolation**.
Rule of thumb:

- Business rules SHOULD be pure functions or use injected dependencies.
- Access to IO (database, network, filesystem) MUST be encapsulated in
  clear interfaces or adapters.
- Whenever possible, automated tests SHOULD be added for critical
  behaviors before or right after implementation.

**Rationale**: In a small project, a lean but focused test suite
provides safety to refactor, keep Clean Code, and evolve without fear of
regressions.

### IV. Explicit Boundaries & Dependencies

Boundaries between layers (for example, domain, infrastructure,
presentation) MUST be explicit. Dependencies MUST be clear, injected
when possible, and MUST NOT be hidden in global singletons or implicit
shared state. Domain code MUST NOT depend directly on framework details
or external library internals.

**Rationale**: Well-defined boundaries reduce coupling, make testing and
replacement of implementation details easier, and prevent the project
from growing in an unstructured way.

### V. Consistent Style & Readability

Code MUST be **easy for any team member to read and follow**. This
includes:

- Descriptive names for variables, functions, and files.
- Consistent formatting (configured and enforced lint/formatter).
- No commented-out code or dead code.
- Comments only when the “why” is not obvious from the code.

**Rationale**: In a small project, consistency and clarity are more
valuable than premature optimizations. Clean code reduces onboarding
time and the risk of bugs introduced by misunderstandings.

## Clean Code Constraints for a Small Project

This section defines constraints that ensure the project stays small,
simple, and aligned with Clean Code.

- **Limited scope**: Each feature MUST be small and deliver isolated
  value. If a feature feels too large, it SHOULD be split into smaller
  stories.
- **Few layers**: Use only the layers that are actually needed (for
  example, domain + infrastructure + a simple interface). Avoid
  overengineering such as multiple levels of “services”, “managers”, and
  “facades” without a real need.
- **Minimal dependencies**: Before adding a new library, verify that it
  is truly indispensable and does not introduce complexity
  disproportionate to its benefit.
- **No premature optimization**: Measure first, optimize later. Clarity
  is prioritized over micro-optimizations.
- **Simple folder structure**: Keep a shallow hierarchy, with folders
  named by responsibility (for example, `domain/`, `infra/`, `ui/` or
  the equivalent in the chosen language).

## Development Workflow & Quality Gates

This project follows a development workflow oriented toward simplicity
and quality:

1. **Specify behavior** in natural language (user stories and acceptance
   criteria).
2. **Define a simple code structure** to support the behavior, respecting
   the boundaries between domain and infrastructure.
3. **Implement the smallest possible solution** that satisfies the
   acceptance criteria, applying the Clean Code principles in this
   constitution.
4. **Add tests** for happy paths and critical scenarios.
5. **Refactor safely** using tests as a safety net.

Any significant change MUST pass through the following **quality gates**:

- Code follows the principles of single responsibility and simplicity.
- No unnecessary dependencies are introduced.
- Code remains testable in isolation.
- Readability and agreed style are preserved.

## Governance

This constitution is the primary reference for design, structure, and
code quality decisions in this project.

- **Precedence**: When there is a conflict between previous practices
  and this constitution, the constitution prevails.
- **Revisions**: Changes to the constitution MUST be made via a
  dedicated pull request, with a clear description of motivations and
  impact.
- **Semantic versioning**:
  - **MAJOR**: Backward-incompatible changes to the rules (removal or
    redefinition of fundamental principles).
  - **MINOR**: Addition or material expansion of principles or sections.
  - **PATCH**: Text, clarity, or wording fixes that do not change the
    semantics of the rules.
- **Periodic review**: The constitution SHOULD be revisited whenever the
  project scope grows significantly or, at a minimum, at major milestones
  (for example, main releases).
- **Runtime guide**: TODO(GUIDANCE_FILE): define a practical document
  (for example, `docs/quickstart.md`) with concrete examples of how to
  apply these principles day to day.

**Version**: 1.0.0 | **Ratified**: 2026-03-10 | **Last Amended**: 2026-03-10
