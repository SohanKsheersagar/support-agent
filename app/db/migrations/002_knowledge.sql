CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;

CREATE TABLE kb_chunks (
    source_id text PRIMARY KEY,
    title text NOT NULL,
    text text NOT NULL,
    version text NOT NULL,
    audience text NOT NULL CHECK (audience IN ('public', 'internal')),
    model text NOT NULL,
    embedding public.vector(384) NOT NULL
);
