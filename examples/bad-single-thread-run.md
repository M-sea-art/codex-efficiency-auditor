# Bad Single-Thread Codex Run Example

This example illustrates a Codex run that scores poorly on capability utilization and auditability.

Codex Capability Utilization: 54/100

Verdict: mostly single-thread execution with weak auditability

Capability gaps:
- No explicit goal contract at the start.
- No task decomposition; everything happened in one thread.
- Did not use worktree isolation.
- No reviewer agent; no subagents.
- No Git evidence or commit history; changes were applied directly without a PR.
- Tests were mentioned but no evidence was provided.
- The final handoff lacked enough details for another agent to continue.

Upgrade prompts:
Before continuing, create a bounded `/goal` contract, split the task into Task Cards, assign a read-only verifier, and require validation evidence before final handoff.
