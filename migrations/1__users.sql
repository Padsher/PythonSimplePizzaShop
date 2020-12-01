CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    login TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE IF NOT EXISTS public.sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    updated_at TIMESTAMP WITH TIME ZONE
);