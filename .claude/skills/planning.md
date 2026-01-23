---
name: planning
description: Create development plans for this repo. Use when the user asks for a plan or when switching into planning mode; ensures plans are written to dev_plans/ and include required sections + best-practice references.
---

# Planning Skill

Create development plans for this repo.

## Instructions

When this skill is invoked:

1. **Write plans to `dev_plans/`** (repo-relative).
2. **Research best practices** relevant to the feature and include **exact references (links)** from credible sources (official docs, reputable engineering blogs, high-quality GitHub repos).
3. **Ensure every new plan includes**:
   1. **End user context** - who the feature is for (role, technical level, goals)
   2. **User requirements** - what the end user needs to accomplish and why
   3. **Architecture diagram** - ASCII art showing how the feature fits into the existing system
   4. **Goals** - what the plan intends to achieve
   5. **Non-goals** - what is explicitly out of scope
   6. **Success metrics** - how we'll know it worked (measurable where possible)

### Diagram conventions (required when the plan touches system behavior)
- Include **both**:
  - **High-level** diagram: C4 **Level 1: System Context**
  - **Low-level** diagram: C4 **Level 2: Containers + data stores** (explicitly call out storage like local files, e.g. `HitL_local/.../<id>.json`)
- For behavior/flows, also include a short **runtime** section (arc42 **Runtime View**) describing the key scenarios step-by-step.
