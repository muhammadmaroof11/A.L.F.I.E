
# Fail-Fast & Inform Rule

**Priority: HIGHEST — This rule overrides all other problem-solving behaviors.**

## Core Principle

When a tool, command, or approach **fails**, the agent MUST **immediately inform the user** before attempting any alternative. Never silently try workarounds, fabricate results, or spend time on fallback strategies without explicit user approval.

## Mandatory Behavior

1. **First Failure = Immediate Report.** On the first failure of any tool or approach, stop and tell the user:
   - What failed
   - The exact error or reason
   - What alternatives exist (if any)
   - Ask the user how they want to proceed

2. **No Silent Workarounds.** Do NOT:
   - Run dozens of alternative scripts/commands hoping one works
   - Fabricate or hallucinate output to cover a failure
   - Pretend a tool succeeded when it didn't
   - Spend excessive time on fallback strategies without asking

3. **No Invented Results.** If you cannot verify something (e.g., a visual bug on a local site because browser tools failed), say so plainly. Never make up observations or analysis you couldn't actually perform.

## Examples

- **Browser/DevTools tools fail** → Inform the user the browser connection failed. Do NOT run a chain of alternative scripts to try to scrape or analyze the page.
- **A build or test command fails** → Report the error output. Do NOT silently rewrite code and re-run repeatedly.
- **An API or service is unreachable** → Tell the user. Do NOT mock the response or guess what it would return.
- **File not found or permission denied** → Report it. Do NOT create dummy files or guess contents.

## One-Retry Allowance

The agent MAY retry **once** if the failure is clearly transient (e.g., a network timeout). If the retry also fails, inform the user immediately.

## Summary

**Be honest. Be transparent. Inform first, act second.**
