-- database/init.sql

-- 1. Bronze Schema: Raw data ingestion
CREATE SCHEMA IF NOT EXISTS bronze;

-- 2. Silver Schema: Cleaned, filtered and enriched data
CREATE SCHEMA IF NOT EXISTS silver;

-- 3. Gold Schema: Business-level aggregates and ML features
CREATE SCHEMA IF NOT EXISTS gold;

-- Output success message to the console during initialization
DO $$ 
BEGIN
    RAISE NOTICE 'Database schemas (bronze, silver, gold) initialized successfully for PrescriptAI.';
END $$;