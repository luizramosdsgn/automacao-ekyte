## 2026-03-31 - Module-level Regex Pre-compilation in Text Formatting
**Learning:** Recompiling regular expressions in inner loops or helper functions (such as `re.compile(...)` inside a function called per line) introduces measurable overhead (~55% slower string processing).
**Action:** Always extract static regex patterns to module-level constants (`_TAG_PATTERNS`) when processing text files or document streams line-by-line.
