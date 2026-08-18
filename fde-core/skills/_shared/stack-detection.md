# Stack detection

How to identify what you're working with, before assuming anything. Used by `env-bootstrap`, `repo-recon`, `safe-change`, `verification-plan`, and `deploy-runbook`.

## Principle

Detect from artifacts in the repository, in this order: **build manifest → lockfile → CI config → container/orchestration → IaC**. Each layer tells you something the others don't, and they disagree surprisingly often. When they disagree, **CI config is the most reliable statement of how the software is actually built**, because it's the one that has to work every day. A README is the least reliable — it records what was true when someone last cared.

## One-shot survey

Run this first. It costs nothing and usually settles the question.

```bash
ls -a && find . -maxdepth 2 \( -name "pom.xml" -o -name "build.gradle*" -o -name "package.json" \
  -o -name "*.csproj" -o -name "*.sln" -o -name "go.mod" -o -name "Cargo.toml" \
  -o -name "pyproject.toml" -o -name "requirements*.txt" -o -name "Gemfile" \
  -o -name "composer.json" -o -name "mix.exs" -o -name "build.sbt" -o -name "pubspec.yaml" \
  -o -name "Makefile" -o -name "CMakeLists.txt" -o -name "BUILD.bazel" -o -name "WORKSPACE" \
  -o -name "Dockerfile" -o -name "docker-compose*.y*ml" -o -name "*.gemspec" \) \
  -not -path "*/node_modules/*" -not -path "*/vendor/*" 2>/dev/null
```

Then check the language mix, which catches things the manifests miss. **Fold case** — z/OS and some Windows trees ship `.cbl` and `.CBL` as two extensions:

```bash
git ls-files | sed 's/.*\.//' | tr '[:upper:]' '[:lower:]' | sort | uniq -c | sort -rn | head -25
```

Use `git ls-files` rather than `find` — it respects `.gitignore` for free, so build output and vendored dependencies don't drown the signal.

**The language mix outranks the manifest.** A repository whose root manifest says one thing while 90% of its files are another language has usually been migrated, and the manifest is a leftover. Trust the file count and go looking for why they disagree — that discrepancy is often the single most important thing to know about the codebase.

**An empty one-shot survey is not a failed detection.** Mainframe inventories, low-code exports, and some generated-spec trees have no `pom.xml` / `mix.exs` / `package.json`. The language mix *is* the stack. Record "no package manager, no CI" as a finding, then treat the dominant extensions as the declaration surface — see `repo-recon/references/entry-points-by-stack.md` ("When there is no language section" and "are the entry points even in the code?").

### Count sub-manifests before concluding

The depth-2 survey deliberately finds only top-level manifests, which **undercounts a workspace or monorepo by orders of magnitude**. Always follow up:

```bash
# Same names as the one-shot survey. Omitting a detected stack here
# makes a polyglot repo look like only the stacks in this list.
for m in Cargo.toml pom.xml package.json go.mod pyproject.toml build.gradle \
         build.gradle.kts mix.exs Gemfile composer.json pubspec.yaml \
         CMakeLists.txt Makefile; do
  n=$(find . -name "$m" -not -path "./.git/*" -not -path "*/node_modules/*" -not -path "./target/*" 2>/dev/null | wc -l)
  [ "$n" -gt 0 ] && echo "$m: $n"
done
# .csproj / .sln are globs
n=$(find . -name "*.csproj" -o -name "*.sln" | grep -vc node_modules)
[ "$n" -gt 0 ] && echo "*.csproj/*.sln: $n"
```

One root manifest and 124 below it is a workspace, not a project. That single fact changes how you build it, how you scope a change, and what "the repo" even means in every artifact you write.

## Build manifests

