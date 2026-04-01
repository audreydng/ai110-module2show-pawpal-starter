# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML used four core classes: `Task`, `Pet`, `Owner`, and `Scheduler`.
`Task` represented one care activity with priority and duration.
`Pet` stored pet profile data and owned a list of tasks.
`Owner` stored owner-level constraints and managed multiple pets.
`Scheduler` was the orchestration layer that ranked tasks and produced a daily plan.

**b. Design changes**

Yes, the design changed during implementation.
I added `due_time` and `due_date` to `Task` so sorting and conflict checks were explicit instead of inferred.
I also added `Owner.get_pet()` and `Scheduler.filter_tasks()` to keep lookup/filter logic centralized and reduce repetitive UI code.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler currently considers daily time budget, task priority, completion status, due time ordering, and simple conflict checks.
I treated time budget and priority as highest importance because they directly control whether essential care tasks fit into a realistic day.

**b. Tradeoffs**

My scheduler uses lightweight conflict detection that only flags exact same-time collisions (same date + same `HH:MM`) rather than calculating full interval overlaps.
This is less comprehensive than overlap math, but it is reasonable here because it is easy to explain, fast, and catches the most obvious owner-facing scheduling mistakes.

---

## 3. AI Collaboration

**a. How you used AI**

I used Copilot for architecture brainstorming, class skeleton generation, algorithm ideation, and test drafting.
The most helpful prompts were concrete and scoped, such as asking for sorting by `HH:MM`, recurring task rollover logic using `timedelta`, and edge-case test ideas for conflict detection.

**b. Judgment and verification**

One suggestion implied adding deeper overlap-detection complexity immediately.
I rejected that for this iteration and kept exact-time conflict checks to preserve readability and maintainability.
I verified the chosen behavior with targeted automated tests and by running the terminal demo to inspect warnings.

Using separate chat sessions for design, implementation, and testing helped me stay organized by reducing context switching and keeping each phase focused on one decision type.
The biggest takeaway is that AI is strongest as a fast collaborator, but I still need to act as lead architect by setting scope boundaries, choosing tradeoffs, and validating output with tests.

---

## 4. Testing and Verification

**a. What you tested**

I tested task completion, task addition to pets, chronological sorting, recurring task rollover, conflict detection, and the no-task edge case.
These tests are important because they cover both the core happy path and common failure points in scheduler behavior.

**b. Confidence**

I am moderately high confidence (4/5) based on passing automated tests and successful terminal/UI smoke checks.
Next, I would add tests for overlapping-duration conflicts, invalid/duplicate pet names, and more advanced recurrence patterns.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the clear separation of concerns across `Task`, `Pet`, `Owner`, and `Scheduler`, which made feature additions straightforward.

**b. What you would improve**

In another iteration, I would redesign scheduling to use true time intervals and add configurable optimization goals (for example, shortest-total-time vs highest-priority-first).

**c. Key takeaway**

My key takeaway is that strong system design comes from deliberate boundaries: AI can generate options quickly, but architecture quality depends on human decisions about simplicity, clarity, and verification.
