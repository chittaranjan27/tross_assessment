# LinkedIn Profile API

A production-grade HTTP API built with FastAPI that accepts a LinkedIn profile URL and returns structured JSON information.

## Features

- **Public HTTPS API**: Secure REST API endpoints.
- **Robust Parsing**: Normalizes data and extracts experience, education, skills, and locations safely.
- **Redis Caching**: Caches normalized responses to minimize upstream requests.
- **Rate Limiting**: Protects against abuse via IP-based rate limiting.
- **Production Ready**: Fully dockerized, well-typed, tested, and CI/CD ready.
- **Architectural Isolation**: Separates LinkedIn-specific upstream logic from public API models.

## Architecture

Please see `docs/architecture.md` for a complete system diagram and request lifecycle overview.
The application follows a layered approach: Client -> FastAPI Routes -> ProfileService -> Cache -> LinkedInClient -> Normalization/Parsing.

## Reverse Engineering Approach

Please see `docs/reverse-engineering.md` for our approach to discovering the internal API structure.

## API Documentation

Interactive Swagger documentation is available at `/docs` once the server is running.

### Example Request

```http
POST /api/v1/profiles
Content-Type: application/json

{
  "profile_url": "https://www.linkedin.com/in/example-slug"
}
```

### Example Response

```json
{
  "success": true,
  "data": {
    "id": "example-slug",
    "url": "https://www.linkedin.com/in/example-slug",
    "first_name": "John",
    "last_name": "Doe",
    "name": "John Doe",
    "headline": "Senior Software Engineer",
    "location": {
      "raw": "Bengaluru, Karnataka, India",
      "city": "Bengaluru",
      "region": "Karnataka",
      "country": "India"
    },
    "experience": [
      {
        "title": "Senior Software Engineer",
        "company": "Example",
        "location": "Bengaluru",
        "start_date": "2023-01",
        "end_date": null
      }
    ],
    "education": [
      {
        "institution": "Example University",
        "degree": "MCA",
        "field_of_study": "Computer Science",
        "start_date": "2020",
        "end_date": "2022"
      }
    ],
    "skills": ["Python", "React"]
  },
  "meta": {
    "partial": false,
    "missing_sections": [],
    "retrieved_at": "2026-08-30T00:00:00Z"
  }
}
```

## Error Model
Errors return a standard JSON structure with HTTP status codes matching the context (400 for bad URLs, 404 for missing profiles, 429 for rate limits, 502 for upstream auth/gateway errors).

```json
{
  "error": {
    "code": "INVALID_PROFILE_URL",
    "message": "The provided URL is not a valid LinkedIn profile URL.",
    "request_id": "uuid-here"
  }
}
```

## Local Development

Requirements:
- Docker and Docker Compose
- Or Python 3.12+ and Redis locally

### Environment Variables
Copy `.env.example` to `.env` and fill in the values.
> Note: Never commit `.env` to source control!

### Docker
To run locally:
```bash
docker compose up --build
```
The API will be available at `http://localhost:8000`.

## Testing
Run unit and integration tests using pytest:
```bash
pytest -v
```

## Deployment
This app is ready to be deployed to platforms like AWS ECS, Render, or Railway that support Docker and Redis. Ensure the environment variables match your deployment environment.

## Security
- Validates profile URLs using strict regex to prevent SSRF.
- No session/credentials logged or committed.
- Includes rate limiting to prevent DDOS.

## Caching
Responses are cached in Redis with a configurable TTL (e.g., 6 hours).

## Rate Limiting
Configured to X requests per minute per IP to protect public availability.

## Known Limitations
- The integration client relies on private APIs which are subject to unannounced changes.
- Requires valid session cookies to successfully retrieve upstream data, meaning cookies must be maintained.
