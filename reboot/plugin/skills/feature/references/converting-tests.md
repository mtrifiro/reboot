---
title: Converting an Existing Test Suite to Feature Files
impact: MEDIUM
impactDescription: How `unittest` / `IsolatedAsyncioTestCase` tests become feature files without losing what they showed
tags: feature, conversion, unittest, migration
---

## Converting an Existing Test Suite

When an application has `unittest` / `IsolatedAsyncioTestCase`
tests (the pre-feature-file layout) and the user wants them as
feature files, or the `upgrade` skill's migration notes ask for it:

1. Read every test and list what each one shows, in English, one
   line per test.
2. **Group them into features by capability**, not by servicer or
   test file: a `test_bank.py` with deposits, withdrawals, and
   transfers becomes `deposits.feature`, `withdrawals.feature`, and
   `transfers.feature`. Where the grouping is not obvious, propose
   one and ask the user; do not guess at a business rule they did
   not state.
3. Follow the `feature` skill's steps 1 and 2 for each feature, then
   write the scenarios from the tests' calls and assertions in the
   built-in steps. A test's helper that the steps cannot express
   becomes a custom step, written as plain Reboot code
   (`../../python/references/testing-custom-steps.md`); a mock
   becomes an autouse fixture asserted through a one-line custom
   step.
4. Keep the tests that are not about the application's behavior:
   the crash-and-recover tests of
   `../../python/references/testing-failure-recovery.md` stay on the
   harness.
5. Run both until the scenarios cover the tests, then delete the
   converted tests. Leave every feature `@wip` until the user has
   reviewed the files, then ask to remove the tags.
