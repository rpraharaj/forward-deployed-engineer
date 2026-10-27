# Coding-agent integrations

The seven `fde-*/skills/` directories contain the canonical instructions and resources.
Integrations install or expose those same files; they do not maintain different
procedures for each agent. The format follows the [Agent Skills specification](https://agentskills.io/specification).

## Local skill installation

Requires Python 3.10+; the installer uses only the standard library. Choose a
working project and a skill directory that its agent actually discovers:

```bash
python3 /path/to/forward-deployed-engineer/scripts/install-skills.py \
  --dest /path/to/your-project/.agents/skills --packs fde-core fde-ai
```

Omit `--packs` for core alone. Valid packs are `fde-core`, `fde-data`,
`fde-migration`, `fde-platform`, `fde-operate`, `fde-product`, and `fde-ai`.
For the general lifecycle, install core plus the optional packs needed for the work.
Specialized skills can also be installed separately when their prerequisites and
engagement artifacts already exist.

The destination contains one folder per skill and an `_shared/` resource folder.
Full references, scripts, and assets are copied. `_shared` has no `SKILL.md` and
is not itself an invocable skill. The installer makes no network requests, does
not run skill code, and does not change agent settings or `AGENTS.md`/`CLAUDE.md`.
Review whether installed skill copies should be committed or ignored by the team.

## Codex

Codex [discovers project skills under `.agents/skills/`](https://learn.chatgpt.com/docs/build-skills).
Install there, launch Codex in the working project, then explicitly invoke a skill:

```text
$repo-recon Map this repository before we plan a change. Use the existing engagement workspace.
```

Names and descriptions also support automatic matching. Discovery is affected by
host settings and metadata budgets. If an installation is not visible, restart the
session and inspect the host's skill list. Avoid installing the same skill twice
at project and user scope; Codex does not merge duplicate names.

The [validation record](../VALIDATION.md) distinguishes native CLI trials from
structural installation checks. Installed-format compatibility is not a claim
that every procedure has been exercised in Codex.

## Claude Code optional plugin integration

The existing marketplace and pack manifests remain available. From the directory
containing your clone:

```bash
claude plugin marketplace add ./forward-deployed-engineer
claude plugin install fde-core@fde-skills
claude plugin install fde-ai@fde-skills
```

Select other optional packs using the same `name@fde-skills` form. For a local
development session without installing:

```bash
claude --plugin-dir ./forward-deployed-engineer/fde-core \
  --plugin-dir ./forward-deployed-engineer/fde-ai
```

Refresh the local catalog after pulling changes with
`claude plugin marketplace update fde-skills`. See the
[Claude plugin CLI reference](https://code.claude.com/docs/en/plugins/cli-reference).
Do not also copy the same skills into another directory that Claude discovers.
Plugin validation verifies packaging; it is not a new behavioral score.

## Compatibility evidence

| Host / route | Recorded evidence | Limits |
|---|---|---|
| Codex CLI 0.144.1, local `.agents/skills/` | Two native trials: `context-strategy` + `repo-recon` preserved an existing `AGENTS.md`; `env-bootstrap` + `handover-pack` created a portable guide when no instruction file existed | Four procedures, explicit invocation, small synthetic repositories; not a trial of all skills or implicit selection |
| Claude Code plugin | Root marketplace and all seven pack manifests pass strict validation | Historical behavioral results remain historical; no new Claude procedure run for this change |
| Cursor and other hosts | Standard skill format and documented installation locations | Runtime behavior untested here |

See [run 17](../VALIDATION.md#run-17--agent-neutral-procedures-and-native-codex-trials)
and [native results](../eval/codex-smoke-results.json) for inputs, artifacts,
checks, command traces, and limitations.

## Other agents and manual use

[Cursor documents Agent Skills and `.agents/skills/` discovery](https://cursor.com/docs/skills).
The local installer can prepare that directory, but Cursor runtime behavior has
not been tested here. Verify discovery, reference resolution, and actual outputs
in the target host before describing the integration as tested.

For another host, check its documented skill locations. If native discovery is
unavailable, explicitly read the desired skill and its references from the full
checkout. Required capabilities are determined by the task: local file access,
Git/shell for repository investigation, and any separately authorized system
access. Skills cannot provide tools or approvals the host does not have.

## Working guides and automatic context

Preserve applicable team instructions and the designated working guide. Use
`<workspace>/repo-guide.md` when no suitable guide exists, as described in
[`agent-context.md`](../fde-core/skills/_shared/agent-context.md). Read it explicitly
when switching agents. `AGENTS.md` and `CLAUDE.md` are host-specific examples, not
universal filenames. Do not duplicate policy or assume an arbitrary guide loads
automatically.

## Updating an installation

Copied installations are snapshots, independent of later changes to the clone.
Rerunning the installer is safe for identical files and can add new packs.
If an existing destination differs, the installer stops before copying any new
folders, including when an entry is a symlink. It never overwrites a team skill.

To refresh changed files, review and back up the affected FDE skill folders and
`_shared/`, remove only the copies you intend to replace, then rerun the installer.
Keep local edits in your backup and review the new copies before restoring them.
If ownership is unclear, choose a clean destination instead. Do not delete the
whole `.agents/skills/` directory: it may contain unrelated team skills.
