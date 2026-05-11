# Project-Specific Extensions

Decision aids, selection guides, and checklists tailored to this project's infrastructure patterns.

## Compute Selection Guide

| Requirement | Container Apps | AKS | App Service | Functions |
|-------------|---------------|-----|-------------|-----------|
| Microservices | Preferred | Complex workloads | Simple APIs | Event-driven |
| Auto-scale | Built-in (KEDA) | KEDA/HPA | Built-in | Built-in |
| Networking | VNet inject | Full control | VNet inject | VNet inject |
| Min cost | Scale to zero | Always-on nodes | Always-on plan | Pay-per-execution |
| GPU workloads | Workload profiles | Node pools | Not supported | Not supported |
| Team expertise | Low ops overhead | Kubernetes required | Lowest overhead | Lowest overhead |
| Max control | Medium | Full | Low | Low |

### Decision Heuristic

1. **Event-driven, short-lived** → Azure Functions
2. **HTTP APIs, microservices, moderate control** → Container Apps
3. **Full Kubernetes needed** (service mesh, CRDs, node pools) → AKS
4. **Simple web apps, lowest ops** → App Service

## Data Platform Selection

| Requirement | Cosmos DB | SQL Database | PostgreSQL Flex | Storage Tables |
|-------------|-----------|--------------|-----------------|----------------|
| Global distribution | Built-in | Geo-replication | Read replicas | GRS/RA-GRS |
| Schema flexibility | Schema-free | Fixed schema | Fixed schema | Schema-free |
| Consistency models | 5 levels | Strong only | Strong only | Strong/eventual |
| Cost model | RU-based | DTU/vCore | vCore | Pay-per-transaction |
| Best for | High-scale NoSQL | Relational, ACID | Open-source compat | Simple key-value |

## Networking Patterns

### Hub-Spoke (Most Common)

```
Hub VNet
├── Azure Firewall / NVA
├── VPN Gateway / ExpressRoute
└── Shared services (DNS, monitoring)

Spoke VNets (peered to hub)
├── Workload A (Container Apps Environment)
├── Workload B (AKS cluster)
└── Workload C (App Service VNet-integrated)
```

### Key Networking Decisions

| Decision | Default | When to Change |
|----------|---------|----------------|
| Private endpoints | Always | Never — public endpoints are a security risk |
| DNS | Azure Private DNS Zones | Custom DNS when integrating with on-prem |
| Ingress | Azure Front Door / App Gateway | Direct access only for internal workloads |
| Egress | Azure Firewall | NAT Gateway for simpler/cheaper egress |
| Service mesh | Not needed | AKS with complex inter-service auth |

## Cost Optimization Strategies

1. **Right-size first**: Use Azure Advisor recommendations
2. **Reserved instances**: 1-year (20-30% savings) or 3-year (40-60%) for steady-state workloads
3. **Scale to zero**: Container Apps, Functions for variable workloads
4. **Spot instances**: Batch processing, dev/test environments
5. **Storage tiering**: Hot → Cool → Archive lifecycle policies
6. **Shared services**: Centralize monitoring, DNS, firewalls in hub

## Availability Targets

| SLA Target | Architecture Pattern | Typical Cost Impact |
|------------|---------------------|---------------------|
| 99.9% | Single region, zone-redundant | Baseline |
| 99.95% | Single region, multiple instances, zone-redundant | +20-30% |
| 99.99% | Multi-region active-passive | +80-100% |
| 99.999% | Multi-region active-active | +150%+ |
