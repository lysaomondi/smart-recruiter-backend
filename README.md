# Smart Recruiter Backend

Smart Recruiter is an assessment and interview-management platform. Recruiters create assessments, invite candidates, review submissions, grade responses, and share feedback. This repository contains the Django REST API for the Smart Recruiter application.

**Deployed application:** [smart-recruiter-eta.vercel.app](https://smart-recruiter-eta.vercel.app/)

## Features

- JWT authentication for recruiter and interviewee accounts.
- Role-based permissions for protected resources.
- Assessment authoring, publishing, previewing, and closing.
- MCQ, text, coding, whiteboard, BDD, and pseudocode questions.
- Candidate invitations, timed attempts, answer autosave, and final submission.
- Automatic MCQ grading, manual grading, results, rankings, statistics, and feedback.
- Codewars kata search and import support for coding assessments.

## Technology

- Python 3.12+
- Django 6.1 and Django REST Framework
- Simple JWT
- SQLite for local development and PostgreSQL support for production
- `django-cors-headers` and `python-dotenv`

## Project Structure

```text
smart-recruiter-backend/
├── accounts/          # Users, authentication, roles, and permissions
├── assessments/       # Assessments, questions, choices, and publishing
├── invitations/       # Candidate invitation lifecycle
├── attempts/          # Timed attempts, answers, autosave, and submission
├── results/           # Grading, rankings, feedback, and statistics
├── integrations/      # External services, including Codewars
├── config/            # Django settings and root URL configuration
├── manage.py          # Django management entry point
└── requirements.txt   # Python dependencies
```

## Local Setup

1. Clone the repository and enter it.

   ```bash
   git clone <repository-url>
   cd smart-recruiter-backend
   ```

2. Create and activate a virtual environment.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   On Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file using the example below.

5. Apply migrations and start the server.

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

   The local API runs at `http://127.0.0.1:8000/`.

6. Run tests.

   ```bash
   python manage.py test
   ```

## Environment Variables

Keep credentials and production settings outside version control. Example `.env`:

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgresql://username:password@localhost:5432/smart_recruiter
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
CODEWARS_API_BASE_URL=https://www.codewars.com/api/v1
```

`DATABASE_URL` is intended for PostgreSQL deployments. Local development can use SQLite until database URL configuration is added to `config/settings.py`.

## API Overview

Protected endpoints expect an access token:

```http
Authorization: Bearer <access-token>
```

### Authentication

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/auth/register/` | Register a recruiter or interviewee. |
| POST | `/auth/login/` | Log in and receive JWT tokens. |
| POST | `/auth/token/refresh/` | Refresh an access token. |
| POST | `/auth/logout/` | End the authenticated session. |
| GET | `/auth/me/` | Get the current user's profile and role. |

### Assessments

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET, POST | `/assessments/` | List or create assessments. |
| GET, PATCH, DELETE | `/assessments/{id}/` | View, edit, or delete an assessment. |
| POST | `/assessments/{id}/publish/` | Publish an assessment. |
| POST | `/assessments/{id}/close/` | Close an assessment. |
| GET | `/assessments/{id}/preview/` | Get an assessment preview. |
| GET, POST | `/assessments/{id}/questions/` | List or add questions. |
| GET, PATCH, DELETE | `/assessments/{id}/questions/{question_id}/` | Manage a question. |
| GET, POST | `/questions/{id}/choices/` | List or add MCQ choices. |
| GET, PATCH, DELETE | `/questions/{id}/choices/{choice_id}/` | Manage an MCQ choice. |

### Invitations and Attempts

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/invitations/` | List candidate or recruiter invitations. |
| POST | `/invitations/{id}/accept/` | Accept an invitation. |
| POST | `/invitations/{id}/decline/` | Decline an invitation. |
| POST | `/invitations/{id}/attempt/` | Start or resume an attempt. |
| GET | `/attempts/{id}/` | Get an attempt, questions, and saved answers. |
| PUT, PATCH | `/attempts/{id}/answers/{question_id}/` | Autosave an answer. |
| GET | `/attempts/{id}/remaining-time/` | Get remaining time. |
| POST | `/attempts/{id}/submit/` | Submit and lock an attempt. |

### Results and Integrations

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/assessments/{id}/results/` | Get assessment results and rankings. |
| GET | `/assessments/{id}/statistics/` | Get assessment statistics. |
| GET | `/results/{id}/review/` | Review answers and grading details. |
| POST, PATCH | `/results/{id}/feedback/` | Create or update feedback. |
| POST | `/results/{id}/grade/` | Manually grade open-ended answers. |
| POST | `/results/{id}/release/` | Release a result to its interviewee. |
| GET | `/my-results/` | List the current interviewee's results. |
| GET | `/integrations/codewars/katas/` | Search Codewars kata metadata. |
| POST | `/integrations/codewars/import/` | Import a Codewars kata. |

## Domain Workflow

```text
Recruiter -> Creates assessment -> Adds questions -> Publishes
                                                    |
                                                    v
                                           Invites interviewee
                                                    |
                                                    v
Interviewee -> Accepts -> Starts timed attempt -> Autosaves -> Submits
                                                    |
                                                    v
                      Auto-grades MCQs + manually grades remaining answers
                                                    |
                                                    v
                                   Creates, releases, and shares result
```

## Core Models and Statuses

| App | Primary models | Responsibility |
| --- | --- | --- |
| `accounts` | Custom User; optional RecruiterProfile and IntervieweeProfile | Identity, role, active status, authentication, and permissions. |
| `assessments` | Assessment, Question, Choice | Assessment authoring, publishing, question definitions, and MCQ answers. |
| `invitations` | Invitation | Candidate invitation lifecycle. |
| `attempts` | AssessmentAttempt, Answer | Timed work, validation, expiry, autosave, and submission. |
| `results` | Result, Feedback | Grading, rankings, statistics, feedback, and release state. |
| `integrations` | Optional CodewarsKata cache | Codewars metadata search and import. |

Use consistent status enums across the API:

| Resource | Suggested statuses |
| --- | --- |
| Assessment | `draft`, `published`, `closed` |
| Invitation | `pending`, `accepted`, `declined`, `expired` |
| Attempt | `not_started`, `in_progress`, `submitted`, `expired` |
| Result | `unreleased`, `released` |

## Question Types

| Type | Description | Grading |
| --- | --- | --- |
| `mcq` | Single- or multiple-selection question. | Automatic comparison with correct choices. |
| `text` | Written response. | Manual. |
| `coding` | Programming problem, optionally linked to Codewars. | Manual or integration-supported. |
| `whiteboard` | Diagram or design response. | Manual. |
| `bdd` | Behaviour-driven development scenario. | Manual. |
| `pseudocode` | Algorithm expressed as pseudocode. | Manual. |

## Team

| Member | Ownership | Django apps |
| --- | --- | --- |
| Najib | Authentication, custom user model, JWT, and permissions | `accounts` |
| Lysa | Recruiter assessment management and question authoring | `assessments` |
| Jane | Invitations, attempts, answers, and submission rules | `invitations`, `attempts` |
| Sahal | Results, grading, statistics, feedback, and Codewars | `results`, `integrations` |

### Recommended Branches

| Member | Branch |
| --- | --- |
| Najib | `feature/accounts-auth` |
| Lysa | `feature/assessments-management` |
| Jane | `feature/invitations-attempts` |
| Sahal | `feature/results-codewars` |

### Dependency Order

1. Implement the custom user model, JWT configuration, and reusable role permissions.
2. Define `Assessment`, `Question`, and `Choice`, including shared status enums.
3. Implement invitations, attempts, answer validation, expiry handling, and submission.
4. Add auto-grading, manual grading, rankings, feedback, and statistics.
5. Integrate Codewars metadata into coding questions.

Use a short-lived integration branch or pull request first for shared settings, root URL configuration, and the custom user model. It will give all feature branches a stable base and reduce migration conflicts.

## Current Implementation Status

The Django project structure and required dependencies are in place. The domain app modules have been created, but the models, serializers, views, URL registrations, authentication configuration, and tests are still to be implemented. The routes and architecture in this README are the agreed target contract for that work.

## License

This project is distributed under the terms in [LICENSE](LICENSE).
