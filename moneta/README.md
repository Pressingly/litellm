# Moneta Component for LiteLLM

## Overview

`moneta` is a dedicated component for extending the [LiteLLM](https://docs.litellm.ai/) open-source project. The primary goal of `moneta` is to house all custom modifications and additions within this distinct folder/module. This approach offers several advantages:

*   **Reduced Merge Conflicts:** By keeping our changes separate from the core LiteLLM codebase, we minimize the likelihood of conflicts when pulling updates from the main project.
*   **Improved Code Isolation:** `moneta` provides a clear separation of concerns, making it easier to identify, manage, and debug our specific enhancements.
*   **Enhanced Traceability:** All changes made for our specific needs are centralized within the `moneta` directory, simplifying tracking and understanding of our contributions.

## Development Conventions

To maintain a consistent and organized codebase within `moneta`, please adhere to the following conventions:

1.  **Modular Packages:** Create a new package (sub-directory) for each distinct feature or area of modification. For example:
    *   `billing`
    *   `user_logging`
    *   `cost_calculator`

2.  **Standard Package Structure:** Each package should, at a minimum, include the following:
    *   `readme.md`: A dedicated README file providing an introduction and documentation for that specific module/package.
    *   `apis/`: A directory to house any new or modified API endpoints related to the package.
    *   `tests/`: A directory containing unit tests and/or integration tests for the package's functionality.

3.  **Database Table Naming Convention:**
    *   All tables created by MONETA components should be prefixed with `Moneta_` to distinguish them from LiteLLM's tables (which use the `LiteLLM_` prefix).
    *   Example: `Moneta_LagoSubscription`, `Moneta_UserBilling`, etc.
    *   This convention helps prevent naming conflicts and makes it clear which tables belong to the MONETA component.

## Setup and Running

### Prerequisites

1.  Ensure you have a `.env` file in the project root and that the `DATABASE_URL` variable is correctly configured.

### Installation and Database Setup

1.  **Install Dependencies:** For detailed instructions on setting up your development environment, please refer to the official LiteLLM contributing guide: [https://docs.litellm.ai/docs/extras/contributing_code](https://docs.litellm.ai/docs/extras/contributing_code)
    ```bash
    poetry install --with dev --extras proxy
    ```

2.  **Database Seeding (Prisma):**
    ```bash
    prisma generate
    prisma db push
    ```
3 . database migration

```bash
prisma migrate deploy
```

### Running the Proxy Server

```bash
dotenv uvicorn litellm.proxy.proxy_server:app --host localhost --port 4004 --reload
```

To run db migrations
```
cd moneta/billing && prisma migrate deploy
```

### PRISMA
- after generate model, we need to manually add copy from `moneta/.../schema.prisma` in to `./schema.prisma` then run `prisma generate` to make it work

I'm new to this. if you have better solution. let me know. Maybe they have a mechanism to merge it.