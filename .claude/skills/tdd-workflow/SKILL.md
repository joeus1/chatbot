---
name: tdd-workflow
description: Test-driven development workflow - use when writing new features, fixing bugs, or refactoring. Red-green-refactor with tests as the spec.
---

# TDD Workflow

Write the test before the code, every time the change has observable behavior.

## The cycle

1. **Red** - Write one small test expressing the next bit of required behavior. Run it. Watch it fail *for the right reason* (an assertion, not an import error). For bug fixes, this test is the reproduction: it must fail on the current code.
2. **Green** - Write the least code that passes. Hard-coding is fine for one cycle; the next test forces the generalization.
3. **Refactor** - Clean up names and duplication with the tests as a net. Run tests after each step.
4. Repeat until the requirement's edges are covered.

## What to test

- The happy path, then the edges that actually occur: empty/None, zero, negative, boundary lengths, duplicate submissions, out-of-order events, the error path and its message/status code.
- Behavior through the public interface (function return values, HTTP responses, DB state) - never private internals.
- One behavior per test, named for the behavior: `test_expired_subscription_blocks_checkout`, not `test_checkout_2`.

## Mocking rules

- Mock only system boundaries: network calls, clocks, payment providers, email/SMS, LLM APIs.
- Never mock the module under test or your own database layer in integration tests - use fixtures/scratch DBs.
- If mocking feels necessary everywhere, the design has too many hidden dependencies; inject them instead.

## Repo harnesses

- **Python**: `pytest` (see pyproject.toml for testpaths). Fixtures in `conftest.py`. Run the narrow file first (`pytest path/to/test_x.py`), full suite before committing.
- **Vite/React**: `npm test` (vitest) for units, `npm run test:e2e` (Playwright) for journeys. Testing Library queries by role/label, not test-ids, where possible.

## Definition of done

Full relevant suite green, new behavior covered including its failure modes, and no test weakened or skipped to get there.
