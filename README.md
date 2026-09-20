# [Nome Progetto - es. VibeCore API]
A robust, role-based REST API for audio catalog management and user interactions, built with FastAPI and PostgreSQL.

## 🎯 Core Business Logic
The system implements strict Role-Based Access Control (RBAC) with three primary actors:
- **Admin:** Can soft-delete users/songs, and manage role elevations (promote/demote other admins).
- **Musician:** Inherits Listener permissions. Can upload and manage their own tracks with dynamic visibility (public/private).
- **Listener:** Can fetch available public tracks and manage a personal "favorites" collection.

## 🏗️ Tech Stack
- **Framework:** Python / FastAPI
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Containerization:** Docker & Docker Compose
- **Tooling:** Ruff (Linter/Formatter), Alembic (Migrations)

## 🗄️ Database Architecture

![DB Schemas](./docs/entity-relationship_diagram.png)

