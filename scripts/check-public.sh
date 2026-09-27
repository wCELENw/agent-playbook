#!/usr/bin/env bash
# Fails if tracked files or unpushed commits contain any private term.
# Terms live outside the repo, one per line: ~/.agents/public-scrub.txt
# Install as a hook: cp scripts/check-public.sh .git/hooks/pre-push
set -u
LIST="${PUBLIC_SCRUB_LIST:-$HOME/.agents/public-scrub.txt}"
[ -s "$LIST" ] || { echo "check-public: no deny-list at $LIST" >&2; exit 1; }
PATTERNS=$(grep -v '^[[:space:]]*#' "$LIST" | sed '/^[[:space:]]*$/d' | tr -d '\r')
[ -n "$PATTERNS" ] || { echo "check-public: deny-list is empty" >&2; exit 1; }
cd "$(git rev-parse --show-toplevel)" || exit 1
fail=0
ARGS=(); while IFS= read -r p; do ARGS+=(-e "$p"); done <<< "$PATTERNS"
git grep -n -i -F "${ARGS[@]}" -- . ; rc=$?
[ $rc -eq 0 ] && fail=1
[ $rc -gt 1 ] && { echo "check-public: git grep error $rc" >&2; exit 2; }
RANGE='@{u}..HEAD'; git rev-parse -q --verify '@{u}' >/dev/null || RANGE=HEAD
while IFS= read -r p; do
  if git log -i -F -S"$p" --format='  commit %h %s' "$RANGE" | grep -q .; then
    echo "check-public: unpushed history contains a private term (line of $LIST)" >&2; fail=1
  fi
  if git log --format='%an %ae %cn %ce' "$RANGE" | grep -q -i -F -- "$p"; then
    echo "check-public: commit author/committer contains a private term" >&2; fail=1
  fi
done <<< "$PATTERNS"
[ $fail -eq 0 ] && echo "check-public: clean" || echo "check-public: FAILED, replace with placeholders before push" >&2
exit $fail
