-- BuiltEnvironment.ai - Database Initialization Script
-- This script runs automatically when PostgreSQL container first starts

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create Langflow database (Langflow needs its own database)
CREATE DATABASE langflow;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE builtenvironment TO postgres;
GRANT ALL PRIVILEGES ON DATABASE langflow TO postgres;

-- Create UUID extension for primary keys
\c builtenvironment
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

\c langflow
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log initialization
\c builtenvironment
DO $$
BEGIN
  RAISE NOTICE 'BuiltEnvironment.ai database initialized successfully';
  RAISE NOTICE 'TimescaleDB extension enabled';
  RAISE NOTICE 'Langflow database created';
END
$$;
