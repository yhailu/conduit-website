-- ============================================
-- ORCHESTRAFLOW PREVIEW LINKS TABLE
-- Run this in your Supabase SQL Editor
-- ============================================

CREATE TABLE preview_links (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  token TEXT NOT NULL UNIQUE,
  business_name TEXT NOT NULL,
  original_url TEXT,
  demo_file TEXT NOT NULL,
  email TEXT,
  views INTEGER DEFAULT 0,
  expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_preview_links_token ON preview_links(token);

-- Disable RLS for simplicity (internal use only)
ALTER TABLE preview_links DISABLE ROW LEVEL SECURITY;
