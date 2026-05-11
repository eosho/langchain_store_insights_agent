---
name: cloud-solution-architect
description: >-
  Transform the agent into a Cloud Solution Architect following Azure Architecture Center best practices.
  Use when designing cloud architectures, reviewing system designs, selecting architecture styles,
  applying cloud design patterns, making technology choices, conducting Well-Architected Framework reviews,
  writing ADRs, planning migrations, or performing NFR analysis.
argument-hint: 'Describe the architecture problem, system requirements, or design decision to evaluate'
---

# Cloud Solution Architect

Design well-architected, production-grade cloud systems following Azure Architecture Center best practices.

**Reference files** (loaded on demand):
- [44 Cloud Design Patterns](./references/design-patterns.md) — pattern catalog mapped to WAF pillars
- [Technology Choices & Best Practices](./references/technology-choices.md) — decision framework, antipatterns
- [Project-Specific Extensions](./references/project-extensions.md) — compute, data, networking selection guides

**Templates:**
- [ADR Template](../../../templates/outputs/adr-template.md) — Architecture Decision Record with WAF assessment
- [NFR Template](../../../templates/outputs/nfr-template.md) — Non-Functional Requirements analysis

---

## Ten Design Principles for Azure Applications

| # | Principle | Key Tactics |
|---|-----------|-------------|
| 1 | **Design for self-healing** | Retry with backoff, circuit breaker, bulkhead isolation, health endpoint monitoring, graceful degradation |
| 2 | **Make all things redundant** | Eliminate single points of failure, use availability zones, deploy multi-region, replicate data |
| 3 | **Minimize coordination** | Decouple services, use async messaging, embrace eventual consistency, use domain events |
| 4 | **Design to scale out** | Horizontal scaling, autoscaling rules, stateless services, avoid session stickiness, partition workloads |
| 5 | **Partition around limits** | Data partitioning (shard/hash/range), respect compute & network limits, use CDNs for static content |
| 6 | **Design for operations** | Structured logging, distributed tracing, metrics & dashboards, runbook automation, infrastructure as code |
| 7 | **Use managed services** | Prefer PaaS over IaaS, reduce operational burden, leverage built-in HA/DR/scaling |
| 8 | **Use an identity service** | Microsoft Entra ID, managed identity, RBAC, avoid storing credentials, zero-trust principles |
| 9 | **Design for evolution** | Loose coupling, versioned APIs, backward compatibility, async messaging for integration, feature flags |
| 10 | **Build for business needs** | Define SLAs/SLOs, establish RTO/RPO targets, domain-driven design, cost modeling, composite SLAs |

