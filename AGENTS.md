# Core Rules

## Shell

- **CRITICAL**: do not **EVER** run `git` commands, with these exceptions:
    - Read-only inspection is always allowed: `git diff` (any flags/paths) and `git status`.
    - `git add` and `git commit` are allowed **only** when the user explicitly asks for a commit - never autonomously, never as a side effect of another task.
    - Everything else that mutates history or remotes (checkout, reset, rebase, push, branch -D, stash drop, etc.) stays forbidden.

## TypeScript

- **NEVER** use `any` or `as` casting
- Explicit type annotations **ONLY** when needed (inlined data, function params, etc)
- **NEVER** `is` type guards in `.filter` - narrowing is automatic
- **ALWAYS** `const` for functions, not `function`
- **NO** region-dividing comments unless explicitly requested
- **ALWAYS** kebab-case for files
- **Avoid untyped Zod `.parse()`**: Don't use `schema.parse(untypedValue)` to bypass TypeScript - it silently erases the type-checking bridge between layers. Use `.parse()` only at true system boundaries (files parsing, user input, etc). For internal data, let TypeScript enforce the mapping - if types don't align, fix the types, don't `.parse()` them away.

## Code Style

### Prefer declarative over imperative

- **Avoid `let` + loops**: use `.find()`, `.map()`, `.filter()`, `.reduce()`, `.some()`, `.every()`, `.flatMap()` instead of `let` + `for` loops when possible.
- **NEVER** `.forEach()` - use `for(const x of arr)` when a loop is needed.
- **Avoid manual array building**: instead of `const arr = []; if (x) arr.push(...)`, use `[x ? mapX(x) : undefined, y ? mapY(y) : undefined].filter(defined)`.
- **Ternary over simple if/else**: for simple conditional assignments, prefer ternary operators. Avoid when they hurt readability (nested ternaries).
- **Prefer `const`**: use `let` only when mutation is truly unavoidable. Build data with expressions (ternary, spread, array methods), not statements (if/push/reassign).

### Comments

- **Write timeless comments**: describe the code as it is **now**. Never narrate history or transitions ("changed to X", "previously we...", "now...") - that's what `git` is for. This is valid for both JSDoc and inline comments.

#### JSDoc: what gets one

| Declaration                        | Rule                                                                                    |
| ---------------------------------- | --------------------------------------------------------------------------------------- |
| Class methods                      | **ALWAYS**, except trivial forwarders, trivial private helpers                          |
| Top level functions                | **ALWAYS**, except trivial forwarders, trivial private helpers                          |
| Top level helper types             | **ONLY** function-like helpers with generics, **NEVER** interfaces/interface-like types |
| Top level consts, class attributes | **ONLY** when something non-trivial needs saying (through `@remarks`)                   |

**NOTHING** else gets one

#### JSDoc: how to write it

**Allowed tags - closed set. The order below is the order in the block, no exceptions.**

| Order | Tag            | When                                                                                        |
| ----- | -------------- | ------------------------------------------------------------------------------------------- |
| 1     | `@template`    | One per type parameter, in order: name + **SMALL** description. **NO** re-stating `extends` |
| 2     | `@param`       | One per parameter, in order: name + **SMALL** description. **NO** types                     |
| 3     | `@description` | **ALWAYS**, exactly one                                                                     |
| 4     | `@remarks`     | **ONLY** a **REAL** caveat about using **this** declaration                                 |
| 5     | `@example`     | **ONLY** when the call shape or output is genuinely non-obvious                             |

**Language - telegraphic:**

- `@description` opens with a third-person verb, no subject: "Builds...", "Returns...". Never "This function..." or "Build...".
- One sentence. No filler ("simply", "basically", "just", "note that"), no hedging.
- Same term for the same concept:
    - **Returns** (pure derivation)
    - **Builds** (constructs data)
    - **Maps** (transforms)
    - **True when** (predicate)
    - **Fetches** (network/DB read)
    - **Persists** (DB write)

Use telegraphic (no filler, impersonal, same-term/same-concept) language in **ALL** comments, not just `@description` tags.

#### Inline comments (inside bodies)

- **Default to none**: prefer self-explanatory names and structure over comments. Don't restate code, don't add ceremony.
- **Be concise**: one short line where it genuinely adds something. Explain the **why** (non-obvious intent, a subtle constraint), not the **what** the code already states.
- Allowed **ONLY** when the reader **must** see the note at that exact line to not get it wrong, and it cannot live anywhere else. **MUST** also adhere to telegraphic language.

### Pattern matching: ts-pattern

- Use `.exhaustive()` by default - compile-time exhaustiveness checking catches missing cases.
- Use `.otherwise()` only when a genuine default/fallback is needed (e.g., unknown external input, catch-all logging). Don't use it to skip handling known cases.
- Don't overuse for trivial 2-branch conditions - a simple ternary or `if` is fine there.
- `.returnType<T>()` when: return type needs `as const`, or type already exists/is reusable.
- `.returnType` set -> no `as const` in branches.

### Results

- When a function can fail, use the `Result` type

### Utilities: es-toolkit

- Use `es-toolkit` for all utility operations that it supports

## Checklist

**CRITICAL**: before yielding control, run **exactly** this - nothing more, nothing less:

```
pnpm checklist
```
