CREATE TABLE users (id uuid PRIMARY KEY, username text, created_at timestamptz default now());
CREATE TABLE tasks (id uuid PRIMARY KEY, user_id uuid REFERENCES users(id), title text, payload jsonb, status text, idempotency_key text, created_at timestamptz default now(), updated_at timestamptz default now());
CREATE TABLE task_logs (id serial PRIMARY KEY, task_id uuid REFERENCES tasks(id), level text, message text, meta jsonb, created_at timestamptz default now());
CREATE TABLE api_keys (id serial PRIMARY KEY, name text, key text, masked text, created_at timestamptz default now());
CREATE TABLE files (id uuid PRIMARY KEY, object_key text, size bigint, content_type text, scanned boolean default false, created_at timestamptz default now());
