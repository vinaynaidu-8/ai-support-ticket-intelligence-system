# AcmeCloud API Rate Limiting

## Overview

AcmeCloud APIs enforce request limits to protect platform stability and maintain predictable service performance.

Rate limits are applied based on the customer's subscription plan and API usage pattern.

## HTTP 429 Responses

When a client exceeds its applicable API request limit, AcmeCloud may return HTTP status code 429.

A 429 response indicates that the request was rejected because the applicable rate limit was exceeded.

Support agents should not immediately assume that a 429 response indicates an AcmeCloud platform outage.

## Support Procedure

When a customer reports repeated HTTP 429 responses:

1. Confirm the affected API endpoint.
2. Determine whether the customer's request volume recently increased.
3. Check AcmeCloud service health for the affected API.
4. Review the customer's subscription and applicable rate limits.
5. If the customer is generating legitimate traffic that exceeds the configured limit, determine whether a rate-limit increase is appropriate.

## Escalation

Escalate the issue to the infrastructure team when:

- The customer is receiving unexpected 429 responses without a corresponding increase in traffic.
- Service health indicates an API degradation.
- Multiple unrelated customers report similar rate-limit problems.
- The configured customer limit appears inconsistent with the customer's subscription.

## Important Restriction

Support agents must not promise a permanent rate-limit increase without confirmation from the appropriate team.