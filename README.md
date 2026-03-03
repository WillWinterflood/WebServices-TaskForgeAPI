# Recipe Intelligence API (COMP3011 Coursework 1)

## Vision
Build a production-style, data-driven web API that helps users create recipes, manage ingredients, and get nutrition insights and recommendations.  
The product/project should feel like a real backend service that a mobile/web app could use directly.

Hopefully shouldnt only be CRUD.

## What it should be like

### 1) Core API
- authentication and authorization
- resource design (ingredients, recipes, analytics)
- validation and status codes
- JSON response formats

### 2) Software engineering quality
- architecture and folder structure
- commit history by phase
- Testable, reproducible setup (local + Docker)
- Linting and tests passing in CI

### 3) Documentation and presentation
- README
- Full API docs with examples and error formats
- Evidence-based technical report with tradeoffs and reflection.

## Project Scope

### Domain entities
- `User`
- `Ingredient`
- `Recipe`
- `RecipeIngredient` (quantity + unit join model)

### Core capabilities
- Auth: register/login/JWT.
- Ingredients CRUD.
- Recipes CRUD + composition from ingredients.
- Nutrition totals per recipe/per serving.
- Analytics endpoints (macro distribution, allergens, scoring).
- Recommendation endpoint (rule-based, explainable).

## Technical Direction
- FastAPI
- SQLAlchemy + Alembic migrations
- PostgreSQL (Docker)
- Pytest
- Ruff
- GitHub Actions CI

## Planned Endpoint Groups
- `/health`
- `/api/v1/auth/*`
- `/api/v1/ingredients/*`
- `/api/v1/recipes/*`
- `/api/v1/analytics/*`
- `/api/v1/recommendations/*`

## 5-Minute Demo Path (Target)
1. Register and login.
2. Create ingredient records.
3. Create a recipe with ingredient quantities.
4. Show nutrition total endpoint.
5. Show one analytics endpoint.
6. Show one recommendation query.
7. Demonstrate protected route behavior (auth required).

## Setup (to be completed in upcoming commits)
```bash
# planned
docker compose up --build
alembic upgrade head
uvicorn app.main:app --reload
```

## Coursework Deliverables Mapping
- Code repository + commit history: this repository.
- README + setup + overview: this file.
- API documentation PDF: `docs/API_DOCUMENTATION.pdf` (to generate later).
- Technical report + GenAI declaration: submitted via Minerva.
- Slides + oral demo materials: submitted via Minerva.

Why is it coming from my personal account?
