-- ==========================================
-- Phase 6: Security Hardening
-- Run this in Supabase SQL Editor
-- ==========================================

-- Step 1: Remove the dangerous SELECT policy that exposes access codes
DROP POLICY IF EXISTS "Access codes can be read for validation" ON access_codes;

-- Step 2: Create a secure validation function
-- This function validates codes server-side WITHOUT exposing the codes table
CREATE OR REPLACE FUNCTION validate_access_code(input_code TEXT)
RETURNS TABLE(is_valid BOOLEAN, permission_level TEXT)
LANGUAGE plpgsql
SECURITY DEFINER  -- Runs with elevated privileges to read access_codes
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT
        TRUE as is_valid,
        COALESCE(ac.permission_level, 'submit') as permission_level
    FROM access_codes ac
    WHERE ac.code = input_code;

    -- If no rows returned, return invalid result
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, NULL::TEXT;
    END IF;
END;
$$;

-- Step 3: Grant execute permission on the function to anon users
GRANT EXECUTE ON FUNCTION validate_access_code(TEXT) TO anon;
GRANT EXECUTE ON FUNCTION validate_access_code(TEXT) TO authenticated;

-- ==========================================
-- Verification: Test the function works
-- ==========================================
-- This should return: is_valid=true, permission_level='submit' (for your submit code)
-- SELECT * FROM validate_access_code('your-submit-code');

-- This should return: is_valid=true, permission_level='edit' (for your edit code)
-- SELECT * FROM validate_access_code('your-edit-code');

-- This should return: is_valid=false, permission_level=null
-- SELECT * FROM validate_access_code('wrongcode');

-- ==========================================
-- Verification: Confirm codes are now hidden
-- ==========================================
-- This should now FAIL with permission denied:
-- SELECT * FROM access_codes;
