-- CreateTable
CREATE TABLE "Moneta_LagoSubscription" (
    "id" UUID    NOT NULL,
    "customer_id" UUID,
    "plan_id" UUID,
    "status" VARCHAR(255) NOT NULL DEFAULT 'active',
    "balance_threshold" JSONB NOT NULL DEFAULT '{}',
    "remaining_balance" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Moneta_LagoSubscription_pkey" PRIMARY KEY ("id")
);

