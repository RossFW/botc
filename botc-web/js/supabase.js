/**
 * Database connection module for Blood on the Clocktower stats
 *
 * This module provides a unified interface for data access.
 * Currently supports:
 * - Local JSON files (for development/testing)
 * - Supabase (for production with live data entry)
 *
 * To switch to Supabase:
 * 1. Create a project at supabase.com
 * 2. Run the SQL schema below in your Supabase SQL editor
 * 3. Update SUPABASE_URL and SUPABASE_ANON_KEY
 * 4. Set USE_SUPABASE = true
 */

// ==========================================
// CONFIGURATION - Update these for Supabase
// ==========================================
const USE_SUPABASE = true;  // Supabase is now configured!
const SUPABASE_URL = 'https://mfwigdvxwpdemmwwskyk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1md2lnZHZ4d3BkZW1td3dza3lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk4NzY3NzMsImV4cCI6MjA4NTQ1Mjc3M30.KKAP1Tovgykk6iM6QHy_0-JHCik2Tp_6ja1T00shIDs';  // Get from: Supabase Dashboard > Settings > API > "anon public"

// Local JSON path - used as fallback or for testing
// Detect if we're on GitHub Pages or local
const isGitHubPages = window.location.hostname.includes('github.io');
const LOCAL_GAMELOG_PATH = isGitHubPages ? '/botc/gamelog.json' : '../gamelog.json';

// ==========================================
// SUPABASE SQL SCHEMA
// ==========================================
/*
-- Run this in your Supabase SQL Editor to set up the database:

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    game_id INTEGER UNIQUE NOT NULL,
    date TIMESTAMPTZ DEFAULT NOW(),
    players JSONB NOT NULL,
    winning_team TEXT NOT NULL CHECK (winning_team IN ('Good', 'Evil')),
    game_mode TEXT,
    story_teller TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE access_codes (
    code TEXT PRIMARY KEY,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert your confirmation code (change 'your-secret-code' to your actual code)
INSERT INTO access_codes (code, description) VALUES ('your-secret-code', 'Friends access');

-- Enable Row Level Security
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE access_codes ENABLE ROW LEVEL SECURITY;

-- Allow anyone to read games
CREATE POLICY "Games are viewable by everyone" ON games
    FOR SELECT USING (true);

-- Allow inserts (validation happens in JavaScript)
CREATE POLICY "Games can be inserted" ON games
    FOR INSERT WITH CHECK (true);

-- Allow reading access codes for validation
CREATE POLICY "Access codes can be read for validation" ON access_codes
    FOR SELECT USING (true);

-- Create index for faster queries
CREATE INDEX idx_games_game_id ON games(game_id);
*/

// ==========================================
// SUPABASE CLIENT
// ==========================================
let supabase = null;

async function initSupabase() {
    if (!USE_SUPABASE) return null;

    // Dynamically import Supabase client from CDN
    const { createClient } = await import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm');
    supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    return supabase;
}

// ==========================================
// DATA ACCESS FUNCTIONS
// ==========================================

/**
 * Fetch all games from the database.
 * @returns {Promise<Array>} Array of game objects
 */
export async function fetchGames() {
    if (USE_SUPABASE) {
        await initSupabase();
        const { data, error } = await supabase
            .from('games')
            .select('*')
            .order('game_id', { ascending: true });

        if (error) {
            console.error('Error fetching games:', error);
            throw error;
        }

        // Convert Supabase format to match gamelog.json format
        return data.map(game => ({
            game_id: game.game_id,
            date: game.date,
            players: game.players,
            winning_team: game.winning_team,
            game_mode: game.game_mode,
            story_teller: game.story_teller
        }));
    } else {
        // Fetch from local JSON file
        const response = await fetch(LOCAL_GAMELOG_PATH);
        if (!response.ok) {
            throw new Error(`Failed to fetch gamelog.json: ${response.status}`);
        }
        return await response.json();
    }
}

