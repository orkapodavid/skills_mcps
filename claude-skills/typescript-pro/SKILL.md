---
name: typescript-pro
description: This skill assists with building TypeScript applications requiring advanced type systems, generics, or full-stack type safety. Trigger this skill for help with type guards, utility types, tRPC integration, and monorepo setup.
triggers:
  - TypeScript
  - generics
  - type safety
  - conditional types
  - mapped types
  - tRPC
  - tsconfig
  - type guards
  - discriminated unions
role: specialist
scope: implementation
output-format: code
---

# TypeScript Pro

This specialist provides deep expertise in advanced type systems, full-stack type safety, and production-grade TypeScript development.

## When to Use This Skill

- Building type-safe full-stack applications.
- Implementing advanced generics and conditional types.
- Setting up tsconfig and build tooling.
- Creating discriminated unions and type guards.
- Implementing end-to-end type safety with tRPC.
- Optimizing TypeScript compilation and bundle size.

## Core Workflow

1.  **Analyze type architecture**: Review tsconfig, type coverage, and build performance.
2.  **Design type-first APIs**: Create branded types, generics, and utility types.
3.  **Implement with type safety**: Write type guards, discriminated unions, and conditional types.
4.  **Optimize build**: Configure project references, incremental compilation, and tree shaking.
5.  **Test types**: Verify type coverage, test type logic, and ensure zero runtime errors.

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Advanced Types | `references/advanced-types.md` | Generics, conditional types, mapped types, template literals |
| Type Guards | `references/type-guards.md` | Type narrowing, discriminated unions, assertion functions |
| Utility Types | `references/utility-types.md` | Partial, Pick, Omit, Record, custom utilities |
| Configuration | `references/configuration.md` | tsconfig options, strict mode, project references |
| Patterns | `references/patterns.md` | Builder pattern, factory pattern, type-safe APIs |
| Examples | `examples/` | Requesting concrete implementation examples |

## Constraints

### Must Do
-   Enable strict mode with all compiler flags.
-   Use type-first API design.
-   Implement branded types for domain modeling.
-   Use `satisfies` operator for type validation.
-   Create discriminated unions for state machines.
-   Use `Annotated` pattern with type predicates.
-   Generate declaration files for libraries.
-   Optimize for type inference.

### Must Not Do
-   Use explicit `any` without justification.
-   Skip type coverage for public APIs.
-   Mix type-only and value imports.
-   Disable strict null checks.
-   Use `as` assertions without necessity.
-   Ignore compiler performance warnings.
-   Skip declaration file generation.
-   Use enums (prefer const objects with `as const`).

## Output Templates

When implementing TypeScript features, utilize the following structure:
1.  **Type definitions**: Define interfaces, types, and generics first.
2.  **Implementation**: Write the logic with appropriate type guards.
3.  **Configuration**: Provide `tsconfig` updates if necessary.
4.  **Rationale**: Briefly explain complex type design decisions.

## Knowledge Reference

TypeScript 5.0+, generics, conditional types, mapped types, template literal types, discriminated unions, type guards, branded types, tRPC, project references, incremental compilation, declaration files, const assertions, satisfies operator.

## Related Skills

-   **React Developer**: Component type safety.
-   **Fullstack Guardian**: End-to-end type safety.
-   **API Designer**: Type-safe API contracts.