| File | Stack | Build | Test |
|---|---|---|---|
| `pom.xml` | JVM / Maven | `mvn -q package -DskipTests` | `mvn test` |
| `build.gradle`, `build.gradle.kts` | JVM / Gradle | `./gradlew build -x test` | `./gradlew test` |
| `build.sbt` | Scala | `sbt compile` | `sbt test` |
| `package.json` | Node / TS | check `scripts` — never assume | check `scripts.test` |
| `*.csproj`, `*.sln`, `Directory.Build.props` | .NET | `dotnet build` | `dotnet test` |
| `pyproject.toml` | Python (Poetry/PDM/uv/Hatch) | per `[build-system]` | usually `pytest` |
| `requirements*.txt`, `setup.py` | Python (legacy) | `pip install -r …` | `pytest` or `python -m unittest` |
| `go.mod` | Go | `go build ./...` | `go test ./...` |
| `Cargo.toml` | Rust | `cargo build` | `cargo test` |
| `Gemfile`, `*.gemspec` | Ruby | `bundle install` | `bundle exec rspec` / `rake test` |
| `composer.json` | PHP | `composer install` | `vendor/bin/phpunit` |
| `mix.exs` | Elixir | `mix compile` | `mix test` |
| `pubspec.yaml` | Dart / Flutter | `flutter build` | `flutter test` |
| `CMakeLists.txt` | C / C++ | `cmake -B build && cmake --build build` | `ctest` |
| `Makefile` | anything | **read it** — often the real entry point | `make test` |

**Always prefer the repo's own wrapper** over a globally installed tool: `./gradlew` over `gradle`, `./mvnw` over `mvn`, the version in `.nvmrc` / `.tool-versions` / `.python-version` over whatever is on `PATH`. On a locked-down enterprise machine the global tool is frequently the wrong major version, and this is the single most common cause of a build that fails only for you.

**`Makefile` deserves special attention.** In large organizations it is often a thin wrapper hiding the actual, heavily-parameterized build command — the one nobody remembers. Read it before running anything else.

## Monorepo and orchestration signals

These change *how you build*, not what the language is. Miss them and you'll try to build a single module in a repo where that isn't a supported operation.

| Signal | Meaning |
|---|---|
| `nx.json`, `turbo.json`, `lerna.json`, `pnpm-workspace.yaml` | JS monorepo — build through the orchestrator, not per-package |
| `workspaces` key in `package.json` | npm/yarn workspaces |
| `BUILD.bazel`, `WORKSPACE`, `MODULE.bazel` | Bazel — hermetic; ignore per-language build files |
| `settings.gradle` listing many `include` | Gradle multi-project |
| `pom.xml` with `<modules>` | Maven reactor — build from root |
| `Cargo.toml` with `[workspace]` | Cargo workspace |
| `go.work` | Go workspace |
| `.sln` referencing many `.csproj` | .NET solution |

## Lockfiles

Presence tells you the package manager exactly; absence is itself a finding worth recording.

`package-lock.json` → npm · `yarn.lock` → Yarn · `pnpm-lock.yaml` → pnpm · `bun.lockb` → Bun · `poetry.lock` → Poetry · `uv.lock` → uv · `Pipfile.lock` → Pipenv · `Gemfile.lock` → Bundler · `composer.lock` → Composer · `go.sum` → Go modules · `Cargo.lock` → Cargo · `packages.lock.json` → NuGet · `mix.lock` → Hex/Mix

Using the wrong package manager on a locked repo rewrites the lockfile and produces an enormous, unreviewable diff — a memorable way to introduce yourself to a new team.

## CI configuration — the ground truth

This is the highest-value file in the repository for an arriving engineer. It contains the exact build, test, and deploy commands that actually work, in order, with the environment they need.

`.github/workflows/*.yml` · `Jenkinsfile` · `.gitlab-ci.yml` · `azure-pipelines.yml` · `.circleci/config.yml` · `bitbucket-pipelines.yml` · `.teamcity/` · `tekton/` · `.drone.yml` · `cloudbuild.yaml` · `buildspec.yml`

### Find the build workflow among the automation

Mature repositories accumulate twenty or more workflows, most of which are bots — changelog checks, issue labelling, backports, release cutting, stale-bot. Reading them in order wastes the step. Triage by what they trigger on and what they run:

