-- ============================================
-- ORCHESTRAFLOW WEB DEVELOPMENT TABLES
-- Run this in your Supabase SQL Editor
-- ============================================

-- Portal clients (businesses with demo access)
CREATE TABLE portal_clients (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  business_name TEXT NOT NULL,
  original_url TEXT,
  demo_url TEXT,
  improvements JSONB DEFAULT '[]'::jsonb,
  metrics JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_portal_clients_email ON portal_clients(email);

-- Build requests from portal clients
CREATE TABLE build_requests (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID REFERENCES portal_clients(id) ON DELETE CASCADE,
  message TEXT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_build_requests_client ON build_requests(client_id);
CREATE INDEX idx_build_requests_status ON build_requests(status);

-- Web development leads from landing page
CREATE TABLE webdev_leads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  business_name TEXT,
  website_url TEXT,
  email TEXT NOT NULL,
  phone TEXT,
  source TEXT DEFAULT 'web-development',
  city TEXT,
  state TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_webdev_leads_email ON webdev_leads(email);
CREATE INDEX idx_webdev_leads_created ON webdev_leads(created_at DESC);

-- ============================================
-- Row Level Security
-- ============================================

ALTER TABLE portal_clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE build_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE webdev_leads ENABLE ROW LEVEL SECURITY;

-- Portal clients: allow reads (for login auth via anon key)
CREATE POLICY "Allow read access" ON portal_clients
  FOR SELECT USING (true);

-- Build requests: allow reads and inserts
CREATE POLICY "Allow read access" ON build_requests
  FOR SELECT USING (true);

CREATE POLICY "Allow inserts" ON build_requests
  FOR INSERT WITH CHECK (true);

-- Web dev leads: allow public inserts (landing page form)
CREATE POLICY "Allow public inserts" ON webdev_leads
  FOR INSERT WITH CHECK (true);

-- Web dev leads: server-side reads only
CREATE POLICY "Server reads only" ON webdev_leads
  FOR SELECT USING (false);
