-- ============================================================
-- HeroCall Platform Schema
-- Run this in Supabase SQL Editor to create platform tables
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -----------------------------------------------------------
-- Customers table
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  full_name text,
  company_name text,
  phone text,
  plan text DEFAULT 'trial',        -- trial, starter, pro, enterprise
  status text DEFAULT 'active',     -- active, suspended, cancelled
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);

-- -----------------------------------------------------------
-- AI Agents table (one per customer, could be multiple)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS agents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  agent_name text DEFAULT 'AI Receptionist',
  industry text,                    -- hvac, dental, legal, real_estate, insurance, etc.
  business_name text NOT NULL,
  business_phone text,
  business_address text,
  business_hours jsonb,             -- {"mon": "8am-5pm", "tue": "8am-5pm", ...}
  services jsonb,                   -- ["AC Repair", "Heating", "Installation"]
  greeting_message text,
  system_prompt text,               -- the full AI prompt
  calendar_url text,                -- calendly or google calendar link
  phone_number text,                -- the Vapi/Twilio number assigned
  vapi_assistant_id text,           -- placeholder for Vapi integration
  status text DEFAULT 'setup',      -- setup, active, paused, cancelled
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agents_customer_id ON agents(customer_id);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);

-- -----------------------------------------------------------
-- Call logs table
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS call_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  customer_id uuid NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  caller_phone text,
  caller_name text,
  call_duration_seconds int,
  call_summary text,
  call_outcome text,                -- appointment_booked, message_taken, transferred, spam
  transcript text,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_call_logs_agent_id ON call_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_call_logs_customer_id ON call_logs(customer_id);
CREATE INDEX IF NOT EXISTS idx_call_logs_created_at ON call_logs(created_at DESC);

-- -----------------------------------------------------------
-- Appointments table
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS appointments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  customer_id uuid NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  client_name text,
  client_phone text,
  client_email text,
  service_type text,
  appointment_date timestamptz,
  notes text,
  status text DEFAULT 'scheduled',  -- scheduled, completed, cancelled, no_show
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_appointments_agent_id ON appointments(agent_id);
CREATE INDEX IF NOT EXISTS idx_appointments_customer_id ON appointments(customer_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);

-- -----------------------------------------------------------
-- Auto-update updated_at trigger
-- -----------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS customers_updated_at ON customers;
CREATE TRIGGER customers_updated_at
  BEFORE UPDATE ON customers
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS agents_updated_at ON agents;
CREATE TRIGGER agents_updated_at
  BEFORE UPDATE ON agents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- -----------------------------------------------------------
-- Row Level Security (RLS)
-- -----------------------------------------------------------
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Policies: customers can only see their own data
-- (Using service role from backend bypasses RLS, but these
--  protect direct Supabase client access)

CREATE POLICY customers_own ON customers
  FOR ALL USING (id = auth.uid());

CREATE POLICY agents_own ON agents
  FOR ALL USING (customer_id = auth.uid());

CREATE POLICY call_logs_own ON call_logs
  FOR ALL USING (customer_id = auth.uid());

CREATE POLICY appointments_own ON appointments
  FOR ALL USING (customer_id = auth.uid());
