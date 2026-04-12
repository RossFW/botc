-- ==========================================
-- BotC Stats - Schema Migrations
-- ==========================================
-- Run these in Supabase SQL Editor if you set up your database
-- BEFORE these features were added. New users running schema.sql
-- don't need this file — it's already included.

-- Added: Delete game and delete script support
CREATE POLICY "Games can be deleted" ON games
    FOR DELETE USING (true);

CREATE POLICY "Scripts can be deleted" ON scripts
    FOR DELETE USING (true);

-- Added: Fabled/Loric modifier tracking
-- (Run this if you set up before modifiers were added)
ALTER TABLE games ADD COLUMN IF NOT EXISTS modifiers JSONB DEFAULT NULL;
