# Recipe Intelligence API (COMP3011 Coursework 1)

## Vision
Build a production-style, data-driven web API that helps users create recipes, manage ingredients, and get nutrition insights and recommendations.  
The product/project should feel like a real backend service that a mobile/web app could use directly.

Hopefully shouldnt only be CRUD.

## What it should be like in my opinion

### 1) Core API quality (highest weighting)
- Reliable authentication and authorization.
- Clean resource design (ingredients, recipes, analytics).
- Correct validation and status codes.
- Consistent JSON response formats.

### 2) Software engineering quality
- Clear architecture and folder structure.
- Meaningful commit history by phase.
- Testable, reproducible setup (local + Docker).
- Linting and tests passing in CI.

### 3) Documentation and presentation quality
- README that lets examiners run and understand the project quickly.
- Full API docs with examples and error formats.
- Evidence-based technical report with tradeoffs and reflection.
- A 5-minute live demo path with deterministic outputs.

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

## Rubric Strategy
- **API Functionality & Implementation (25):** complete and stable endpoints with clean contracts.
- **Code Quality & Architecture (20):** service-oriented structure, migrations, typed schemas, error consistency.
- **Documentation (12):** rich OpenAPI docs, API PDF export, clear README and usage examples.
- **Version Control & Deployment (6):** phase-based commits, Dockerized run, optional live deployment.
- **Testing & Error Handling (6):** integration tests for auth/CRUD/analytics + structured errors.
- **Creativity & GenAI Usage (6):** dataset enrichment, recommendations, and explicit AI-assisted design exploration.

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
