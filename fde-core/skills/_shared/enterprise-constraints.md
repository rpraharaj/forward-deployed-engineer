# Enterprise constraints

Working inside a large organization's controls. These are the environmental facts that make an enterprise engagement different from open-source work, and each one has a standard workaround worth knowing before it costs you a day.

## Network

**Proxies.** Corporate egress usually goes through an authenticating proxy with TLS interception. Symptoms are certificate errors, hangs on package downloads, and tools that work in the browser but not the terminal.

Check what's already configured before assuming there's no route out:

```bash
python3 - <<'PY'
import os
for name in sorted(os.environ):
    if "proxy" in name.lower():
        print(f"{name}=<set>")
PY
```

Proxy URLs can contain credentials. Inspect tool-specific configuration locally in an approved viewer; report only the file and setting names that are present. Do not print raw environment values or registry/proxy configuration into tool output, chat, or artifacts.

Each toolchain needs its proxy configured separately — `git`, `npm`, `pip`, Maven, Gradle, Docker, and the JVM all read different settings. Configuring one and assuming the rest follow is the usual mistake.

**TLS interception** means the proxy presents its own certificate. Tools need the corporate root CA in *their* trust store, which is not the OS trust store for the JVM (`cacerts`), Node (`NODE_EXTRA_CA_CERTS`), Python (`REQUESTS_CA_BUNDLE`, `SSL_CERT_FILE`), or Git (`http.sslCAInfo`). Never resolve this by disabling verification — `strict-ssl=false`, `GIT_SSL_NO_VERIFY`, `-k` — even temporarily. It is the kind of thing that gets committed, and it is a finding in any subsequent audit.

**Internal registries.** Public registries are frequently blocked outright; the organization mirrors through Artifactory, Nexus, or an equivalent. The URLs are in `.npmrc`, `settings.xml`, `pip.conf`, `nuget.config`. Two consequences worth anticipating: a package that exists publicly may simply not be mirrored, and requesting that it be added is a process with a lead time — one that belongs in `00b-access.md` as soon as you know you need it.

## Machine

Assume no administrator rights. Practical consequences:

- Install to user scope where a tool supports it — `pipx`, `npm --prefix ~/.local`, `~/.local/bin` on `PATH`
- Prefer the repository's own wrapper (`./gradlew`, `./mvnw`) over anything global
- Version managers that don't need root — `asdf`, `mise`, `nvm`, `pyenv` — are usually permitted where package managers aren't
- Docker may be unavailable, restricted to a remote daemon, or gated behind a licence. Check before designing a workflow around it.

Some organizations issue a VDI or jump host for development, with the source only ever residing there. If so, that machine is your environment, and its performance and clipboard restrictions shape everything — including which coding-agent capabilities are available on it. Establish this on day one, not week two.

## Offline

Assume you cannot search the web. Every skill in this portfolio is written to reach its conclusion from repository-local evidence, but it changes your habits:

- The dependency's source in the local package cache (`~/.m2`, `~/.gradle`, `node_modules`, site-packages) is your documentation. Read it.
- `git log` and PR history are your Stack Overflow — someone already hit this
- The test suite is the specification, more reliably than any wiki
- Where an internal Confluence or Backstage exists, it is reachable even when the internet isn't; ask for the link early

## Data handling

The controlling question is: **what leaves the machine, and where does it go?** The organization has a policy on this. Find it before you need it, and if the answer is unclear, ask the security or engineering lead named in `02b-ownership.md` rather than deciding for yourself.

Regardless of the answer, these hold:

- Never put credentials, tokens, or connection strings into artifacts, commits, or chat. Reference where they live — "the value is in Vault at `secret/billing/db`" — never the value.
- Never copy production data into a local or test environment. That's what `test-data-strategy` exists for.
- When an artifact needs an example payload, invent the values and say so: *"illustrative values, not real data."*
- Redact before you paste. Real customer identifiers in an error message are still customer data.

## Change control

Large organizations gate production changes: CAB approval, release calendars, freeze periods around quarter-end and peak trading, mandatory lead times, segregation of duties meaning the person who wrote the change may not deploy it.

Find out what applies **before** you plan the work, not when you try to ship. A change that is technically complete and misses the release window by two days is late by a month. `change-control-navigation` covers this properly; the minimum on day one is knowing whether a freeze is coming and what the lead time on an approval is.

## Working while blocked

You will be blocked, repeatedly, on access and on other people. The FDE's distinguishing habit is having a queue of useful work that doesn't depend on the blocker.

Almost always available before any access is granted:

- Reading whatever source you *can* reach — usually more than you think
- `repo-recon` on any repository you have read access to
- `requirements-to-spec` from documents and conversations
- Drafting the questions for `knowledge-interview` while you wait for the meeting
- Building the access register itself, which is what turns a passive wait into a tracked critical path

Record the blocker in `00b-access.md` with a date and an owner, then move to the next thing. A blocker without a date is invisible; one with a date and an owner is a fact you can escalate with.
