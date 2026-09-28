# Service Health Troubleshooting

## Overview

AcmeCloud services expose health information that support agents can use when investigating service availability problems.

A service health check helps determine whether a service is operational, degraded, or unavailable.

## Service Health Responses

A healthy service normally reports an operational status.

If the service reports a degraded or unavailable status, the support agent should investigate the affected service before recommending customer-side changes.

## Support Procedure

When a customer reports service availability problems:

1. Check the current service health status.
2. Identify whether the issue affects one service or multiple services.
3. Check the relevant service health information and recent incident information.
4. If the service is degraded or unavailable, follow the applicable incident or escalation procedure.
5. Do not recommend restarting production services unless the authorized support procedure explicitly permits the action.

## Important Restriction

Support agents must not perform unauthorized production infrastructure changes.

A service restart is a controlled operational action and must only be performed through an authorized tool or workflow when the agent has the required permission.

## Escalation

Escalate the issue to the appropriate infrastructure team when:

- The service remains unavailable after approved troubleshooting.
- Multiple customers are affected.
- A high-priority service outage is suspected.
- The support agent does not have authorization to perform the required operational action.