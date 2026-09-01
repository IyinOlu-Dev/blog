**Blog Website**

A full-stack blogging platform with a FastAPI backend, PostgreSQL database, and a vanilla JS/HTML frontend. Users can register, log in, write posts, and like other users' posts.

**Live demo:** [blog-f1vp.onrender.com](https://blog-f1vp.onrender.com) 

**## Features**

- User registration and login with hashed passwords (Argon2) and JWT-based authentication
- Create, read, update, and delete blog posts
- Drafts vs. published posts (`published` flag) — unpublished posts are excluded from public listings
- Post previews with auto-generated content snippets on the home feed
- Like/unlike posts
- Paginated post listings (`limit` / `offset` query params, capped at 50 per page)

**## Tech stack**

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API framework
- [SQLAlchemy](https://www.sqlalchemy.org/) (ORM) + [PostgreSQL](https://www.postgresql.org/) — data layer
- [Alembic](https://alembic.sqlalchemy.org/) — database migrations
- [python-jose](https://github.com/mpdavis/python-jose) — JWT token creation/verification
- [Argon2](https://github.com/hynek/argon2-cffi) — password hashing
- [Pydantic](https://docs.pydantic.dev/) — request/response validation

**Frontend**
- Vanilla HTML, CSS, and JavaScript (no framework) — login/auth page, post feed, single post view, post creation

**Deployment**
- Hosted on [Render](https://render.com/)

**## API overview**

| Method | Endpoint | Description | Auth required |
|--------|----------|-------------|----------------|
| GET | `/` | Paginated home feed with post previews | No |
| GET | `/posts` | List published posts | No |
| GET | `/posts/{id}` | Get a single post | No |
| POST | `/posts` | Create a new post | Yes |
| PATCH | `/posts/{id}` | Update a post | Yes |
| DELETE | `/posts/{id}` | Delete a post | Yes |
| POST | `/users` | Register a new user | No |
| POST | `/login` | Log in and receive a JWT | No |

**## Data model**

- **User** — id, username, email, hashed password, created_at; has many posts
- **Post** — id, title, content, published flag, created_at, owner (foreign key to User)
- **Like** — composite key of post_id + user_id, tracks which users liked which posts

**## Running locally**

Requires Python 3.11+ and a PostgreSQL database.

**```bash**
git clone https://github.com/IyinOlu-Dev/blog.git
cd blog
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with your database connection details and JWT secret:

```
DATABASE_URL=postgresql://user:password@localhost:5432/blog_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Run migrations:**

```bash
alembic upgrade head
```

**Start the server:**

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`. Open `frontend/index.html` in a browser (or serve it with a simple static server) to use the UI.

**## Project structure**

```
blog/
├── backend/
│   ├── main.py        # FastAPI app and route definitions
│   ├── model.py        # SQLAlchemy models (User, Post, Liked)
│   ├── schema.py        # Pydantic request/response schemas
│   ├── database.py       # DB engine and session setup
│   ├── oauth.py         # JWT creation and auth dependency
│   └── utils.py         # Password hashing helpers
├── alembic/            # Database migration scripts
├── frontend/
│   ├── index.html        # Home feed
│   ├── auth.html         # Login / register
│   ├── post.html         # Single post view
│   ├── create-post.html    # New post form
│   └── app.js           # Frontend logic
└── requirements.txt
```

## License
**MIT**
