---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session
---

# Subagent-Driven Development

Execute plan by dispatching fresh subagent per task, with two-stage review after each: spec compliance review first, then code quality review.

**Why subagents:** Delegate tasks to specialized agents with isolated context. By precisely crafting their instructions and context, you ensure they stay focused. They should never inherit your session's context — you construct exactly what they need.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration

## When to Use

- Have an implementation plan with mostly independent tasks
- Want to stay in the current session (not a parallel session)
- Tasks can be dispatched one at a time without tight coupling

## The Process

1. **Read plan, extract all tasks** with full text and context
2. **Per task:**
   - Dispatch implementer subagent (see `./implementer-prompt.md`)
   - Handle status: DONE → review, NEEDS_CONTEXT → provide and re-dispatch, BLOCKED → assess and re-dispatch or escalate
   - Dispatch spec compliance reviewer (see `./spec-reviewer-prompt.md`)
   - If issues: implementer fixes → re-review → repeat until approved
   - Dispatch code quality reviewer (see `./code-quality-reviewer-prompt.md`)
   - If issues: implementer fixes → re-review → repeat until approved
   - Mark task complete
3. **After all tasks:** dispatch final code reviewer for entire implementation

## Model Selection

Use the least powerful model that can handle each role:

- **Mechanical tasks** (isolated functions, clear specs, 1-2 files): use Haiku or Sonnet
- **Integration tasks** (multi-file coordination, debugging): use Sonnet
- **Architecture and review tasks**: use Opus

**Task complexity signals:**
- Touches 1-2 files with complete spec → cheap model
- Touches multiple files with integration concerns → standard model
- Requires design judgment or broad codebase understanding → most capable model

## Handling Implementer Status

**DONE:** Proceed to spec compliance review.

**DONE_WITH_CONCERNS:** Read concerns before proceeding. If about correctness/scope, address first. If observations, note and proceed.

**NEEDS_CONTEXT:** Provide missing context and re-dispatch.

**BLOCKED:** Assess: context problem → provide more context; task too complex → re-dispatch with more capable model; task too large → break into pieces; plan wrong → escalate to human.

**Never** ignore an escalation or force the same model to retry without changes.

## Red Flags

**Never:**
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed issues
- Dispatch multiple implementation subagents in parallel (conflicts)
- Make subagent read plan file (provide full text instead)
- Skip scene-setting context
- **Start code quality review before spec compliance is approved**
- Move to next task while either review has open issues

**If reviewer finds issues:**
- Implementer (same subagent) fixes them
- Reviewer reviews again
- Repeat until approved
- Don't skip the re-review

## Advantages

- Fresh context per task (no confusion)
- Self-review catches issues before handoff
- Two-stage review: spec compliance then code quality
- Spec compliance prevents over/under-building
- Review loops ensure fixes actually work
