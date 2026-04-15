---
name: patch-review
description: Create a temporary patch of all changes on the current branch (committed and uncommitted) compared against main and perform a comprehensive industry-standard code review.
---

# Patch Review

This skill automates the process of generating a diff against the `main` branch and performing a deep code review based on industry-standard engineering practices.

## Workflow

1.  **Generate Diff**: Use `scripts/create_review_diff.sh` to generate a comprehensive patch of the current branch compared to the merge-base of `main`.
2.  **Analyze Standards**: Reference `references/review_criteria.md` to understand the dimensions of a high-quality review (Security, Logic, Design, Testing, etc.).
3.  **Perform Review**: Analyze the generated diff and provide a point-wise review, highlighting strengths and identifying areas for improvement.

## Usage Examples

- "Review my changes against main."
- "Generate a patch for this branch and perform a code review."
- "Compare my current work with main and tell me what can be improved."

## Review Dimensions

The review should always cover:
- **Logic & Correctness**: Bug identification and edge case handling.
- **Design**: SOLID principles and DRY.
- **Security**: Secret detection and input validation.
- **Testing**: Presence and quality of new tests.
- **Style**: Naming conventions and readability.

## Resources

### scripts/create_review_diff.sh
A bash script that finds the merge base with `main` and outputs a full diff including staged and unstaged changes.

### references/review_criteria.md
A comprehensive guide to industry-standard code review criteria used to evaluate the quality of the changes.
