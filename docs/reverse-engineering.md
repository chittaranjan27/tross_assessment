# LinkedIn Reverse Engineering Documentation

> **Note**: This document describes the typical HTTP contracts observed via browser developer tools. No actual secrets or valid session cookies are committed to the repository.

## URL Resolution
Public URL: `https://www.linkedin.com/in/<slug>`
The internal identity is typically mapped to this `<slug>`.

## Authentication Requirements
LinkedIn's private API (Voyager) requires valid session cookies and a CSRF token:
- **Cookies**: `li_at` (main session cookie), `JSESSIONID` (CSRF token)
- **Headers**: `csrf-token` matching the JSESSIONID.
- **User-Agent**: Requires a valid modern browser user-agent.

## Endpoints

### 1. Profile View
- **URL**: `https://www.linkedin.com/voyager/api/identity/profiles/{slug}/profileView`
- **Method**: GET
- **Purpose**: Returns the core profile summary (headline, summary, location).

### 2. Experience & Education
Often returned either nested in `profileView` or via separate endpoints like:
- `https://www.linkedin.com/voyager/api/graphql` with specific query ids for positions and education.

## Response Structure
The Voyager API often returns an `included` array (a graph of entities).
Entities are referenced via `*entityUrn`.
A robust parser must:
1. Build a dictionary mapping `entityUrn` to the actual entity.
2. Resolve references safely without assuming they exist.

## Rate Limiting and Failure Modes
- **429 Too Many Requests**: Triggered if fetching too many profiles too quickly on a single session.
- **401/403**: Triggered if the session cookie is invalid, expired, or if the account is flagged.
- **404**: Returned if the slug does not exist or the profile is set to fully private.

## Implementation Details
For this assignment, we are mocking the direct HTTP fetch since we do not have a valid, dedicated, and authorized session to include. However, the architecture is designed so that the `LinkedInClient` could simply uncomment the `httpx.AsyncClient` fetch to become fully functional.
