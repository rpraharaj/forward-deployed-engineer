# Entry points by stack

Load the section matching the stack detected in step 2. Do **not** run patterns from a stack you didn't detect — they produce a confident, wrong answer.

## Before you start: what shape is this thing?

Entry points differ more by *deployment shape* than by language. Establish the shape first, or you'll search for HTTP routes in a CLI tool and conclude it has no entry points.

| Shape | Signals | Where entry points live |
|---|---|---|
| **Service (API)** | Web framework dependency, `Dockerfile` with `EXPOSE`, k8s manifests | HTTP routes, RPC handlers |
| **Server-rendered web** | Template files (`.cshtml`, `.erb`, `.jinja`, `.blade.php`, `.hbs`) in bulk | Controllers **and** the view/route mapping |
| **CLI** | Argument-parsing library, `bin/` targets, install docs showing a command | Command definitions, subcommand tree |
| **Library** | Published to a package registry, no `main`, consumers are other code | Public API surface — exported symbols |
| **Batch / job** | Scheduler config, cron, workflow YAML | Job classes, scheduled functions |
| **Event consumer** | Broker client dependency, topic names in config | Subscription handlers |
| **Serverless** | `serverless.yml`, `template.yaml`, per-function handlers | Handler functions named in config |

Most real systems are two or three of these at once. A CLI tool that also exposes a local server, a service that also runs nightly jobs. Enumerate all shapes present before searching.

For a **library**, "entry point" means the public API. Read the module's export surface (`lib.rs`, `__init__.py`, `index.ts`, `package.json` `exports`) rather than hunting for `main`.

---

## When the standard search returns zero

**Read this before concluding a capability is absent.** It is the most common way this reference produces a confidently wrong answer.

Mature enterprise codebases define **their own abstractions** over framework primitives. Searching for the framework's interface then returns zero — which reads as "this system has no scheduled work" when in fact it has thirty-nine scheduled tasks behind a house interface.

Observed in testing: a large .NET application returned **0 hits** for `IHostedService` and `BackgroundService`, the framework-standard patterns. It had **39** implementations of its own `IScheduleTask`.

So: if a search for a capability the system *obviously must have* returns zero, the search is wrong, not the system. A shop with an order pipeline has scheduled work. A payments service has retries. Trust that inference over your grep.

**Finding the house abstraction:**

```bash
# Interfaces or base classes with many implementors are usually the house abstraction
grep -rhoE "(: |implements |extends |impl )I?[A-Z][A-Za-z]*(Task|Job|Handler|Listener|Consumer|Command|Worker|Processor|Service)" \
  --include="*.<ext>" . | sed 's/.*[ :]//' | sort | uniq -c | sort -rn | head -20
```

```bash
# Or work backwards from the scheduler/dispatcher: what does the runner iterate over?
grep -rln "Scheduler\|Dispatcher\|Registry\|TaskRunner\|JobRunner" --include="*.<ext>" . | head
```

Then search for implementors of whatever that reveals. The same applies to house abstractions over HTTP handlers, event consumers, validators, and plugins.

**Plugin and module systems** are a related blind spot. Where a codebase has a plugin architecture, each plugin may contribute its own entry points — routes, tasks, event handlers — that are registered dynamically and invisible to a search of the core. Check for a `plugins/`, `modules/`, or `extensions/` tree and search inside it separately.

---

## Rust

```bash
# Binary entry points — note `async fn main` is common and easy to miss
grep -rn "fn main()" --include="*.rs" . | grep -v "/tests/\|/benches/\|/examples/"

# Declared binaries — more reliable than grepping for main
grep -rn -A2 "^\[\[bin\]\]" --include="Cargo.toml" .

# CLI surface (clap is near-universal)
grep -rln "derive(Parser)\|derive(Subcommand)\|command(" --include="*.rs" .

# HTTP, if it's a service
grep -rn "axum::\|actix_web::\|Router::new\|HttpServer::new\|warp::" --include="*.rs" . | head -20

# Library API surface
find . -name "lib.rs" -not -path "./target/*" | head
```

**Workspace note:** in a `crates/` workspace, each crate may have its own binary. Enumerate per crate rather than assuming one entry point:
```bash
find . -name "Cargo.toml" -not -path "./target/*" -not -path "./.git/*" | wc -l
```

## JVM (Java, Kotlin, Scala)

```bash
grep -rn "public static void main\|fun main(" --include="*.java" --include="*.kt" .
grep -rhoE "@(Get|Post|Put|Delete|Request|Patch)Mapping\([^)]*\)" --include="*.java" --include="*.kt" . | sort -u
grep -rn "@Scheduled\|@KafkaListener\|@RabbitListener\|@JmsListener\|@EventListener" --include="*.java" --include="*.kt" .
grep -rn "@RestController\|@Controller\|@Path(" --include="*.java" --include="*.kt" .
# Batch
grep -rn "implements Tasklet\|extends QuartzJobBean\|@DisallowConcurrentExecution" --include="*.java" .
```

## .NET