```bash
# Workflows that gate a pull request are the ones that matter
grep -l "pull_request" .github/workflows/*.y*ml 2>/dev/null

# Rank by whether they actually build or test anything
for f in .github/workflows/*.y*ml; do
  n=$(grep -cE "cargo |mvn |gradle|npm |pnpm |yarn |dotnet |pytest|tox |python |go test|mix |elixir|make " "$f" 2>/dev/null)
  [ "$n" -gt 0 ] && echo "$n $f"
done | sort -rn | head -5
```

The top result is nearly always the real build. Read that one properly and skim the rest.

Read it for:

- The real build and test invocation, including flags and profiles
- Required environment variables and secret names *(names are the finding; never copy values)*
- Service containers the tests depend on — databases, brokers, mocks
- Language and tool versions, which are usually pinned here and nowhere else
- The deploy path and its gates — the starting point for `deploy-runbook`
- Which branches trigger what, which tells you the branching model without asking

## Runtime, packaging, and infrastructure

| Signal | Tells you |
|---|---|
| `Dockerfile` | Runtime base image, exact build steps, entrypoint, exposed ports |
| `docker-compose*.yml` | The service's local dependency graph — the fastest map of what it talks to |
| `k8s/`, `*.yaml` with `kind:` | Kubernetes deployment; check resource limits, probes, config sources |
| `Chart.yaml`, `values*.yaml` | Helm — `values-<env>.yaml` files enumerate the environments |
| `*.tf`, `.terraform/` | Terraform; `*.tfvars` filenames enumerate environments |
| `template.yaml`, `serverless.yml`, `sam.yaml` | Serverless — event-driven entry points, not HTTP routes |
| `Procfile` | Heroku-style process model |
| `*.bicep`, `azuredeploy.json` | Azure ARM/Bicep |
| `ansible/`, `playbook*.yml` | Configuration management; often the only record of VM-era deployment |

`docker-compose.yml` is worth calling out: in one file it usually names every database, cache, broker, and stubbed downstream the service needs. For `repo-recon` it is often the single most informative artifact in the repository.

## Version pinning

Version mismatch is the most common bootstrap failure. Search **three layers**. An empty result in one layer is not evidence the version is unpinned — that is the same silent-zero as grepping the wrong extension.

### 1. Dedicated pin files

`.nvmrc` · `.node-version` · `.python-version` · `.ruby-version` · `.tool-versions` (asdf/mise) · `.sdkmanrc` · `rust-toolchain.toml` / `rust-toolchain` · `global.json` (.NET) · `.java-version`

```bash
git ls-files | grep -iE "^\.(nvmrc|node-version|python-version|ruby-version|tool-versions|sdkmanrc|java-version)$|toolchain|global\.json"
```

### 2. Version fields in the manifests you already found

After detection, read the field **this stack** uses — including the workspace/root hoist. A per-package search returns nothing while the language version is defined once:

| Stack signal | Language / compiler field | Common hoist |
|---|---|---|
| `Cargo.toml` | `rust-version`, `edition` | `[workspace.package]` |
| `package.json` | `engines` | workspace root `package.json` |
| `pom.xml` | `<maven.compiler.release>` / `<java.version>` | parent POM |
| `*.csproj` | `TargetFramework` | `Directory.Build.props` |
| `pyproject.toml` | `requires-python` | — |
| `go.mod` | `go` directive | `go.work` |
| `mix.exs` | Elixir / OTP | `.tool-versions`, CI |
| `build.gradle*` | toolchain / `sourceCompatibility` | `gradle/libs.versions.toml` |

`[workspace.dependencies]`, `Directory.Packages.props`, and parent-POM `<dependencyManagement>` pin *libraries*. `[workspace.package]` and `Directory.Build.props` pin *the language*. Look at both.

### 3. CI toolchain install

The build workflow from the triage above. The version is often only here: a matrix key (`rust:`, `node-version:`, `go-version:`, `java-version:`) or a setup action (`*-toolchain`, `setup-node`, `setup-java`, `setup-python`, `setup-beam`).

**When layers disagree**, record all three. The CI job that matches this OS is what the PR will run. The manifest field is usually the floor (minimum supported). A dedicated pin file is what local tools auto-select. Do **not** invent a pin file the repo does not ship — install the version the manifest or CI named, and record that as a workaround.

