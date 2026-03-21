-- ============================================
-- ORCHESTRAFLOW SIGNUPS TABLE
-- Run this in your Supabase SQL Editor
-- ============================================

-- Create the signups table
CREATE TABLE signups (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  source TEXT DEFAULT 'unknown',
  signed_up_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create an index on email for faster lookups
CREATE INDEX idx_signups_email ON signups(email);

-- Create an index on signed_up_at for sorting
CREATE INDEX idx_signups_signed_up_at ON signups(signed_up_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE signups ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anyone to INSERT (for public signups)
CREATE POLICY "Allow public inserts" ON signups
  FOR INSERT
  WITH CHECK (true);

-- Policy: Allow anyone to SELECT (for admin panel - you can restrict this later)
-- For production, you might want to remove this and create a secure admin route
CREATE POLICY "Allow public reads" ON signups
  FOR SELECT
  USING (true);

-- ============================================
-- OPTIONAL: Create a view for signup stats
-- ============================================

CREATE VIEW signup_stats AS
SELECT 
  COUNT(*) as total_signups,
  COUNT(CASE WHEN signed_up_at > NOW() - INTERVAL '24 hours' THEN 1 END) as last_24h,
  COUNT(CASE WHEN signed_up_at > NOW() - INTERVAL '7 days' THEN 1 END) as last_7d,
  COUNT(CASE WHEN signed_up_at > NOW() - INTERVAL '30 days' THEN 1 END) as last_30d
FROM signups;
