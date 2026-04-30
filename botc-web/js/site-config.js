/**
 * Site Configuration
 *
 * This is the ONLY file you need to edit to set up your community's site.
 * Everything else works out of the box.
 */

const SITE_CONFIG = {
    // ==========================================
    // REQUIRED: Supabase Connection
    // ==========================================
    // Get these from: Supabase Dashboard > Settings > API
    // Leave as-is to use demo mode with sample data.

    supabaseUrl: 'https://mfwigdvxwpdemmwwskyk.supabase.co',
    supabaseAnonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1md2lnZHZ4d3BkZW1td3dza3lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk4NzY3NzMsImV4cCI6MjA4NTQ1Mjc3M30.KKAP1Tovgykk6iM6QHy_0-JHCik2Tp_6ja1T00shIDs',

    // ==========================================
    // OPTIONAL: Customize Your Site
    // ==========================================

    // Community name shown in the header
    communityName: 'Blood on the Clocktower',

    // Minimum games a player needs to appear on the leaderboard
    minGamesForLeaderboard: 5,

    // ELO settings
    defaultRating: 1500,    // Starting ELO for new players
    kFactor: 32,            // How much each game affects ratings (higher = more volatile)

    // ==========================================
    // OPTIONAL: Player Privacy
    // ==========================================
    // Players listed here have their stats hidden in the UI but their games
    // STILL count toward ELO calculations (so opponents' stats remain accurate).
    //
    // Player names should match how they're stored in Supabase (underscores for spaces).
    //
    //   hideLeaderboard: true  → name doesn't appear on leaderboard, ranks adjust
    //   hideAnalytics: true    → name removed from Player tab, H2H, "Played By", etc.
    //
    // Example:
    //   playerPrivacy: {
    //       'Some_Player': { hideLeaderboard: true, hideAnalytics: true },
    //   },
    playerPrivacy: {
        'Kat_Minor': { hideLeaderboard: true, hideAnalytics: true },
    },
};

// Export for use in other modules
// (Do not modify below this line)
export default SITE_CONFIG;
