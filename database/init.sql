CREATE TABLE IF NOT EXISTS "users" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "username" text,
  "avatar_url" text,
  "email" text UNIQUE NOT NULL,
  "password_hash" text NOT NULL,
  "work_email" text,
  "gmail_refresh_token" text,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE IF NOT EXISTS "applications" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "user_id" uuid NOT NULL,
  "company_name" text NOT NULL,
  "job_title" text NOT NULL,
  "current_status" text,
  "email_chain" jsonb NOT NULL DEFAULT ('[]'::jsonb),
  "applied_at" date NOT NULL,
  "updated_at" timestamptz NOT NULL DEFAULT (now()),
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE UNIQUE INDEX ON "applications" ("user_id", "company_name", "job_title");

ALTER TABLE "applications" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;