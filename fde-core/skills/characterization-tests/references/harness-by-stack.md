# Test harness by stack

Load the section matching the stack detected in step 2 of `repo-recon`. **Use what the repository already uses** — introducing a new test framework as a side effect of characterizing legacy code is its own, larger change, and it will be the thing the review argues about.

## First: find the existing convention

Before choosing anything, establish what's already there.

```bash
# What test framework does the build actually pull in?
grep -rniE "junit|testng|xunit|nunit|pytest|unittest|jest|vitest|mocha|rspec|minitest|testify|criterion" \
  pom.xml build.gradle* package.json *.csproj pyproject.toml requirements*.txt Gemfile go.mod Cargo.toml mix.exs 2>/dev/null | head

# Copy the shape of a neighbouring test
find . -path "*test*" -name "*.*" -newer README.md 2>/dev/null | head -5
```

Read one recent test file before writing yours. Match its naming, fixture setup, assertion style, and mocking approach. See `safe-change` step 2 — idiom matching applies to tests just as much as production code.

---

## Approval / snapshot testing

The core technique for characterization: write the output to a file, review it once, commit it as the baseline. Subsequent runs diff against it.

| Stack | Library | Notes |
|---|---|---|
| JVM | ApprovalTests, JsonUnit, or hand-rolled file compare | Hand-rolled is fine and often clearer |
| .NET | Verify, ApprovalTests.Net | Verify is the current default |
| Node / TS | Jest/Vitest built-in snapshots | `toMatchSnapshot()`; beware auto-update on CI |
| Python | pytest + syrupy, or `--snapshot-update` patterns | |
| Go | golden files — `-update` flag convention | Idiomatic and widely used; no library needed |
| Rust | `insta` | Excellent; `cargo insta review` |
| Ruby | `approvals` gem, or RSpec + fixture compare | |
| Elixir | Hand-rolled compare of captured output; no stock snapshot lib | Tests live in `*_test.exs`; ExUnit. No approval framework unless the repo already has one. |

**Watch the auto-update trap.** Snapshot frameworks can regenerate baselines on failure. If that runs in CI, a behavior change silently rewrites the baseline and the test never fails. Confirm update mode is off in CI before relying on any of these.

Hand-rolling is entirely reasonable: serialize the output, compare to a committed file, print a diff on mismatch. Fewer moving parts and no dependency to justify.

---

## Substituting dependencies at the seam

| Stack | Common approach |
|---|---|
| JVM | Mockito, or hand-written fakes; constructor injection is the cleanest seam |
| .NET | Moq / NSubstitute; interface + DI |
| Node / TS | `jest.mock`, dependency injection, or `nock` for HTTP |
| Python | `unittest.mock.patch`, `monkeypatch`, `responses` for HTTP |
| Go | Interfaces + hand-written fakes; `httptest` for HTTP |
| Rust | Trait objects + hand-written fakes; `mockall` if already present |
| Ruby | RSpec doubles; `webmock` for HTTP |
| Elixir | Pass fakes into the function; `Mox` only if the repo already uses it |

**Prefer hand-written fakes over mocks for characterization.** A mock asserts *interactions*, which couples the test to the current implementation — exactly what you're about to refactor. A fake supplies *behavior* and lets the implementation change freely underneath. Characterization tests that break during a pure refactor have failed at their one job.

---

## Testing at a coarse boundary

When there's no usable seam in the code, characterize from outside it. This requires no source change and no understanding of internals, which is often the fastest route into hostile legacy code.

**HTTP boundary** — record request/response pairs and replay them:

| Stack | Tooling |
|---|---|
| JVM | WireMock, MockWebServer, Spring `MockMvc`, RestAssured |
| .NET | `WebApplicationFactory`, WireMock.Net |
| Node | `supertest`, `nock` |
| Python | `pytest` + `TestClient` / `requests-mock` |
| Go | `httptest.Server` |
| Rust | `axum-test`, `wiremock` |

**Process / CLI boundary** — invoke the binary, capture stdout/stderr and exit code, snapshot all three. Crude, effective, and completely stack-independent.

**Database state** — set up known rows, run the operation, snapshot the resulting state. Containerized databases (Testcontainers and equivalents) make this practical where the team already uses them. Where they don't, a transaction rolled back after each test is usually enough.

---

## Verifying the test can fail

Every stack, same discipline — mutate the code, confirm red, revert. See step 5 of the skill.

Where a mutation-testing tool already exists in the repo (PIT, Stryker, mutmut, `cargo-mutants`, `go-mutesting`), it automates this. Do **not** introduce one just for this purpose; a manual mutation of the specific line you care about takes thirty seconds and proves the same thing.

---

## Coverage confirmation

To confirm your tests actually reach the change site:

| Stack | Tool |
|---|---|
| JVM | JaCoCo |
| .NET | coverlet |
| Node / TS | `c8`, `nyc`, or built into Jest/Vitest |
| Python | `coverage.py` / `pytest-cov` |
| Go | `go test -cover -coverprofile` |
| Rust | `cargo-llvm-cov`, `tarpaulin` |
| Ruby | SimpleCov |
| Elixir | `mix test --cover` / ExCoveralls if present |

Where no tool is available or installing one is blocked, a temporary `throw`/`panic` at the change site proves reachability just as well: run the tests, confirm they fail, remove it.
