# Durable context across coding agents

The working guide carries build/test commands, layout, conventions, and landmines
between sessions. Its content is portable; automatic loading depends on the host.

1. Read the active agent's applicable project instructions first. Reuse the team's
   designated working guide, such as `AGENTS.md`, `CLAUDE.md`, or another documented
   file. Respect its directory scope, policy, and existing structure.
2. If no suitable guide exists, write `<workspace>/repo-guide.md` with the standard
   artifact header. Record the chosen guide's path in the charter or context notes.
   Do not create a vendor-specific instruction file just because an agent changed.
3. Preserve existing instructions and unrelated sections. Add confirmed commands,
   evidence references, conventions, and known limits; never credentials or raw
   customer data. Updating technical facts does not authorize changing team policy.
4. On each new session or agent switch, explicitly read the recorded guide and the
   relevant engagement artifacts. Do not assume a host automatically loads an
   arbitrary Markdown file. Tool-specific setup may add a short pointer to the guide
   in a host-supported instruction file when appropriate and authorized.

Keep the guide short (roughly under 200 lines). Detailed engagement narrative,
decisions, and readouts belong in the resolved workspace and are linked from it.
Subagents, MCP integrations, and built-in review commands are optional capabilities;
use available tools within the user's authorization, with scripts or a bounded
sequential investigation when delegation is unavailable.
