-- tenant template: create tables inside ws_<id>
-- This is a template file, not a direct migration
-- It will be used by scripts to create tenant schemas

-- CREATE SCHEMA ws_<uuid>;

-- CREATE TABLE ws_<uuid>.projects (
--   id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
--   name text NOT NULL,
--   description text,
--   created_by uuid,
--   created_at timestamptz DEFAULT now()
-- );

-- CREATE TABLE ws_<uuid>.items (
--   id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
--   project_id uuid REFERENCES ws_<uuid>.projects(id),
--   data jsonb,
--   created_at timestamptz DEFAULT now()
-- );

-- If ENABLE_PGVECTOR=true include:
-- CREATE EXTENSION IF NOT EXISTS vector;
-- CREATE TABLE ws_<uuid>.embeddings (
--   id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
--   project_id uuid,
--   text_chunk text,
--   vector vector
-- );