/**
 * Validate an access code.
 * @param {string} code - The confirmation code to validate
 * @returns {Promise<boolean>} True if code is valid
 */
export async function validateAccessCode(code) {
    if (USE_SUPABASE) {
        await initSupabase();
        const { data, error } = await supabase
            .from('access_codes')
            .select('code')
            .eq('code', code)
            .single();

        return !error && data !== null;
    } else {
        // For local testing, accept a hardcoded test code
        // In production, this should always use Supabase
        return code === 'test123';
    }
}

/**
 * Submit a new game.
 * @param {Object} gameData - The game data to submit
 * @param {string} code - The confirmation code
 * @returns {Promise<Object>} The inserted game record
 */
export async function submitGame(gameData, code) {
    // Validate code first
    const isValid = await validateAccessCode(code);
    if (!isValid) {
        throw new Error('Invalid confirmation code');
    }

    if (USE_SUPABASE) {
        await initSupabase();

        // Get the next game_id
        const { data: maxGame } = await supabase
            .from('games')
            .select('game_id')
            .order('game_id', { ascending: false })
            .limit(1);

        const nextId = (maxGame && maxGame.length > 0) ? maxGame[0].game_id + 1 : 1;

        // Insert the new game
        const { data, error } = await supabase
            .from('games')
            .insert({
                game_id: nextId,
                date: new Date().toISOString(),
                players: gameData.players,
                winning_team: gameData.winning_team,
                game_mode: gameData.game_mode,
                story_teller: gameData.story_teller
            })
            .select()
            .single();

        if (error) {
            console.error('Error submitting game:', error);
            throw error;
        }

        return data;
    } else {
        // For local testing, just return a mock response
        console.log('Local mode: Game would be submitted:', gameData);
        throw new Error('Game submission requires Supabase. Enable Supabase in supabase.js');
    }
}

/**
 * Check if we're using Supabase or local data.
 * @returns {boolean} True if using Supabase
 */
export function isUsingSupabase() {
    return USE_SUPABASE;
}

/**
 * Get the stored confirmation code from localStorage.
 * @returns {string|null} The stored code or null
 */
export function getStoredCode() {
    return localStorage.getItem('botc_access_code');
}

/**
 * Store a confirmation code in localStorage.
 * @param {string} code - The code to store
 */
export function storeCode(code) {
    localStorage.setItem('botc_access_code', code);
}

/**
 * Clear the stored confirmation code.
 */
export function clearStoredCode() {
    localStorage.removeItem('botc_access_code');
    localStorage.removeItem('botc_permission_level');
}

/**
 * Get stored permission level.
 * @returns {string|null} 'submit', 'edit', or null
 */
export function getStoredPermissionLevel() {
    return localStorage.getItem('botc_permission_level');
}

/**
 * Store permission level in localStorage.
 * @param {string} level - 'submit' or 'edit'
 */
export function storePermissionLevel(level) {
    localStorage.setItem('botc_permission_level', level);
}

// ==========================================
// PHASE 4B: GAME EDITING FUNCTIONS
// ==========================================

/**
 * Validate access code and return permission level.
 * @param {string} code - The confirmation code to validate
 * @returns {Promise<string|null>} 'submit', 'edit', or null if invalid
 */
export async function validateAccessCodeWithLevel(code) {
    if (USE_SUPABASE) {
        await initSupabase();
        const { data, error } = await supabase
            .from('access_codes')
            .select('code, permission_level')
            .eq('code', code)
            .single();

        if (error || !data) return null;
        return data.permission_level || 'submit';
    } else {
        // For local testing
        if (code === 'test123') return 'submit';
        if (code === 'edit123') return 'edit';
        return null;
    }
}

/**
 * Search games by game ID, storyteller, or script.
 * @param {string} query - Search query
 * @returns {Promise<Array>} Array of matching games (summary only)
 */
