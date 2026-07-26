# Following indirection

When a call path disappears. Read the section matching the mechanism you've hit — the symptom usually tells you which one.

## Diagnosing which mechanism you've hit

| Symptom | Likely mechanism |
|---|---|
| Call is to an interface with several implementations | DI container, or strategy selection |
| Call is to an interface with exactly one implementation | DI — just find the implementor |
| No caller found for a method that clearly runs | Framework callback, reflection, or annotation-driven |
| Behavior doesn't match the code you're reading | Interception / AOP, or you're reading generated output |
| Something publishes and nothing appears to consume | Event bus, message broker, or a consumer in another repo |
| The method body is trivial but behavior is complex | A proxy or decorator wraps it |
| Grep finds the string but no code path reaches it | Config-driven wiring, or genuinely dead |

---

## Dependency injection

The most common cause. The type you can see is an interface; the type that runs is chosen at wiring time.

**Find the implementations first:**
```bash
# Adapt keyword to language: implements / extends / ": Interface" / "impl Trait for"
grep -rn "implements OrderRepository\|: OrderRepository\|impl OrderRepository for" --include="*.*" .
```

**One implementation:** that's your answer.

**Several:** find the wiring. Look for explicit registration before assuming annotation scanning:
- Configuration classes and modules — search for the interface name in files named `*Config*`, `*Module*`, `*Registry*`, `*Startup*`
- Qualifiers, named bindings, or profile/environment conditions on the injection site
- XML or config-file wiring in older enterprise systems — still very common
- Conditional registration: "use implementation A when property X is set"

**The profile trap:** the implementation bound in production may differ from the one bound in tests or locally. Check which environment's wiring you're reading. A trace built against test wiring describes a system that doesn't exist in production.

## Interfaces with runtime selection

A factory or strategy chooses by a value known only at runtime.

```bash
grep -rn "switch\|when (\|match \|if.*type ==\|\.get(type)" --include="*.*" <factory file>
```

Find where the selector value comes from — a config property, a database column, a request field. Then establish which value the flow you're tracing actually carries. Trace the *value*, not just the mechanism, or you've documented the switch without knowing which branch runs.

## Events and message buses

**In-process event buses:** publisher and subscriber are decoupled by an event type. Search for the event type name, not the publishing call.

```bash
grep -rn "OrderPlaced" --include="*.*" . | grep -v "publish\|emit\|raise"
```

**Message brokers:** the consumer is frequently in another repository or another team's service. Search by the **topic or queue name**, which appears in config on both sides:

```bash
grep -rn "orders\.placed\|ORDERS_TOPIC" --include="*.y*ml" --include="*.properties" --include="*.tf" .
```

If the consumer isn't in this repository, that's a legitimate `[unverified]` hop. Record the topic name and what would resolve it — an org-wide search, a service catalogue, or the platform team. Don't guess at consumers.

**Check delivery semantics while you're there.** At-least-once delivery against a non-idempotent consumer is a real defect and one of the more valuable things a trace can surface.

## Framework callbacks and lifecycle hooks

Methods invoked by a framework have no visible caller. If a method clearly runs but nothing calls it, check whether its name or annotation is a framework contract — lifecycle hooks, scheduled methods, request handlers, serialization callbacks, test fixtures.

The framework's own documentation on invocation order matters here: initialization order bugs are common and invisible in the code.

## Interception, proxies, and aspects

Behavior that doesn't match the code you're reading usually means something wraps it. Common wrappers: transactions, caching, retry, security checks, logging, metrics.

Look for: annotations on the method or class that imply behavior, proxy or interceptor registration in configuration, decorator classes wrapping the same interface, middleware chains.

**This matters for tracing because wrapped behavior is invisible at the call site.** A method annotated as transactional starts a transaction that appears nowhere in its body — and if you miss it, your trace puts the transaction boundary in the wrong place, which is exactly the kind of error that causes a bad change later.

## Reflection and dynamic dispatch

Names constructed at runtime defeat grep entirely.

```bash
grep -rn "Class.forName\|getattr(\|importlib\|Activator.CreateInstance\|method_missing\|eval(" --include="*.*" .
```

Where you find one, the resolvable question is usually "what values can reach this?" — trace the string's origin rather than its destination. Often it comes from a config file or database table that enumerates the possibilities, and that enumeration is your answer.

Note explicitly that grep-based analysis is blind here. Any "this is unused" claim in a codebase using reflection is `[inferred]` at best.

## Config-driven wiring

Enterprise systems frequently assemble behavior from configuration — rules engines, workflow definitions, feature flags, routing tables, BPMN, database-held configuration.

The code is generic; the behavior lives in data. Grep the config, not just the source:

```bash
grep -rn "<handler-name>" --include="*.y*ml" --include="*.xml" --include="*.json" --include="*.properties" .
```

Where configuration lives in a **database table**, the code will not tell you what runs. You need a read on that table — record it as an access requirement if you don't have one, because no amount of code reading substitutes for it.

## Generated code

If the file you're reading is generated, it isn't the source of truth and editing it is wrong.

```bash
grep -rln "DO NOT EDIT\|auto-generated\|@Generated\|Code generated by" --include="*.*" . | head
```

Find the generator and its input schema — an OpenAPI spec, a `.proto`, an ORM schema, an IDL. Trace through the *input*, and note in the trace that the code shown is generated so a later reader doesn't try to change it.

## Cross-repository boundaries

The single most common hard stop for an FDE, because you may not have the other repository yet.

Before concluding, check: is the client a published library whose source is in the local package cache? Is there a service catalogue? Is there an OpenAPI spec or `.proto` in this repo describing the other side?

If none of that resolves it, stop and record it properly:

> Hop 8: `inventory-service` `/reserve`. Behavior beyond this boundary not established `[unverified]` — separate repository, access requested (see `00b-access.md` #7).

That is an honest, actionable trace. Guessing at what the other service does — and then designing against the guess — is how integrations fail in ways nobody can debug afterwards.
