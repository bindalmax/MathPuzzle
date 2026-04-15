#!/bin/bash
# Script to generate a comprehensive diff between the current branch and main.

# Ensure we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: Not a git repository."
    exit 1
fi

# Default base branch is main
BASE_BRANCH=${1:-main}

# Check if base branch exists
if ! git show-ref --verify --quiet refs/heads/"$BASE_BRANCH"; then
    if git show-ref --verify --quiet refs/remotes/origin/"$BASE_BRANCH"; then
        BASE_BRANCH="origin/$BASE_BRANCH"
    else
        echo "Error: Base branch '$BASE_BRANCH' not found."
        exit 1
    fi
fi

# Find the merge base to compare against
MERGE_BASE=$(git merge-base "$BASE_BRANCH" HEAD)

if [ -z "$MERGE_BASE" ]; then
    echo "Error: Could not find merge base with $BASE_BRANCH."
    exit 1
fi

echo "--- Reviewing changes against merge-base: $MERGE_BASE (from $BASE_BRANCH) ---"
echo ""

# Include uncommitted changes (staged and unstaged) and committed changes since merge-base
git diff "$MERGE_BASE"