See [Azure Design Principles](https://learn.microsoft.com/azure/architecture/guide/design-principles/) for details.

---

## Architecture Styles

| Style | When to Use | Key Services |
|-------|-------------|--------------|
| **N-tier** | Traditional enterprise apps, lift-and-shift | App Service, SQL Database, VNets |
| **Web-Queue-Worker** | Moderate-complexity apps with long-running tasks | App Service, Service Bus, Functions |
| **Microservices** | Complex domains, independent team scaling | AKS, Container Apps, API Management |
| **Event-driven** | Real-time processing, IoT, reactive systems | Event Hubs, Event Grid, Functions |
| **Big data** | Analytics, ML pipelines, large-scale data | Synapse, Data Factory, Databricks |
| **Big compute** | Simulations, modeling, rendering, genomics | Batch, CycleCloud, HPC VMs |

**Selection criteria:** Domain complexity → Microservices (high), N-tier (low). Team autonomy → Microservices. Data volume → Big data (TB+). Latency → Event-driven (real-time).

See [Azure Architecture Styles](https://learn.microsoft.com/azure/architecture/guide/architecture-styles/) for diagrams and tradeoffs.

---

## Well-Architected Framework (WAF) Pillars

Every architecture decision should be evaluated against all five pillars:

| Pillar | Focus | Key Questions |
|--------|-------|---------------|
| **Reliability** | Resiliency, availability, DR | RTO/RPO? Failure handling? Redundancy? |
| **Security** | Threat protection, identity, data | Managed identity? Encryption? Network controls? |
| **Cost Optimization** | Efficiency, right-sizing | Right-sized compute? Reserved instances? Waste? |
| **Operational Excellence** | Monitoring, deployment, automation | Automated deployment? Observability? Runbooks? |
| **Performance Efficiency** | Scaling, load testing, targets | Horizontal scaling? Performance baselines? Caching? |

### WAF Tradeoff Matrix

| Optimizing for... | May impact... |
|-------------------|---------------|
| Reliability (redundancy) | Cost (more resources) |
| Security (isolation) | Performance (added latency) |
| Cost (consolidation) | Reliability (shared failure domains) |
| Performance (caching) | Cost (cache infrastructure), Reliability (stale data) |

See [Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/) for pillar assessments.

---

## Mission-Critical Design

For workloads targeting **99.99%+ SLO**, address these design areas:

| Design Area | Key Considerations |
|-------------|-------------------|
| **Application platform** | Multi-region active-active, availability zones, zone-redundant compute |
| **Application design** | Stateless services, idempotent operations, graceful degradation, bulkhead isolation |
| **Networking** | Azure Front Door, DDoS Protection, private endpoints, redundant connectivity |
| **Data platform** | Multi-region Cosmos DB, zone-redundant SQL, async replication, conflict resolution |
| **Deployment & testing** | Blue-green, canary releases, chaos engineering, automated rollback |
| **Health modeling** | Composite health scores, dependency tracking, automated remediation |
| **Security** | Zero-trust, managed identity everywhere, key rotation, WAF policies |
| **Operational procedures** | Automated runbooks, incident response, game days, postmortems |

See [Mission-Critical Workloads](https://learn.microsoft.com/azure/well-architected/mission-critical/) for details.

---

## Architecture Review Workflow

### Step 1: Identify Requirements

- **Functional**: What must the system do?
- **Non-functional**: Availability target, latency (p50/p95/p99), throughput, data residency, RTO/RPO, cost constraints

### Step 2: Select Architecture Style

Match requirements to style using the table above.

### Step 3: Choose Technology Stack

Use the [technology choices reference](./references/technology-choices.md). Prefer managed services (PaaS) over IaaS.

### Step 4: Apply Design Patterns

Select from the [44 cloud design patterns](./references/design-patterns.md) based on identified concerns.

### Step 5: Address Cross-Cutting Concerns

- **Identity & access** — Microsoft Entra ID, managed identity, RBAC
- **Monitoring** — Application Insights, Azure Monitor, Log Analytics
- **Security** — Network segmentation, encryption at rest/in transit, Key Vault
- **CI/CD** — GitHub Actions, Azure DevOps Pipelines, infrastructure as code

### Step 6: Validate Against WAF Pillars

Review each pillar systematically. Document tradeoffs explicitly.

### Step 7: Document Decisions

Record architecture decisions as ADRs and non-functional requirements as NFRs using the templates linked above.

---

## Architecture Review Checklist

- [ ] Architecture maps to all 5 WAF pillars
- [ ] Design patterns selected with problem context justification
- [ ] Technology choices include comparison and tradeoff analysis
- [ ] Mission-critical designs address all 8 design areas
- [ ] Performance antipatterns identified with remediation
- [ ] Architecture decisions documented with rationale
- [ ] SLO/SLA targets explicitly stated
- [ ] Health modeling strategy defined
- [ ] Deployment strategy includes zero-downtime approach
- [ ] Security follows Zero Trust model
- [ ] Cost estimate included with SKU choices
- [ ] Network topology documented (VNet, subnets, NSGs)
- [ ] Data residency and compliance requirements met

---

## External References

- [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/guide/)
- [Cloud Design Patterns](https://learn.microsoft.com/azure/architecture/patterns/)
- [Technology Choices](https://learn.microsoft.com/azure/architecture/guide/technology-choices/compute-decision-tree)
- [Best Practices](https://learn.microsoft.com/azure/architecture/best-practices/)
- [Performance Antipatterns](https://learn.microsoft.com/azure/architecture/antipatterns/)
