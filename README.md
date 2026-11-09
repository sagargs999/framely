# Framely

A photo and video sharing app with a FastAPI backend and a Streamlit frontend. Users register, log in with JWT authentication, upload media with captions, and browse a feed of posts.

## Features

- User registration and login with JWT tokens (fastapi-users)
- Protected endpoints: only logged-in users can upload or delete posts
- Photo and video uploads with captions <!-- confirm ImageKit or local storage -->
- Feed of posts, newest first
- Delete your own posts
- Streamlit frontend for logging in, uploading, and browsing

## Tech stack

- **Backend:** FastAPI, fastapi-users, SQLAlchemy (async)
- **Database:** SQLite via aiosqlite
- **Media storage:** ImageKit <!-- change if you store files elsewhere -->
- **Frontend:** Streamlit
- **Tooling:** uv

## Getting started

### Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
git clone https://github.com/sagargs999/framely.git
cd framely
uv sync
```

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env`.

| Variable | Description |
| --- | --- |
| `SECRET` | Random string used to sign JWTs and reset tokens |
| `IMAGEKIT_PRIVATE_KEY` | ImageKit private key |
| `IMAGEKIT_PUBLIC_KEY` | ImageKit public key |
| `IMAGEKIT_URL_ENDPOINT` | ImageKit URL endpoint |

<!-- match this table to the names in your .env.example -->

### Run the backend

```bash
uv run python -m uvicorn app.fast_api_proj.app:app --reload
```

The API runs at http://localhost:8000, with interactive docs at http://localhost:8000/docs.

### Run the frontend

In a second terminal:

```bash
uv run python -m streamlit run frontend.py
```

The app opens at http://localhost:8501.

## API overview

| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| POST | `/auth/register` | Create an account | No |
| POST | `/auth/jwt/login` | Log in (form data: `username` = email, `password`) | No |
| GET | `/feed` | List posts, newest first | Yes |
| POST | `/upload` | Upload a photo or video with a caption | Yes |
| DELETE | `/posts/{post_id}` | Delete one of your posts | Yes |

<!-- replace the last three rows with your real routes from app.py -->

## Project structure

```
app/fast_api_proj/
├── app.py        # FastAPI app and routes
├── db.py         # SQLAlchemy models and session setup
├── users.py