export async function searchGames(query) {
    if (!USE_SUPABASE) {
        throw new Error('Search requires Supabase');
    }

    await initSupabase();

    const trimmedQuery = query.trim();
    const gameIdNum = parseInt(trimmedQuery);

    // Build search - try game_id first if it's a number
    let searchQuery = supabase
        .from('games')
        .select('game_id, date, game_mode, story_teller, winning_team')
        .order('game_id', { ascending: false })
        .limit(20);

    if (!isNaN(gameIdNum) && trimmedQuery === String(gameIdNum)) {
        // Search by game ID
        searchQuery = searchQuery.eq('game_id', gameIdNum);
    } else {
        // Search by storyteller or script name
        searchQuery = searchQuery.or(`story_teller.ilike.%${trimmedQuery}%,game_mode.ilike.%${trimmedQuery}%`);
    }

    const { data, error } = await searchQuery;

    if (error) {
        console.error('Error searching games:', error);
        throw error;
    }

    return data || [];
}

/**
 * Get full game data by game_id.
 * @param {number} gameId - The game ID
 * @returns {Promise<Object>} Full game object
 */
export async function getGameById(gameId) {
    if (!USE_SUPABASE) {
        throw new Error('Requires Supabase');
    }

    await initSupabase();
    const { data, error } = await supabase
        .from('games')
        .select('*')
        .eq('game_id', gameId)
        .single();

    if (error) {
        console.error('Error fetching game:', error);
        throw error;
    }

    return data;
}

/**
 * Update an existing game.
 * @param {number} gameId - The game ID to update
 * @param {Object} gameData - Updated game data
 * @param {string} code - The edit confirmation code
 * @returns {Promise<Object>} The updated game record
 */
export async function updateGame(gameId, gameData, code) {
    // Validate code has edit permission
    const level = await validateAccessCodeWithLevel(code);
    if (level !== 'edit') {
        throw new Error('Edit access required. Use the edit code.');
    }

    if (!USE_SUPABASE) {
        throw new Error('Update requires Supabase');
    }

    await initSupabase();
    const { data, error } = await supabase
        .from('games')
        .update({
            players: gameData.players,
            winning_team: gameData.winning_team,
            game_mode: gameData.game_mode,
            story_teller: gameData.story_teller
        })
        .eq('game_id', gameId)
        .select()
        .single();

    if (error) {
        console.error('Error updating game:', error);
        throw error;
    }

    return data;
}

// ==========================================
// PHASE 4C: SCRIPTS MANAGEMENT FUNCTIONS
// ==========================================

/**
 * Fetch all scripts from the database.
 * @returns {Promise<Array>} Array of script objects
 */
export async function fetchScripts() {
    if (!USE_SUPABASE) {
        // Return hardcoded list for local testing
        return [
            { name: 'Trouble Brewing', category: 'Normal' },
            { name: 'Bad Moon Rising', category: 'Normal' },
            { name: 'Sects & Violets', category: 'Normal' }
        ];
    }

    await initSupabase();
    const { data, error } = await supabase
        .from('scripts')
        .select('*')
        .order('name', { ascending: true });

    if (error) {
        console.error('Error fetching scripts:', error);
        // Return empty array if scripts table doesn't exist yet
        return [];
    }

    return data || [];
}

/**
 * Add a new script to the database.
 * @param {Object} scriptData - { name, category }
 * @param {string} code - The edit confirmation code
 * @returns {Promise<Object>} The inserted script
 */
export async function addScript(scriptData, code) {
    // Validate code has edit permission
    const level = await validateAccessCodeWithLevel(code);
    if (level !== 'edit') {
        throw new Error('Edit access required to add scripts');
    }

    if (!USE_SUPABASE) {
        throw new Error('Adding scripts requires Supabase');
    }

    await initSupabase();
    const { data, error } = await supabase
        .from('scripts')
        .insert({
            name: scriptData.name,
            category: scriptData.category
        })
        .select()
        .single();

    if (error) {
        console.error('Error adding script:', error);
        throw error;
    }

    return data;
}