**Check for centralized build configuration before grepping per-project files.** Many ecosystems hoist shared settings out of individual manifests:

`Directory.Build.props` / `Directory.Packages.props` (.NET) · `gradle/libs.versions.toml` (Gradle version catalogs) · `<dependencyManagement>` in a parent `pom.xml` · `[workspace.package]` / `[workspace.dependencies]` in a root `Cargo.toml` · `pnpm-workspace.yaml` catalogs

If a version or dependency you expect to find isn't in the project file, it's almost certainly in one of these.

## Enterprise-specific signals

Easy to miss, and each one implies a constraint you will otherwise discover the hard way:

| Signal | Implication |
|---|---|
| `settings.xml`, `.npmrc`, `pip.conf`, `nuget.config`, `.yarnrc.yml` with internal URLs | Internal artifact registry — the public one may be firewalled. See `enterprise-constraints.md` |
| `.mvn/wrapper/`, `gradle/wrapper/` | Wrapper pins the build-tool version; use it |
| `CODEOWNERS` | Ownership signal — feeds `ownership-map` |
| `.editorconfig`, linter and formatter configs | The house style you must match in `safe-change` |
| `sonar-project.properties` | Quality gate that will block your PR; find its thresholds early |
| `renovate.json`, `.dependabot/` | Automated dependency updates — expect churn, and expect conflicts |
| `.gitattributes` with LFS filters | Large files; a plain clone may be incomplete |
| `.pre-commit-config.yaml`, `.husky/` | Hooks that will run on your commit whether you expect them or not |
| `*.feature`, `cucumber/`, `specflow/` | BDD suites — often the closest thing to a written requirements spec |

That last row is a genuine shortcut. In organizations with no maintained documentation, a Cucumber suite is frequently the only place the intended business behavior is written down in a language stakeholders once agreed to.

## When detection is ambiguous

Large enterprise repositories are often several stacks at once — a Java service, a React admin console, some Python batch jobs, and Terraform, in one tree.

Do not pick one and proceed. Record all of them with their roots, then scope to the one your task touches:

```markdown
## Stacks detected
- `services/billing/` — Java 17 / Maven / Spring Boot `[confirmed: pom.xml:14]`
- `web/admin/` — React 18 / pnpm `[confirmed: web/admin/package.json]`
- `jobs/` — Python 3.11 / Poetry `[confirmed: jobs/pyproject.toml]`
- `infra/` — Terraform 1.6 `[confirmed: infra/versions.tf]`

**Task scope:** `services/billing/` only.
```

Stating the scope is what stops a later reader assuming the map covers the whole tree — and stops you quietly wandering into a component nobody asked you to touch.

## Searching after detection

Skills that grep the tree (`repo-recon`, `feasibility-probe`, `blast-radius`, `context-strategy`) **bind file extensions from this detection**, never from an example in a SKILL.md. A search locked to `*.java` on a C# or Rust repository returns near-zero hits and that silence reads as "doesn't exist."

1. Take the top extensions from `git ls-files` (step above), **case-folded**, minus lockfiles, generated code, and vendored trees.
2. Restrict greps to those extensions. Include SQL, DDL, and the declaration artifacts you counted (copybooks, maps, JCL, CSD, scheduler exports) when the question is data or wiring.
3. Match both cases of each extension (`*.cbl` and `*.CBL`). A case-sensitive `--include` on a z/OS tree returns a confident zero.
4. If a capability the system obviously must have returns near-zero hits, the search is wrong — switch extension, then look for a house abstraction or a declaration artifact (see `repo-recon/references/entry-points-by-stack.md`).

```bash
# After detection — EXT is what you found, not a guess
# Example only: rs, cs, ts, py, go, java, cbl, jcl
grep -rl "<domain-term>" --include="*.$EXT" --include="*.$(echo "$EXT" | tr '[:lower:]' '[:upper:]')" --include="*.sql" --include="*.ddl" . | wc -l
```

Dependency trees follow the same rule: use the tool this file's manifest table named for the detected stack (`cargo tree`, `dotnet list package --include-transitive`, `npm ls --all`, and so on). Do not paste every ecosystem's command into a SKILL.md body.
