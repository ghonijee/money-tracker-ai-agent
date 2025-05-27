# Expense Tracker AI Agent

Expense Tracker AI Agent is an AI-powered backend service that helps users track, categorize, and analyze their expenses and incomes via natural language interfaces, including WhatsApp integration. The agent leverages LLMs to interpret user queries, extract structured data, and interact with a transaction database.

## Tech Stack

- **Python 3.12**
- **FastAPI** – Web API framework
- **SQLAlchemy** – ORM for database access
- **Alembic** – Database migrations
- **OpenAI / LLMs** – Natural language processing
- **heyoo** – WhatsApp API integration
- **Granian (uv)** – ASGI server
- **Docker** – Containerization
- **pytest** – Testing framework
- **Jinja2** – Prompt templating

## How to Run

### 1. Clone the Repository

```sh
git clone https://github.com/ghonijee/expense-tracker-ai-agent.git
cd expense-tracker-ai-agent
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env` and fill in the required values (e.g., database URL, OpenAI key, WhatsApp credentials):

```sh
cp .env.example .env
```

### 3. Install Dependencies

You can use `uv` (recommended) or `pip`:

```sh
# Using uv
uv sync

# Or using pip
pip install -r requirements.txt
```

### 4. Run Database Migrations

```sh
alembic upgrade head
```

### 5. Start the Application

#### Using Docker

```sh
docker-compose up --build
```

#### Or Locally

```sh
# Using uv
uv run granian --interface asgi src.main:app --reload

# Or using uvicorn
uvicorn app.main:app --reload
```

### 6. Run Tests

```sh
pytest
```

## Call to Action

Ready to automate your expense tracking with AI?

- Try out the API and connect your WhatsApp to start managing your finances smarter!
- Star this repo if you find it useful.
- Open an issue for feedback or feature requests.
