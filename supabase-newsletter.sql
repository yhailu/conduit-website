-- ============================================
-- ORCHESTRAFLOW NEWSLETTER TABLES
-- Run this in your Supabase SQL Editor
-- ============================================

-- Newsletter subscribers table
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  source TEXT DEFAULT 'website',
  subscribed_at TIMESTAMPTZ DEFAULT NOW(),
  unsubscribed_at TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_newsletter_email ON newsletter_subscribers(email);
CREATE INDEX idx_newsletter_active ON newsletter_subscribers(is_active) WHERE is_active = true;

ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public subscribe" ON newsletter_subscribers
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read" ON newsletter_subscribers
  FOR SELECT USING (true);

CREATE POLICY "Allow update for unsubscribe" ON newsletter_subscribers
  FOR UPDATE USING (true);

-- Newsletter campaigns table
CREATE TABLE IF NOT EXISTS newsletter_campaigns (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  recipient_count INTEGER DEFAULT 0,
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'sending', 'sent', 'failed'))
);

ALTER TABLE newsletter_campaigns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow campaign operations" ON newsletter_campaigns
  FOR ALL USING (true);

-- Consultations table (if not exists)
CREATE TABLE IF NOT EXISTS consultations (
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

ALTER TABLE consultations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public consultation inserts" ON consultations
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow consultation reads" ON consultations
  FOR SELECT USING (true);

-- Stats view
CREATE OR REPLACE VIEW newsletter_stats AS
SELECT 
  COUNT(*) FILTER (WHERE is_active = true) as active_subscribers,
  COUNT(*) as total_subscribers,
  COUNT(*) FILTER (WHERE subscribed_at > NOW() - INTERVAL '7 days') as new_this_week,
  COUNT(*) FILTER (WHERE subscribed_at > NOW() - INTERVAL '30 days') as new_this_month
FROM newsletter_subscribers;
