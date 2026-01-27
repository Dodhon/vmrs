---
name: planning
description: Create development plans for this repo. Use when the user asks for a plan or when switching into planning mode; ensures plans are written to dev_plans/ and include required sections + best-practice references.
---

# Planning Skill

Create development plans for this repo.

## Instructions

When this skill is invoked:

1. **Write plans to `dev_plans/`** (repo-relative).
2. **Research best practices** relevant to the feature and include **exact references (links)** from credible sources (official docs, reputable engineering blogs, high-quality GitHub repos). You must start with an extensive search
3. **Ensure every new plan includes**:
   1. **End user context** - who the feature is for (role, technical level, goals). Also include reference to github issue or pull request (ad hoc)
   2. **Functional requirements** - specific capabilities/behaviors the system must provide (clear, testable statements)
   3. **Non-functional requirements** - performance, reliability, security, privacy, cost, operability, compliance, UX constraints, etc. (clear, testable where possible)
   4. **Architecture diagram** - ASCII art showing how the feature fits into the existing system
   5. **Goals** - what the plan intends to achieve
   6. **Non-goals** - what is explicitly out of scope
   7. **Success metrics** - how we'll know it worked (measurable where possible). This includes the testing approach
4. **Validate** everything. Search online, again, to see if your draft follows industry standards and best practices
5. **Draft** a pull request when you are done. This requires user approval.

### Diagram conventions (required when the plan touches system behavior)
- Include **both**:
  - **High-level** diagram: C4 **Level 1: System Context**
  - **Low-level** diagram: C4 **Level 2: Containers + data stores** (explicitly call out storage like local files, e.g. `HitL_local/.../<id>.json`)
- For behavior/flows, also include a short **runtime** section (arc42 **Runtime View**) describing the key scenarios step-by-step.
