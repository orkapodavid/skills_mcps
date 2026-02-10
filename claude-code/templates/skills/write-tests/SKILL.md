---
name: write-tests
description: Write comprehensive tests for a module or file.
  Use when you need to add test coverage.
argument-hint: "[filepath]"
allowed-tools: Read, Write, Bash, Grep
---

Write tests for `$ARGUMENTS`:

1. Read the source file thoroughly
2. Identify all testable functions, methods, and edge cases
3. Create test file at the conventional location:
   - Python: `tests/test_<basename>.py`
   - TypeScript: `__tests__/<basename>.test.ts`
4. Write tests using the project's framework:
   - Python: pytest with fixtures, parametrize, mock
   - TypeScript: jest or vitest
5. Cover:
   - Happy path for each public function
   - Edge cases (empty input, None/null, boundaries)
   - Error conditions (exceptions, invalid input)
   - Integration points (mock external deps)
6. Run the tests to verify they pass:
   - Python: `uv run pytest tests/test_<basename>.py -v`
   - TypeScript: `npm run test -- <basename>`