```bash
grep -rn "static.*Main(\|WebApplication.CreateBuilder\|Host.CreateDefault" --include="*.cs" .

# Attribute routing
grep -rl "\[HttpGet\|\[HttpPost\|\[HttpPut\|\[HttpDelete\|\[Route(" --include="*.cs" . | wc -l

# Convention-routed controllers — MVC apps often have NO routing attributes at all.
# Compare the two counts: a gap means convention routing, and the attribute search alone undercounts.
grep -rl "class .*Controller *:" --include="*.cs" . | wc -l
grep -rn "MapControllerRoute\|MapDefaultControllerRoute" --include="*.cs" .   # the route table

grep -rn "MapGet(\|MapPost(\|MapControllers()" --include="*.cs" .            # minimal API
grep -rn "IHostedService\|BackgroundService\|\[FunctionName" --include="*.cs" .

# Server-rendered surface
git ls-files | grep -c "\.cshtml$"
find . -name "*.cshtml" -path "*Pages*" | head    # Razor Pages route by file path
```

**Two .NET-specific traps.** Attribute routing and convention routing coexist — in one tested application, 117 files had routing attributes while 138 controller classes existed, so an attribute-only search missed 21 controllers. And `TargetFramework` is frequently centralized in `Directory.Build.props` rather than each `.csproj`, so a per-project grep for the version returns nothing.

## Node / TypeScript

```bash
# Declared entry points are more reliable than grep
grep -nE '"(main|bin|exports)"' package.json

grep -rnE "app\.(get|post|put|delete|patch)\(|router\.(get|post|put|delete)\(" --include="*.ts" --include="*.js" --exclude-dir=node_modules .
grep -rn "@Controller\|@Get(\|@Post(" --include="*.ts" --exclude-dir=node_modules .   # NestJS
find . -path "*/pages/api/*" -o -path "*/app/api/*" -not -path "*/node_modules/*" | head   # Next.js
grep -rn "exports.handler\|export const handler" --include="*.ts" --include="*.js" --exclude-dir=node_modules .
grep -rn "cron\.schedule\|new Worker(\|\.consume(" --include="*.ts" --exclude-dir=node_modules .
```

## Python

```bash
grep -rn "if __name__ == " --include="*.py" .
# Declared console scripts — often the real entry points
grep -nA10 "console_scripts\|\[project.scripts\]" setup.py pyproject.toml setup.cfg 2>/dev/null

grep -rn "@app.route\|@router.get\|@router.post\|APIRouter()\|FastAPI()" --include="*.py" .
find . -name "urls.py" | head          # Django
grep -rn "@shared_task\|@celery.task\|@task(" --include="*.py" .
grep -rn "def lambda_handler\|@functions_framework" --include="*.py" .
# Airflow and similar
find . -path "*dags*" -name "*.py" | head
```

## Go

```bash
grep -rn "func main()" --include="*.go" .
find . -type d -name cmd -not -path "./vendor/*"        # conventional binary location
grep -rnE "http\.HandleFunc|mux\.(Handle|HandleFunc)|\.GET\(|\.POST\(|chi\.NewRouter|gin\.(Default|New)\(" --include="*.go" .
grep -rn "RegisterServer\|grpc.NewServer" --include="*.go" .
```

## Ruby

```bash
find . -name "routes.rb" -o -name "config.ru" | head
grep -rn "class.*< ApplicationController\|get '\|post '" --include="*.rb" . | head -20
grep -rn "perform_later\|include Sidekiq::Worker\|class.*< ActiveJob::Base" --include="*.rb" .
ls bin/ exe/ 2>/dev/null
```

## PHP

```bash
find . -name "web.php" -o -name "api.php" -path "*routes*" | head     # Laravel
grep -rn "Route::get\|Route::post\|@Route(" --include="*.php" . | head -20
grep -rn "extends Command" --include="*.php" . | head
```

---

## Stack-independent entry points

Run these regardless. They catch what language-specific searches miss, and they're where the surprises live.

```bash
# Scheduled work declared outside the code
grep -rn "cron\|schedule\|rate(" --include="*.y*ml" --include="*.tf" --include="*.json" . | grep -vi "schema" | head -20

# Container and process entry
grep -rn "ENTRYPOINT\|^CMD" Dockerfile* 2>/dev/null
cat Procfile 2>/dev/null

# Serverless handlers
grep -rn "handler:" serverless.y*ml template.y*ml 2>/dev/null | head

# Kubernetes jobs and cronjobs
grep -rln "kind: CronJob\|kind: Job" --include="*.y*ml" . | head

# CI-invoked entry points — scripts run by the pipeline are entry points too
grep -rhnE "^\s+(run|script|command):" .github/workflows/*.y*ml .gitlab-ci.yml 2>/dev/null | head -20
```

**Non-obvious entry points are where the surprises are.** A nightly job, a queue consumer, or a CI script nobody mentioned is exactly what breaks when you change a shared component. Enumerate them before concluding the entry-point map is complete — and if you couldn't establish them, tag the gap `[unverified]` rather than omitting it.
