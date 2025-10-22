-- public/001_create_public_tables.sql
CREATE TABLE public.users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE public.workspaces (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  owner_id uuid REFERENCES public.users(id),
  created_at timestamptz DEFAULT now()
);

CREATE TABLE public.workspace_members (
  workspace_id uuid REFERENCES public.workspaces(id),
  user_id uuid REFERENCES public.users(id),
  role text NOT NULL DEFAULT 'member',
  PRIMARY KEY (workspace_id, user_id)
);

CREATE TABLE public.artifact_store (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid REFERENCES public.workspaces(id),
  key text NOT NULL,
  url text NOT NULL,
  size_bytes bigint,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE public.events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid,
  project text,
  type text,
  payload jsonb,
  created_at timestamptz DEFAULT now()
);
