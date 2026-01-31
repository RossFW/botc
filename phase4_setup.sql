-- ==========================================
-- Phase 4B: Game Editing Setup
-- ==========================================

-- Add permission_level column to access_codes
ALTER TABLE access_codes ADD COLUMN IF NOT EXISTS permission_level TEXT DEFAULT 'submit';

-- Update existing submit code
UPDATE access_codes SET permission_level = 'submit' WHERE code = 'REDACTED_CODE';

-- Add new edit access code
INSERT INTO access_codes (code, description, permission_level)
VALUES ('REDACTED_CODE', 'Edit access', 'edit')
ON CONFLICT (code) DO UPDATE SET permission_level = 'edit';

-- Add UPDATE policy for games table
DROP POLICY IF EXISTS "Games can be updated" ON games;
CREATE POLICY "Games can be updated" ON games FOR UPDATE USING (true);

-- ==========================================
-- Phase 4C: Scripts Table Setup
-- ==========================================

-- Create scripts table
CREATE TABLE IF NOT EXISTS scripts (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Normal', 'Teensyville')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on scripts table
ALTER TABLE scripts ENABLE ROW LEVEL SECURITY;

-- RLS policies for scripts
DROP POLICY IF EXISTS "Scripts viewable by all" ON scripts;
CREATE POLICY "Scripts viewable by all" ON scripts FOR SELECT USING (true);

DROP POLICY IF EXISTS "Scripts insertable" ON scripts;
CREATE POLICY "Scripts insertable" ON scripts FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Scripts updatable" ON scripts;
CREATE POLICY "Scripts updatable" ON scripts FOR UPDATE USING (true);

-- Seed scripts from botc_config.py (won't insert duplicates due to ON CONFLICT)
INSERT INTO scripts (name, category) VALUES
    ('Trouble Brewing', 'Normal'),
    ('Bad Moon Rising', 'Normal'),
    ('Sects & Violets', 'Normal'),
    ('Trouble in Violets', 'Normal'),
    ('No Greater Joy', 'Teensyville'),
    ('Over the River', 'Teensyville'),
    ('Laissez un Faire', 'Teensyville'),
    ('Trouble in Legion', 'Normal'),
    ('Hide & Seek', 'Normal'),
    ('Trouble Brewing on Expert Mode', 'Normal'),
    ('Trained Killer', 'Normal'),
    ('Irrational Behavior', 'Normal'),
    ('Binary Supernovae', 'Normal'),
    ('A Leech of Distrust', 'Teensyville'),
    ('Everybody Can Play', 'Normal')
ON CONFLICT (name) DO NOTHING;

-- Verify setup
SELECT 'Access Codes:' as info;
SELECT code, permission_level FROM access_codes;

SELECT 'Scripts:' as info;
SELECT name, category FROM scripts ORDER BY name;
