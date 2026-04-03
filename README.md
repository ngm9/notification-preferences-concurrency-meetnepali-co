# Notification Preferences API — Engineering Task

## Task Overview

You are working on the backend of a multi-tenant SaaS platform that lets enterprise customers manage notification preferences for their users. Each tenant is an isolated organization, and users within a tenant control how they receive notifications — via email, SMS, push, and at what frequency. The API is built with FastAPI and PostgreSQL and is already deployed, but two critical issues have been escalated from production: unauthenticated cross-tenant data access and silent data loss from concurrent writes. Both issues affect real customer data and must be resolved with production-grade correctness — not just patched.

## Objectives

- Enforce tenant-scoped access control on both read and write endpoints, correctly differentiating between regular users and admin users within a tenant
- Ensure that cross-tenant access is firmly and consistently rejected with the correct HTTP response, regardless of the requester's role
- Implement HTTP-level optimistic concurrency control on the preferences update endpoint, using standard conditional request headers to prevent silent data overwrites
- Ensure the API surfaces meaningful, semantically correct HTTP responses for all authorization and concurrency failure scenarios
- Produce clean, well-structured code with proper separation of concerns between routing, business logic, and data access

## Application & Database Access

**API**

- Server: `http://<DROPLET_IP>:8000`
- `GET /health` — health check
- `GET /api/v1/users/{user_id}/preferences` — fetch preferences
- `PUT /api/v1/users/{user_id}/preferences` — update preferences

**Database**

- Host: `<DROPLET_IP>`, Port: `5432`
- Database: `notif_prefs`, User: `notif_user`, Password: `notif_pass`
- Connect using any PostgreSQL client (pgAdmin, DBeaver, psql, DataGrip) to inspect tables and seed data

## How to Verify

- A regular user cannot read or update another user's preferences within the same tenant; an admin can access any user within their own tenant but is rejected for cross-tenant requests
- GET responses include an ETag header; PUT requests require a valid If-Match header — missing or stale values are rejected with the correct HTTP status
- Two concurrent PUTs with the same ETag result in one success and one rejection — no silent overwrites

## Helpful Tips

- Use `curl -v` to inspect response headers: `curl -v -H "Authorization: Bearer <token>" http://<DROPLET_IP>:8000/api/v1/users/{user_id}/preferences`
- Test conditional updates: `curl -v -X PUT -H "Authorization: Bearer <token>" -H "If-Match: \"<etag>\"" -H "Content-Type: application/json" -d '{"sms_enabled": true}' http://<DROPLET_IP>:8000/api/v1/users/{user_id}/preferences`
- Consider how JWT claims can drive tenant-scoped authorization and where that check belongs in the request lifecycle
- Think about which HTTP status codes best distinguish "not allowed" from "resource has changed"
- Explore how ETag values should be generated and how conditional headers (If-Match) work per HTTP semantics
- Think about where concurrency conflict detection should live — database, service, or route layer — and the trade-offs of each
