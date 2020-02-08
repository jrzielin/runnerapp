CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS runs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    run_date TIMESTAMP WITH TIME ZONE NOT NULL,
    distance INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    metric BOOLEAN NOT NULL DEFAULT FALSE,
    warmup INTEGER,
    cooldown INTEGER,
    run_type VARCHAR(128),
    location VARCHAR(128),
    notes TEXT NOT NULL DEFAULT '',
    created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS intervals (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES runs(id),
    distance INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    metric BOOLEAN NOT NULL DEFAULT FALSE,
    created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE run_comments (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES runs(id),
    user_id INTEGER REFERENCES users(id),
    comment TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);