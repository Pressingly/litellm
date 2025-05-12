# Cost Tracking Package

This package implements the integration between LiteLLM and Lago for handling billing and entitlement checks in OpenWebUI.

## Components

1. **BillingLogger**: A custom logger that implements the LiteLLM CustomLogger interface to handle:
   - Pre-call entitlement checks
   - Post-call usage tracking and balance updates

2. **LagoSubscription**: A model class that represents a subscription in the system, with:
   - Balance tracking
   - Status management
   - Threshold-based activation

3. **SubscriptionDBService**: A database service for managing subscription data with:
   - CRUD operations for subscriptions
   - Balance updates
   - Status management

## Setup

1. Configure environment variables:
   ```bash
   LAGO_API_KEY=your_api_key
   LAGO_URL=https://api.lago.com
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

2. Install dependencies:
   ```bash
   pip install prisma
   ```

3. Initialize and run database migrations:
   ```bash
   # Create initial migration
   cd moneta/cost_tracking
   prisma migrate dev --name create_lago_subscriptions_table

   # Apply migrations in production
   prisma migrate deploy
   ```

4. Configure LiteLLM to use the BillingLogger:
   ```python
   from moneta.cost_tracking.billing_logger import BillingLogger
   
   billing_logger = BillingLogger(
       lago_api_key=os.getenv("LAGO_API_KEY"),
       lago_url=os.getenv("LAGO_URL")
   )
   
   # Add to LiteLLM config
   litellm.callbacks = [billing_logger]
   ```

## Usage

The package automatically handles:
1. Checking subscription status before processing requests
2. Tracking usage and updating balances after successful requests
3. Managing subscription status based on balance thresholds

## Development

To add new features or modify existing ones:
1. Update the schema in `schema.prisma`
2. Create a new migration: `prisma migrate dev --name "description_of_changes"`
3. Apply the migration: `prisma migrate deploy`
4. Update the models and services accordingly
5. Update tests

## Database Migrations

The package uses Prisma for database migrations. Here's how to work with migrations:

1. **Create a new migration**:
   ```bash
   prisma migrate dev --name "description_of_changes"
   ```

2. **Apply migrations**:
   ```bash
   prisma migrate deploy
   ```

3. **View migration history**:
   ```bash
   ls migrations/
   ```

Always create a new migration when:
- Adding new tables
- Modifying table structure
- Adding or removing columns
- Changing column types
- Adding or removing indexes 