---
name: tech-design-doc
description: >
  Write Technical Design Documents (TDDs) — the architectural blueprints that explain how a system or feature will be built.
  Use this skill whenever someone asks to write a TDD, create a technical design document, draft a design spec, document a technical proposal, or plan system architecture on paper.
  Also trigger when someone says "write a TDD" (meaning Technical Design Document, not test-driven development), "design doc", "tech spec", "system design document", or "architectural design doc".
  Do NOT use for PRDs (product requirements) or ADRs (architecture decision records) — those have their own skills.
user-invocable: true
---

# Technical Design Documentation (TDD)

A TDD is the blueprint that shows *how* a system or feature will be built before a single line of production code is written. It makes design decisions transparent, aligns stakeholders before implementation begins, and gives future engineers (human or AI) the context needed to understand, maintain, and extend the system.

This skill walks you through creating a TDD by asking the right questions first, then generating a document with exactly the sections that are useful — no mandatory filler.

---

## The Job

1. Ask 3–5 essential clarifying questions to understand the design space
2. Generate a structured TDD with the relevant sections
3. Save to `docs/design/tdd-[feature-name].md`

**Important:** Do NOT start implementing. Just create the document.

---

## Step 1: Clarifying Questions

Before writing anything, ask the most important questions where the prompt leaves gaps. Keep it to 3–5 questions with lettered options so the user can respond quickly (e.g., "1A, 2C, 3B").

Focus on:

- **Scope**: Is this a new system, a feature addition, or a refactor?
- **Audience**: Who are the primary readers — engineers, product managers, execs?
- **Depth**: High-level architecture overview, or full implementation blueprint?
- **Context**: Does a current solution exist that this replaces or extends?
- **Urgency**: Is this for planning, stakeholder review, or handoff to implementers?

### Format Questions Like This

```
1. What is the scope of this design?
   A. Brand new system/service (greenfield)
   B. New feature within an existing system
   C. Refactor or replacement of existing functionality
   D. Other: [please specify]

2. Who is the primary audience?
   A. Engineers implementing the feature
   B. Engineering + product stakeholders
   C. Broad audience including exec/leadership
   D. Internal reference only (no review needed)

3. How deep should this go?
   A. Architecture overview — components, data flow, key decisions
   B. Full implementation blueprint — schemas, APIs, test plan, rollout
   C. Just the essentials to unblock implementation
```

---

## Step 2: Choose Sections

Not every TDD needs every section. After understanding the context, include sections that add value and omit the rest. Use this guide:

| Section | When to include |
|---|---|
| Introduction | Always |
| Objectives | Always |
| Glossary | When domain-specific terms need definition |
| Background | When context is not obvious from the title |
| Non-Goals | Always — prevents scope creep |
| Future Goals | When there's a clear next phase or roadmap |
| Assumptions | When the design depends on things outside your control |
| Solution | Always — this is the core |
| Further Considerations | For production systems (security, privacy, cost, risk) |
| Success Evaluation | When measurable outcomes matter |
| Work | When implementation planning is needed |
| Deliberation | When alternatives were considered or reviewers will ask "why not X?" |
| End Matter | When referencing prior work or external sources |

---

## Step 3: TDD Structure

### 1. Introduction

Metadata at the top. Always include:

```markdown
| Field | Value |
|---|---|
| **Feature** | [Name of the feature or system] |
| **Author** | [Your name] |
| **Created** | [Date] |
| **Last Updated** | [Date] |
| **Reviewers** | @person1, @person2 |
| **Status** | Draft / In Review / Approved |
```

### 2. Objectives

What are you trying to achieve, and why does it matter? Objectives should be SMART — Specific, Measurable, Achievable, Relevant, Time-bound.

Write bullet-point goals that could serve as success criteria later. Examples:

- *Reduce average search latency from 5–7s to under 500ms for 95% of queries*
- *Enable independent deployment of the customer profile service without affecting the billing pipeline*
- *Achieve 99.9% uptime for payment processing within 6 months of launch*

### 3. Glossary

Define terms, acronyms, or project-specific jargon that a newcomer would need explained. Especially useful when the TDD will be read outside the immediate team.

### 4. Background

Set the stage:

- **Problem Statement**: What is broken or missing? Quantify where possible.
- **Motivation**: Why solve this now? Business drivers, user pain, strategic priority.
- **Current State** *(if applicable)*: The existing system — its design, limitations, and pain points.
- **Related Projects** *(if applicable)*: Other initiatives this connects to.
- **Key Stakeholders**: Who is affected or invested.

### 5. Non-Goals

Explicitly state what this design does NOT address. This is one of the highest-value sections — it prevents scope creep and unspoken assumptions from becoming arguments later.

Examples:
- *This design does not cover advanced ML-based recommendation algorithms — those are planned for a future phase.*
- *Authentication infrastructure is out of scope; this design assumes the existing OAuth2 service.*

### 6. Future Goals

What comes after this? Mention planned phases, deferred features, or architectural evolution without committing to them now. This gives readers a sense of where the system is headed and helps them make forward-compatible decisions.

### 7. Assumptions

What are you taking for granted? Surface implicit dependencies so they can be validated. Examples:

- *The existing User Service API will maintain response times under 100ms*
- *AWS cloud access with Lambda and DynamoDB provisioning will be approved before project start*
- *Key third-party libraries will remain backward-compatible for at least 12 months*

### 8. Solution

This is the core of the TDD. Break it into sub-sections as needed:

#### a) Current Solution *(if replacing something)*

Brief description of what exists, why it was built that way, and why it's no longer adequate. Justify the need for the new design.

#### b) Proposed Solution

The full technical design. Include as many of the following as are relevant:

