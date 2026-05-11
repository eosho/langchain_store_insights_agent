# Technology Choices

## Decision Framework

For each technology area, evaluate: **requirements → constraints → tradeoffs → select**.

| Area | Key Options | Selection Criteria |
|------|-------------|-------------------|
| **Compute** | App Service, Functions, Container Apps, AKS, VMs, Batch | Hosting model, scaling, cost, team skills |
| **Storage** | Blob Storage, Data Lake, Files, Disks, Managed Lustre | Access patterns, throughput, cost tier |
| **Data stores** | SQL Database, Cosmos DB, PostgreSQL, Redis, Table Storage | Consistency model, query patterns, scale |
| **Messaging** | Service Bus, Event Hubs, Event Grid, Queue Storage | Ordering, throughput, pub/sub vs queue |
| **Networking** | Front Door, Application Gateway, Load Balancer, Traffic Manager | Global vs regional, L4 vs L7, WAF |
| **AI services** | Azure OpenAI, AI Search, AI Foundry, Document Intelligence | Model needs, data grounding, orchestration |
| **Containers** | Container Apps, AKS, Container Instances | Operational control vs simplicity |

## Best Practices

| Practice | Key Guidance |
|----------|-------------|
| **API design** | RESTful conventions, resource-oriented URIs, HATEOAS, versioning via URL path or header |
| **API implementation** | Async operations, pagination, idempotent PUT/DELETE, content negotiation, ETag caching |
| **Autoscaling** | Scale on metrics (CPU, queue depth, custom), cool-down periods, predictive scaling, scale-in protection |
| **Background jobs** | Use queues or scheduled triggers, idempotent processing, poison message handling, graceful shutdown |
| **Caching** | Cache-aside pattern, TTL policies, cache invalidation strategies, distributed cache for multi-instance |
| **CDN** | Static asset offloading, cache-busting with versioned URLs, geo-distribution, HTTPS enforcement |
| **Data partitioning** | Horizontal (sharding), vertical, functional partitioning; partition key selection for even distribution |
| **Partitioning strategies** | Hash-based, range-based, directory-based; rebalancing approach, cross-partition query avoidance |
| **Host name preservation** | Preserve original host header through proxies/gateways for cookies, redirects, auth flows |
| **Message encoding** | Schema evolution (Avro/Protobuf), backward/forward compatibility, schema registry |
| **Monitoring & diagnostics** | Structured logging, distributed tracing (W3C Trace Context), metrics, alerts, dashboards |
| **Transient fault handling** | Retry with exponential backoff + jitter, circuit breaker, idempotency keys, timeout budgets |

## Performance Antipatterns

Avoid these common patterns that degrade performance under load:

| Antipattern | Problem | Fix |
|-------------|---------|-----|
| **Busy Database** | Offloading too much processing to the database | Move logic to application tier, use caching |
| **Busy Front End** | Resource-intensive work on frontend request threads | Offload to background workers/queues |
| **Chatty I/O** | Many small I/O requests instead of fewer large ones | Batch requests, use bulk APIs, buffer writes |
| **Extraneous Fetching** | Retrieving more data than needed | Project only required fields, paginate, filter server-side |
| **Improper Instantiation** | Recreating expensive objects per request | Use singletons, connection pooling, HttpClientFactory |
| **Monolithic Persistence** | Single data store for all data types | Polyglot persistence — right store for each workload |
| **No Caching** | Repeatedly fetching unchanged data | Cache-aside pattern, CDN, output caching, Redis |
| **Noisy Neighbor** | One tenant consuming all shared resources | Bulkhead isolation, per-tenant quotas, throttling |
| **Retry Storm** | Aggressive retries overwhelming a recovering service | Exponential backoff + jitter, circuit breaker, retry budgets |
| **Synchronous I/O** | Blocking threads on I/O operations | Async/await, non-blocking I/O, reactive streams |

## Reference

- [Azure Technology Choices](https://learn.microsoft.com/azure/architecture/guide/technology-choices/compute-decision-tree) — Detailed decision trees
- [Azure Best Practices](https://learn.microsoft.com/azure/architecture/best-practices/) — Implementation details
- [Performance Antipatterns](https://learn.microsoft.com/azure/architecture/antipatterns/) — Detection and remediation
