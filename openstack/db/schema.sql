CREATE SCHEMA vm_data;
CREATE TABLE vm_data.vm_metrics (
    id BIGSERIAL PRIMARY KEY,
    date_time TIMESTAMP NOT NULL,
    vm_id VARCHAR NOT NULL,
    vm_name VARCHAR NOT NULL,
    vm_state INTEGER NOT NULL,
    vm_tags JSONB,
    vm_resources JSONB NOT NULL,
    vm_price_min NUMERIC NOT NULL
);

CREATE TABLE vm_data.vm_changes (
    id BIGSERIAL PRIMARY KEY,
    date_time TIMESTAMP NOT NULL,
    vm_id VARCHAR NOT NULL,
    vm_name VARCHAR NOT NULL,
    vm_state INTEGER NOT NULL,
    vm_tags JSONB,
    vm_price NUMERIC NOT NULL,
    vm_config JSONB NOT NULL
);

CREATE TABLE vm_data.vm_prices (
    id BIGSERIAL PRIMARY KEY,
    resource VARCHAR NOT NULL,
    price NUMERIC NOT NULL
);

CREATE TABLE vm_data.vm_raw (
    id BIGSERIAL PRIMARY KEY,
    date_time TIMESTAMP NOT NULL,
    vm_id VARCHAR NOT NULL,
    vm_name VARCHAR NOT NULL,
    vm_state INTEGER NOT NULL,
    vm_tags JSONB,
    vm_price NUMERIC NOT NULL,
    vm_config JSONB NOT NULL
);
