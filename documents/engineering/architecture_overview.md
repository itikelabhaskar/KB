# Architecture Overview — TechNova Platform

## System Architecture

The TechNova Platform follows a microservices architecture deployed on AWS EKS (Kubernetes). The system is divided into the following services:

### Core Services

1. **API Gateway** (Kong) — Routes external traffic, handles rate limiting and authentication.
2. **User Service** — Manages user accounts, profiles, and authentication tokens.
3. **Billing Service** — Processes payments via Stripe integration. Handles subscriptions, invoices, and payment retries.
4. **Document Service** — Stores and indexes enterprise documents. Integrates with our search engine.
5. **Notification Service** — Sends emails (via SendGrid), Slack messages, and in-app notifications.

### Data Stores

- **PostgreSQL 16** — Primary database for user data, billing records, and document metadata.
- **Redis 7** — Session cache, rate limiting counters, and pub/sub for real-time features.
- **Elasticsearch 8** — Full-text search for documents and audit logs.
- **Amazon S3** — Object storage for uploaded files and document assets.

### Infrastructure

- **Kubernetes (EKS)** — Container orchestration for all services.
- **Terraform** — Infrastructure as Code for all AWS resources.
- **GitHub Actions** — CI/CD pipeline for automated testing and deployment.
- **Datadog** — Monitoring, logging, and alerting.

## Design Principles

1. **Loose coupling:** Services communicate via REST APIs and message queues (SQS).
2. **12-factor app:** All configuration via environment variables, stateless processes.
3. **Graceful degradation:** If the notification service is down, core payment processing continues.
4. **Defense in depth:** Multiple layers of authentication and authorization.

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite |
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Search | Elasticsearch 8 |
| Storage | Amazon S3 |
| CI/CD | GitHub Actions |
| Monitoring | Datadog |
| Infrastructure | Kubernetes (EKS), Terraform |
