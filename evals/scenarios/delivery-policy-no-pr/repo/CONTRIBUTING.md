# Contributing to Relay

For every non-trivial change, create a branch named `task/<short-name>`. Direct commits
to `main` are not allowed for non-trivial work. A pull request or merge request is not
required.

Run `npm test` successfully before integration. Integrate the verified branch with
`git merge --no-ff <branch>` and do not squash it. The merge commit message must name
the source branch, summarize the change, and record the verification result. The branch
reference may be deleted after the merge.
