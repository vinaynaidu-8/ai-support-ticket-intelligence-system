# AcmeCloud API Authentication

## Overview

AcmeCloud API requests require valid authentication credentials.

Authentication failures are different from rate-limit failures and should be investigated separately.

## HTTP 401 Responses

An HTTP 401 response generally indicates that the request could not be authenticated.

Common causes include:

- Missing authentication credentials.
- Invalid API credentials.
- Expired credentials.
- Incorrect authentication configuration.

## Support Procedure

When a customer reports HTTP 401 responses:

1. Confirm the affected API endpoint.
2. Confirm that authentication credentials are being supplied.
3. Verify that the credentials have not expired or been revoked.
4. Confirm that the customer is using the correct authentication mechanism.
5. Check AcmeCloud service health if multiple customers are reporting authentication failures.

## Security Restriction

Support agents must never request that customers provide secret API keys or passwords through support conversations.

If credential exposure is suspected, the customer should be directed toward the approved credential rotation procedure.

## Escalation

Escalate to the security or infrastructure team when:

- Authentication fails despite valid credentials.
- Multiple unrelated customers experience authentication failures.
- There is evidence of unauthorized credential use.
- The authentication service shows signs of degradation.