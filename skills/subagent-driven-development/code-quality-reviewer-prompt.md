# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent.

**Purpose:** Verify implementation is well-built (clean, tested, maintainable)

**Only dispatch after spec compliance review passes.**

```
Agent tool (general-purpose):
  description: "Review code quality for Task N"
  prompt: |
    Review the code changes between [BASE_SHA] and [HEAD_SHA].

    ## What Was Implemented

    [From implementer's report]

    ## Review Focus

    - Does each file have one clear responsibility?
    - Are units decomposed so they can be understood and tested independently?
    - Is the implementation following the file structure from the plan?
    - Did this change create large files or significantly grow existing files?
    - Code readability, naming, error handling
    - Test quality (testing real behavior, not mocks)
    - No unnecessary complexity (YAGNI)

    ## Report

    - **Strengths:** What was done well
    - **Issues:** Critical / Important / Minor (with file:line references)
    - **Assessment:** Approved or needs fixes
```
