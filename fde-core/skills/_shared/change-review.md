# Reviewing the actual change

Used by `safe-change` and `security-compliance-check`. A branch diff alone misses
work that has not been committed; a hardcoded `main` may be the wrong target.

1. Establish the intended PR target from the ticket, existing PR, repository
   conventions, or remote default branch. If ambiguous, resolve the target before
   claiming review coverage. Compute its merge-base with `HEAD` and record that SHA
   as `review_base`; do not assume the target is named `main`.
2. Inventory each layer separately. These commands return paths, not file content:

   ```bash
   git diff --name-only "$review_base" HEAD
   git diff --cached --name-only
   git diff --name-only
   git ls-files --others --exclude-standard
   ```

3. Review the branch commits, index, working tree, and relevant untracked files.
   Include deleted files and record intentionally excluded paths. Ignored secret
   files stay private and must not be added merely to include them in a review.
4. Before displaying hunks, use the organization's approved local scanner with
   redacted output, or inspect locally without echoing sensitive content. Report
   paths, line numbers, finding types, and redacted summaries. Never print secret
   values, customer payloads, or raw historical patches into the conversation.
5. Record the base SHA, current revision, and whether uncommitted files were
   included. A clean branch diff with a dirty working tree is not a completed
   review. Recheck the inventory if files change after the review.
