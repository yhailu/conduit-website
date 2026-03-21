-- ============================================
-- ORCHESTRAFLOW CONSULTATIONS TABLE
-- Run this in your Supabase SQL Editor
-- ============================================

CREATE TABLE consultations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  company TEXT NOT NULL,
  company_size TEXT,
  industry TEXT,
  message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_consultations_email ON consultations(email);
CREATE INDEX idx_consultations_created_at ON consultations(created_at DESC);

-- Enable Row Level Security
ALTER TABLE consultations ENABLE ROW LEVEL SECURITY;

-- Allow public inserts (the form is public)
CREATE POLICY "Allow public inserts" ON consultations
  FOR INSERT
  WITH CHECK (true);

-- Allow public reads (for admin — restrict later as needed)
CREATE POLICY "Allow public reads" ON consultations
  FOR SELECT
  USING (true);
