CREATE TABLE deals (
  id SERIAL PRIMARY KEY,
  business_name VARCHAR(255) NOT NULL,
  street_address VARCHAR(255) NOT NULL,
  city VARCHAR(120) NOT NULL,
  state VARCHAR(2) NOT NULL,
  county VARCHAR(120),
  zoning_status VARCHAR(50) DEFAULT 'not_evaluated',
  licensing_status VARCHAR(50) DEFAULT 'not_evaluated',
  inspection_status VARCHAR(50) DEFAULT 'not_evaluated',
  infrastructure_status VARCHAR(50) DEFAULT 'not_evaluated',
  entity_status VARCHAR(50) DEFAULT 'not_evaluated',
  risk_score INT DEFAULT 0,
  risk_level VARCHAR(50) DEFAULT 'Low',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE services (
  id SERIAL PRIMARY KEY,
  deal_id INT NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
  service_name VARCHAR(100) NOT NULL
);

CREATE TABLE parcel_data (
  id SERIAL PRIMARY KEY,
  deal_id INT UNIQUE NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
  parcel_id VARCHAR(120),
  zoning_district VARCHAR(120),
  parcel_owner VARCHAR(255),
  property_classification VARCHAR(120)
);

CREATE TABLE risk_radar (
  id SERIAL PRIMARY KEY,
  deal_id INT UNIQUE NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
  zoning_risk INT DEFAULT 0,
  licensing_risk INT DEFAULT 0,
  inspection_risk INT DEFAULT 0,
  infrastructure_risk INT DEFAULT 0,
  veterinary_risk INT DEFAULT 0,
  entity_risk INT DEFAULT 0,
  total_score INT DEFAULT 0,
  level VARCHAR(50) DEFAULT 'Low'
);

CREATE TABLE required_licenses (
  id SERIAL PRIMARY KEY,
  deal_id INT NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  responsible_team VARCHAR(80)
);

CREATE TABLE inspection_agencies (
  id SERIAL PRIMARY KEY,
  deal_id INT NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE due_diligence_tasks (
  id SERIAL PRIMARY KEY,
  deal_id INT NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
  task TEXT NOT NULL,
  responsible_team VARCHAR(80),
  completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  deal_id INT NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
  filename VARCHAR(255) NOT NULL,
  file_path VARCHAR(255) NOT NULL
);