- **High-Level Architecture**: Block diagram or component map describing the main pieces and how they relate. If you can't include a diagram, describe the architecture in prose that could generate one.
- **Component Design**: For each major component — its responsibilities, interfaces, and key behaviors.
- **Data Model**: Schemas, entity relationships, storage choices, migration strategy.
- **Technology Stack**: Languages, frameworks, databases, cloud services, third-party libraries.
- **Interaction Flows**: How components communicate for key user or system actions (use sequence diagrams or numbered steps).

#### c) Business Logic

Translate business rules into technical behavior: how specific inputs produce specific outputs, decision trees, state machines, validation rules, and any non-trivial algorithms.

#### d) Presentation Layer *(if the TDD covers UI/UX)*

Frontend framework, component structure, how the UI consumes the backend APIs, styling approach.

#### e) Test Plan

How the solution will be validated before reaching production:

- Types of testing (unit, integration, e2e, performance, UAT)
- Tools and frameworks
- Coverage targets
- Test environment and data strategy

#### f) Monitoring & Alerting Plan

What gets observed once the system is live:

- Key metrics (latency, error rate, throughput, resource usage)
- Log strategy (format, destination, retention)
- Alert thresholds and notification channels (PagerDuty, Slack, etc.)
- Dashboards and distributed tracing

#### g) Deployment Plan

How the solution moves from code to production:

- Deployment strategy (blue/green, canary, phased rollout)
- CI/CD pipeline and tools
- Deployment checklist
- Traffic cut-over approach

#### h) Rollback Plan

What happens if the deployment fails:

- Triggers that initiate a rollback
- Step-by-step reversion procedure
- Data integrity during rollback
- Who gets notified

#### i) Alternate Solutions

Other technical approaches that were considered and rejected. For each:

- Brief description of the alternative
- Pros and cons
- Why it was not chosen

This section is often what reviewers want most — it shows rigor and prevents "why didn't you just use X?" questions in review.

### 9. Further Considerations

Address the broader implications of the design. Include sub-sections that apply:

- **Impact on Other Teams**: Which teams are affected? What coordination is needed?
- **Third-Party Services**: External dependencies, integration risks, vendor lock-in, rate limits.
- **Cost Analysis**: Infrastructure costs, licensing, development effort, savings vs. current state.
- **Security**: Auth/authz, encryption, input validation, secrets management, compliance (GDPR, HIPAA, PCI-DSS).
- **Privacy**: PII handling, data retention, consent, right-to-deletion.
- **Regional Considerations**: Data residency, multi-region deployment, legal variation by locale.
- **Accessibility**: WCAG compliance, keyboard navigation, screen reader support.
- **Operational Considerations**: Backup/DR, capacity planning, maintenance windows, incident procedures.
- **Risks**: Technical, operational, and project risks with mitigation strategies.
- **Support Considerations**: Support channels, SLAs, documentation, escalation paths.

### 10. Success Evaluation

Connect back to the Objectives. Define:

- **Impact**: Qualitative outcomes — what will be better, solved, or unlocked?
- **Metrics**: Quantitative KPIs with baselines and targets. For each metric: what it measures, current baseline, target, how it's measured, and when.

### 11. Work

The project execution plan:

- **Work Estimates & Timelines**: Effort per component, projected start/end dates, assumptions.
- **Prioritization**: P1/P2/P3 features with rationale, dependencies between them.
- **Milestones**: Key delivery checkpoints with dates.
- **Future Work**: Deferred items explicitly out of scope for this phase.

### 12. Deliberation

- **Discussion**: Key design debates, trade-offs made, why certain approaches were favored over others.
- **Open Questions**: Unresolved decisions, external dependencies pending clarification, things that need someone's input before implementation can proceed.

### 13. End Matter

- **Related Work**: Other TDDs, services, or documentation that this connects to.
- **References**: External docs, RFCs, articles, or internal wiki pages consulted.
- **Acknowledgements**: Key contributors and reviewers.

---

## Writing Principles

These make the difference between a TDD that gets read and one that collects dust:

**Be concrete.** "Improve performance" is not a goal. "Reduce p95 latency from 5s to 500ms" is. Numbers and examples are almost always better than vague statements.

**Show your reasoning, not just your conclusions.** Explain *why* you chose a particular database, framework, or architecture. Future engineers (and LLMs) making changes need to understand the constraints and trade-offs that shaped the design.

**Diagrams beat walls of text.** For architecture, use block diagrams. For flows, use sequence diagrams or numbered steps. If you can't include visuals, write prose that a diagramming tool could consume.

**Non-goals are as important as goals.** Every experienced reviewer will ask what's out of scope. Answer that question proactively.

**The Alternate Solutions section is what separates a great TDD from a mediocre one.** Showing that you considered other approaches — and explaining why you rejected them — builds trust and preempts objections.

**Tailor the depth to the audience.** A TDD for senior engineers who will implement it needs more implementation detail. A TDD for leadership review needs more context and impact framing.

---

## Output

- **Format:** Markdown (`.md`)
- **Location:** `docs/design/`
- **Filename:** `tdd-[feature-name].md` (kebab-case)

If `docs/design/` doesn't exist, create it.

---

## Checklist

Before saving the TDD:

- [ ] Asked clarifying questions with lettered options
- [ ] Included all sections relevant to this design; skipped sections that add no value
- [ ] Objectives are SMART (specific, measurable, achievable, relevant, time-bound)
- [ ] Non-Goals section is present and clearly scoped
- [ ] Solution section includes enough detail for an implementer to start work
- [ ] Alternate Solutions section explains what was considered and why rejected
- [ ] No placeholder text remains — every included section has real content
- [ ] Saved to `docs/design/tdd-[feature-name].md`
