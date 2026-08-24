-- 1. Enable TimescaleDB Extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- 2. Route Metadata & Baseline DGCA Traffic Weights
CREATE TABLE IF NOT EXISTS route_metadata (
    route_id VARCHAR(10) PRIMARY KEY,
    origin_iata VARCHAR(3) NOT NULL,
    destination_iata VARCHAR(3) NOT NULL,
    origin_city VARCHAR(50) NOT NULL,
    destination_city VARCHAR(50) NOT NULL,
    dgca_passenger_weight NUMERIC(6, 4) NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

-- Seed top domestic corridors with representative DGCA passenger volume weights
INSERT INTO route_metadata (route_id, origin_iata, destination_iata, origin_city, destination_city, dgca_passenger_weight)
VALUES 
    ('DEL-BOM', 'DEL', 'BOM', 'New Delhi', 'Mumbai', 0.2200),
    ('BOM-DEL', 'BOM', 'DEL', 'Mumbai', 'New Delhi', 0.2150),
    ('DEL-BLR', 'DEL', 'BLR', 'New Delhi', 'Bengaluru', 0.1450),
    ('BLR-DEL', 'BLR', 'DEL', 'Bengaluru', 'New Delhi', 0.1400),
    ('BOM-BLR', 'BOM', 'BLR', 'Mumbai', 'Bengaluru', 0.1000),
    ('DEL-CCU', 'DEL', 'CCU', 'New Delhi', 'Kolkata', 0.0900),
    ('BLR-HYD', 'BLR', 'HYD', 'Bengaluru', 'Hyderabad', 0.0500),
    ('MAA-DEL', 'MAA', 'DEL', 'Chennai', 'New Delhi', 0.0400)
ON CONFLICT (route_id) DO NOTHING;

-- 3. Normalized Raw Quotes Hypertable
CREATE TABLE IF NOT EXISTS raw_flight_quotes (
    id BIGSERIAL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    crawl_id UUID NOT NULL,
    source_platform VARCHAR(50) NOT NULL,
    carrier VARCHAR(50) NOT NULL,
    flight_number VARCHAR(20) NOT NULL,
    route_id VARCHAR(10) REFERENCES route_metadata(route_id),
    advance_window VARCHAR(5) NOT NULL,
    departure_date DATE NOT NULL,
    departure_time TIME,
    base_fare NUMERIC(10, 2) NOT NULL,
    fuel_surcharge NUMERIC(10, 2) DEFAULT 0.0,
    statutory_taxes NUMERIC(10, 2) DEFAULT 0.0,
    convenience_fee NUMERIC(10, 2) DEFAULT 0.0,
    total_fare NUMERIC(10, 2) NOT NULL,
    is_sold_out BOOLEAN DEFAULT FALSE,
    is_outlier BOOLEAN DEFAULT FALSE,
    audit_s3_key VARCHAR(255)
);

-- Convert to Hypertable partitioned across time
SELECT create_hypertable('raw_flight_quotes', 'recorded_at', if_not_exists => TRUE);

-- 4. Computed APIx Daily Index Store
CREATE TABLE IF NOT EXISTS apix_daily_indices (
    index_date DATE PRIMARY KEY,
    index_value NUMERIC(8, 4) NOT NULL,
    base_period VARCHAR(20) DEFAULT '2026-08-01',
    daily_inflation_rate NUMERIC(6, 4),
    formula_used VARCHAR(50) DEFAULT 'Weighted Laspeyres',
    computed_at TIMESTAMPTZ DEFAULT NOW()
);