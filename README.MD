# 🐦 Twitter Clone API

📄 A training REST API clone of Twitter built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, and **asyncpg**. Implements core Twitter features: users, tweets, likes, follows, media uploads, and API-key-based authentication.

---

## ✨ Features

- 🔐 API key authentication
- 📝 Create, delete, and fetch tweets
- ❤️ Likes and following system
- 🖼️ JPEG image uploads
- ⚡ Asynchronous operations
- 📑 Swagger and ReDoc documentation
- ✅ Linting and testing support

---

## 📁 Setup & Run (Docker)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/twitter-clone.git
cd twitter-clone
```

### 2. Create `.env` file in the root directory

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=twitter_clone_db
DATABASE_URL=postgresql+asyncpg://postgres:password@twitter_db:5432/twitter_clone_db
```

### 3. Launch the app via Docker Compose

```bash
docker-compose up --build
```

Once started:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Tests

```bash
pytest
```

---

## ✏️ Linting

### ✅ Ruff

```bash
ruff check . --fix
```

### ✅ flake8

```bash
flake8 src
```

### ✅ Optionally: isort / mypy / black

```bash
isort src
mypy src
black src
```

---

## 📋 Example API Requests

### → Get tweets

```http
GET /tweets
api-key: test
```

### → Post a tweet

```http
POST /tweets
Headers:
  api-key: test
Body:
{
  "content": "Hello Twitter"
}
```

### → Upload media

```http
POST /media
Headers:
  api-key: test
Form:
  file: image.jpg
```

---

## 📚 Project Structure

```
twitter_clone/
├── src/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── routes/
│   │   ├── tweets.py
│   │   ├── users.py
│   │   └── medias.py
│   └── media/
├── tests/
├── .env
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

