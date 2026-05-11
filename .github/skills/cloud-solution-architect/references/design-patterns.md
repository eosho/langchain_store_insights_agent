# Cloud Design Patterns

44 patterns organized by primary concern. WAF pillar mapping: **R**=Reliability, **S**=Security, **CO**=Cost Optimization, **OE**=Operational Excellence, **PE**=Performance Efficiency.

## Messaging & Communication

| Pattern | Summary | Pillars |
|---------|---------|---------|
| **Asynchronous Request-Reply** | Decouple request/response with polling or callbacks | R, PE |
| **Claim Check** | Split large messages; store payload separately, pass reference | R, PE |
| **Choreography** | Services coordinate via events without central orchestrator | R, OE |
| **Competing Consumers** | Multiple consumers process messages from shared queue concurrently | R, PE |
| **Messaging Bridge** | Connect incompatible messaging systems | R, OE |
| **Pipes and Filters** | Decompose complex processing into reusable filter stages | R, OE |
| **Priority Queue** | Prioritize requests so higher-priority work is processed first | R, PE |
| **Publisher/Subscriber** | Decouple senders from receivers via topics/subscriptions | R, PE |
| **Queue-Based Load Leveling** | Buffer requests with a queue to smooth intermittent loads | R, PE |
| **Sequential Convoy** | Process related messages in order while allowing parallel groups | R, PE |

## Reliability & Resilience

| Pattern | Summary | Pillars |
|---------|---------|---------|
| **Bulkhead** | Isolate resources per workload to prevent cascading failure | R |
| **Circuit Breaker** | Stop calling a failing service; fail fast to protect resources | R |
| **Compensating Transaction** | Undo previously committed steps when a later step fails | R |
| **Health Endpoint Monitoring** | Expose health checks for load balancers and orchestrators | R, OE |
| **Leader Election** | Coordinate distributed instances by electing a leader | R |
| **Retry** | Handle transient faults by retrying with exponential backoff | R |
| **Saga** | Manage data consistency across microservices with compensating transactions | R |
| **Scheduler Agent Supervisor** | Coordinate distributed actions with retry and failure handling | R |

## Data Management

| Pattern | Summary | Pillars |
|---------|---------|---------|
| **Cache-Aside** | Load data on demand into cache from data store | PE |
| **CQRS** | Separate read and write models for independent scaling | PE, R |
| **Event Sourcing** | Store state as append-only sequence of domain events | R, OE |
| **Index Table** | Create indexes over frequently queried fields in data stores | PE |
| **Materialized View** | Pre-compute views over data for efficient queries | PE |
| **Sharding** | Distribute data across partitions for scale and performance | PE, R |
| **Static Content Hosting** | Serve static content from cloud storage/CDN directly | PE, CO |
| **Valet Key** | Grant clients limited direct access to storage resources | S, PE |

## Design & Structure

| Pattern | Summary | Pillars |
|---------|---------|---------|
| **Ambassador** | Offload cross-cutting concerns to a helper sidecar proxy | OE |
| **Anti-Corruption Layer** | Translate between new and legacy system models | OE, R |
| **Backends for Frontends** | Create separate backends per frontend type (mobile, web, etc.) | OE, PE |
| **Compute Resource Consolidation** | Combine multiple workloads into fewer compute instances | CO |
| **External Configuration Store** | Externalize configuration from deployment packages | OE |
| **Sidecar** | Deploy helper components alongside the main service | OE |
| **Strangler Fig** | Incrementally migrate legacy systems by replacing pieces | OE, R |

## Security & Access

| Pattern | Summary | Pillars |
|---------|---------|---------|
| **Federated Identity** | Delegate authentication to an external identity provider | S |
| **Gatekeeper** | Protect services using a dedicated broker that validates requests | S |
| **Quarantine** | Isolate and validate external assets before allowing use | S |
| **Rate Limiting** | Control consumption rate of resources by consumers | R, S |
| **Throttling** | Control resource consumption to sustain SLAs under load | R, PE |

## Deployment & Scaling

| Pattern | Summary | Pillars |
|---------|---------|---------|
| **Deployment Stamps** | Deploy multiple independent copies of application components | R, PE |
| **Edge Workload Configuration** | Configure workloads differently across diverse edge devices | OE |
| **Gateway Aggregation** | Aggregate multiple backend calls into a single client request | PE |
| **Gateway Offloading** | Offload shared functionality (SSL, auth) to a gateway | OE, S |
| **Gateway Routing** | Route requests to multiple backends using a single endpoint | OE |
| **Geode** | Deploy backends to multiple regions for active-active serving | R, PE |

## Reference

See [Cloud Design Patterns](https://learn.microsoft.com/azure/architecture/patterns/) for detailed implementation guidance per pattern.
