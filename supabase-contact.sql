-- ============================================
-- ORCHESTRAFLOW CONTACT MESSAGES TABLE
-- Run this in your Supabase SQL Editor
-- ============================================

CREATE TABLE contact_messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT,
  email TEXT NOT NULL,
  subject TEXT,
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_contact_messages_created ON contact_messages(created_at DESC);

ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public inserts" ON contact_messages
  FOR INSERT WITH CHECK (true);
