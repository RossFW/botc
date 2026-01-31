/**
 * Analytics Application - Main entry point for the analytics dashboard.
 */

import { fetchGames } from './supabase.js';
import {
    StorytellerAnalytics,
    extractStorytellers,
    categorizeScript,
    getCharacterRoleType,
    analyzeHeadToHead
} from './analytics.js';

// ==========================================
// STATE
// ==========================================

let allGames = [];
let currentAnalytics = null;
let currentSortColumn = {};
let currentSortAscending = {};

// ==========================================
// INITIALIZATION
// ==========================================

document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadData();
        setupEventListeners();
        showContent();
    } catch (error) {
        console.error('Failed to initialize analytics:', error);
        showError();
    }
});

/**
 * Load game data from Supabase.
 */
async function loadData() {
    allGames = await fetchGames();

    // Initialize analytics with all games
    currentAnalytics = new StorytellerAnalytics(allGames, 'All');

    // Populate storyteller dropdown
    populateStorytellerDropdown();

    // Populate player dropdowns
    populatePlayerDropdowns();

    // Populate script filter dropdown
    populateScriptFilterDropdown();

    // Update all displays
    updateSummary();
    updateScriptsTab();
    updateCharactersTab();
}

/**
 * Set up event listeners.
 */
function setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Storyteller filter
    document.getElementById('storyteller-filter').addEventListener('change', onStorytellerChange);

    // Character filters
    document.getElementById('script-filter').addEventListener('change', updateCharactersTab);
    document.getElementById('role-type-filter').addEventListener('change', updateCharactersTab);

    // Player selection
    document.getElementById('player-select').addEventListener('change', updatePlayerTab);

    // Head-to-head analyze button
    document.getElementById('h2h-analyze-btn').addEventListener('click', analyzeH2H);

    // Table sorting
    document.querySelectorAll('.analytics-table th[data-sort]').forEach(th => {
        th.addEventListener('click', () => handleSort(th));
    });
}

/**
 * Show main content and hide loading.
 */
function showContent() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('content').style.display = 'block';
}

/**
 * Show error state.
 */
function showError() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'block';
}

// ==========================================
// TAB MANAGEMENT
// ==========================================

/**
 * Switch to a different tab.
 * @param {string} tabId - Tab ID to switch to
 */
function switchTab(tabId) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabId}-tab`);
    });
}

// ==========================================
// DROPDOWN POPULATION
// ==========================================

/**
 * Populate the storyteller dropdown.
 */
function populateStorytellerDropdown() {
    const select = document.getElementById('storyteller-filter');
    const storytellers = extractStorytellers(allGames);

    // Keep "All Games" option, add storytellers
    storytellers.forEach(st => {
        const option = document.createElement('option');
        option.value = st;
        option.textContent = st.replace(/_/g, ' ');
        select.appendChild(option);
    });
}

/**
 * Populate player dropdowns (player tab and H2H).
 */
function populatePlayerDropdowns() {
    const playerNames = currentAnalytics.getPlayerNames();

    // Player tab dropdown
    const playerSelect = document.getElementById('player-select');
    playerNames.forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name.replace(/_/g, ' ');
        playerSelect.appendChild(option);
    });

    // H2H dropdowns
    const h2hPlayer1 = document.getElementById('h2h-player1');
    const h2hPlayer2 = document.getElementById('h2h-player2');

    playerNames.forEach(name => {
        const opt1 = document.createElement('option');
        opt1.value = name;
        opt1.textContent = name.replace(/_/g, ' ');
        h2hPlayer1.appendChild(opt1);

        const opt2 = document.createElement('option');
        opt2.value = name;
        opt2.textContent = name.replace(/_/g, ' ');
        h2hPlayer2.appendChild(opt2);
    });
}

/**
 * Populate the script filter dropdown in characters tab.
 */
function populateScriptFilterDropdown() {
    const select = document.getElementById('script-filter');
    const scripts = Object.keys(currentAnalytics.scriptStats).sort((a, b) =>
        a.toLowerCase().localeCompare(b.toLowerCase())
    );

    scripts.forEach(script => {
        const option = document.createElement('option');
        option.value = script;
        option.textContent = script || '(Unknown)';
        select.appendChild(option);
    });
}

// ==========================================
// STORYTELLER CHANGE
// ==========================================

/**
 * Handle storyteller filter change.
 */
function onStorytellerChange() {
    const storyteller = document.getElementById('storyteller-filter').value;
    currentAnalytics = new StorytellerAnalytics(allGames, storyteller);

    // Update all displays
    updateSummary();
    updateScriptsTab();
    updateCharactersTab();

    // Reset player tab
    document.getElementById('player-select').value = '';
    document.getElementById('player-stats-container').style.display = 'none';

    // Repopulate player dropdowns for filtered analytics
    repopulatePlayerDropdowns();
}

/**
 * Repopulate player dropdowns after storyteller change.
 */
function repopulatePlayerDropdowns() {
    const playerNames = currentAnalytics.getPlayerNames();

    // Clear and repopulate player select
    const playerSelect = document.getElementById('player-select');
    playerSelect.innerHTML = '<option value="">-- Choose a player --</option>';
    playerNames.forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name.replace(/_/g, ' ');
        playerSelect.appendChild(option);
    });

    // Clear and repopulate H2H dropdowns
    const h2hPlayer1 = document.getElementById('h2h-player1');
    const h2hPlayer2 = document.getElementById('h2h-player2');

    h2hPlayer1.innerHTML = '<option value="">-- Select player --</option>';
    h2hPlayer2.innerHTML = '<option value="">-- Select player --</option>';

    playerNames.forEach(name => {
        const opt1 = document.createElement('option');
        opt1.value = name;
        opt1.textContent = name.replace(/_/g, ' ');
        h2hPlayer1.appendChild(opt1);

        const opt2 = document.createElement('option');
        opt2.value = name;
        opt2.textContent = name.replace(/_/g, ' ');
        h2hPlayer2.appendChild(opt2);
    });
}

// ==========================================
// SUMMARY UPDATE
// ==========================================

/**
 * Update the summary statistics display.
 */
function updateSummary() {
    const summary = currentAnalytics.getSummary();

    document.getElementById('summary-games').textContent = `${summary.totalGames} games`;
    document.getElementById('summary-good').textContent = `Good: ${summary.goodPct}%`;
    document.getElementById('summary-evil').textContent = `Evil: ${summary.evilPct}%`;
}

// ==========================================
// SCRIPTS TAB
// ==========================================

/**
 * Update the scripts tab table.
 */
function updateScriptsTab() {
    const tbody = document.getElementById('scripts-body');
    tbody.innerHTML = '';

    const sortCol = currentSortColumn['scripts'] || 'good_pct';
    const sortAsc = currentSortAscending['scripts'] || false;

    const entries = currentAnalytics.getScriptStatsArray(sortCol, sortAsc);

    // Add script rows
    for (const [script, stats] of entries) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${script || '(Unknown)'}</td>
            <td><span class="category-badge ${stats.category.toLowerCase()}">${stats.category}</span></td>
            <td class="good-text">${stats.good_pct.toFixed(1)}%</td>
            <td class="evil-text">${stats.evil_pct.toFixed(1)}%</td>
            <td>${stats.good_wins}</td>
            <td>${stats.evil_wins}</td>
            <td>${stats.games}</td>
        `;
        tbody.appendChild(row);
    }

    // Add separator
    const sepRow = document.createElement('tr');
    sepRow.className = 'separator-row';
    sepRow.innerHTML = '<td colspan="7"></td>';
    tbody.appendChild(sepRow);

    // Add category totals
    for (const [cat, totals] of Object.entries(currentAnalytics.categoryTotals)) {
        if (totals.games === 0) continue;

        const goodPct = (totals.good_wins / totals.games * 100).toFixed(1);
        const evilPct = (totals.evil_wins / totals.games * 100).toFixed(1);

        const row = document.createElement('tr');
        row.className = 'total-row';
        row.innerHTML = `
            <td><strong>${cat} Total</strong></td>
            <td><span class="category-badge ${cat.toLowerCase()}">${cat}</span></td>
            <td class="good-text"><strong>${goodPct}%</strong></td>
            <td class="evil-text"><strong>${evilPct}%</strong></td>
            <td><strong>${totals.good_wins}</strong></td>
            <td><strong>${totals.evil_wins}</strong></td>
            <td><strong>${totals.games}</strong></td>
        `;
        tbody.appendChild(row);
    }
}

// ==========================================
// CHARACTERS TAB
// ==========================================

/**
 * Update the characters tab table.
 */
function updateCharactersTab() {
    const tbody = document.getElementById('characters-body');
    tbody.innerHTML = '';

    const scriptFilter = document.getElementById('script-filter').value;
    const roleTypeFilter = document.getElementById('role-type-filter').value;

    const characters = currentAnalytics.getCharacterStats(scriptFilter, roleTypeFilter);

    for (const char of characters) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${char.character}</td>
            <td><span class="role-type-badge ${char.role_type.toLowerCase()}">${char.role_type}</span></td>
            <td>${char.win_pct.toFixed(1)}%</td>
            <td>${char.wins}</td>
            <td>${char.games}</td>
        `;
        tbody.appendChild(row);
    }
}

// ==========================================
// PLAYERS TAB
// ==========================================

/**
 * Update the player tab with selected player's stats.
 */
function updatePlayerTab() {
    const playerName = document.getElementById('player-select').value;
    const container = document.getElementById('player-stats-container');

    if (!playerName) {
        container.style.display = 'none';
        return;
    }

    const stats = currentAnalytics.getPlayerStats(playerName);
    if (!stats) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'block';

    // Update summary cards
    const winPct = stats.games > 0 ? (stats.wins / stats.games * 100).toFixed(1) : '0.0';
    const goodPct = stats.good_games > 0 ? (stats.good_wins / stats.good_games * 100).toFixed(1) : '0.0';
    const evilPct = stats.evil_games > 0 ? (stats.evil_wins / stats.evil_games * 100).toFixed(1) : '0.0';

    document.getElementById('player-win-pct').textContent = `${winPct}%`;
    document.getElementById('player-good-pct').textContent = `${goodPct}%`;
    document.getElementById('player-good-games').textContent = `${stats.good_games} games`;
    document.getElementById('player-evil-pct').textContent = `${evilPct}%`;
    document.getElementById('player-evil-games').textContent = `${stats.evil_games} games`;
    document.getElementById('player-total-games').textContent = stats.games;

    // Update per-script breakdown
    updatePlayerScriptsTable(stats);

    // Update role history
    updatePlayerRolesTable(stats);
}

/**
 * Update the per-script table for a player.
 * @param {Object} stats - Player stats object
 */
function updatePlayerScriptsTable(stats) {
    const tbody = document.getElementById('player-scripts-body');
    tbody.innerHTML = '';

    // Add "All" row first
    const allWinPct = stats.games > 0 ? (stats.wins / stats.games * 100).toFixed(1) : '0.0';
    const allGoodPct = stats.good_games > 0 ? (stats.good_wins / stats.good_games * 100).toFixed(1) : '0.0';
    const allEvilPct = stats.evil_games > 0 ? (stats.evil_wins / stats.evil_games * 100).toFixed(1) : '0.0';

    const allRow = document.createElement('tr');
    allRow.className = 'total-row';
    allRow.innerHTML = `
        <td><strong>All</strong></td>
        <td><strong>${allWinPct}%</strong></td>
        <td><strong>${stats.games}</strong></td>
        <td class="good-text"><strong>${allGoodPct}%</strong></td>
        <td><strong>${stats.good_games}</strong></td>
        <td class="evil-text"><strong>${allEvilPct}%</strong></td>
        <td><strong>${stats.evil_games}</strong></td>
    `;
    tbody.appendChild(allRow);

    // Sort scripts by win percentage
    const scriptEntries = Object.entries(stats.scripts).sort((a, b) => {
        const aPct = a[1].games > 0 ? a[1].wins / a[1].games : 0;
        const bPct = b[1].games > 0 ? b[1].wins / b[1].games : 0;
        return bPct - aPct;
    });

    for (const [script, s] of scriptEntries) {
        const winPct = s.games > 0 ? (s.wins / s.games * 100).toFixed(1) : '0.0';
        const goodPct = s.good_games > 0 ? (s.good_wins / s.good_games * 100).toFixed(1) : '0.0';
        const evilPct = s.evil_games > 0 ? (s.evil_wins / s.evil_games * 100).toFixed(1) : '0.0';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${script || '(Unknown)'}</td>
            <td>${winPct}%</td>
            <td>${s.games}</td>
            <td class="good-text">${goodPct}%</td>
            <td>${s.good_games}</td>
            <td class="evil-text">${evilPct}%</td>
            <td>${s.evil_games}</td>
        `;
        tbody.appendChild(row);
    }
}

/**
 * Update the role history table for a player.
 * @param {Object} stats - Player stats object
 */
function updatePlayerRolesTable(stats) {
    const tbody = document.getElementById('player-roles-body');
    tbody.innerHTML = '';

    // Sort roles by games played
    const roleEntries = Object.entries(stats.roles).sort((a, b) => b[1].games - a[1].games);

    for (const [role, r] of roleEntries) {
        const winPct = r.games > 0 ? (r.wins / r.games * 100).toFixed(1) : '0.0';
        const roleType = getCharacterRoleType(role);

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${role}</td>
            <td><span class="role-type-badge ${roleType.toLowerCase()}">${roleType}</span></td>
            <td>${winPct}%</td>
            <td>${r.wins}</td>
            <td>${r.games}</td>
        `;
        tbody.appendChild(row);
    }
}

// ==========================================
// HEAD-TO-HEAD TAB
// ==========================================

/**
 * Analyze head-to-head matchup between two players.
 */
function analyzeH2H() {
    const player1 = document.getElementById('h2h-player1').value;
    const player2 = document.getElementById('h2h-player2').value;

    const resultsDiv = document.getElementById('h2h-results');
    const noResultsDiv = document.getElementById('h2h-no-results');

    if (!player1 || !player2) {
        alert('Please select both players.');
        return;
    }

    if (player1 === player2) {
        alert('Please select two different players.');
        return;
    }

    // Use filtered games from current analytics
    const results = analyzeHeadToHead(currentAnalytics.games, player1, player2);

    // Update display
    document.getElementById('h2h-player1-name').textContent = player1.replace(/_/g, ' ');
    document.getElementById('h2h-player2-name').textContent = player2.replace(/_/g, ' ');
    document.getElementById('h2h-total-games').textContent = results.total_together;

    // Same team stats
    document.getElementById('same-team-games').textContent = results.same_team.games;
    document.getElementById('same-team-wins').textContent = results.same_team.wins;
    document.getElementById('same-team-pct').textContent = results.same_team.win_pct;

    document.getElementById('both-good-games').textContent = results.same_team.both_good.games;
    document.getElementById('both-good-wins').textContent = results.same_team.both_good.wins;
    document.getElementById('both-good-pct').textContent = results.same_team.both_good.win_pct;

    document.getElementById('both-evil-games').textContent = results.same_team.both_evil.games;
    document.getElementById('both-evil-wins').textContent = results.same_team.both_evil.wins;
    document.getElementById('both-evil-pct').textContent = results.same_team.both_evil.win_pct;

    // Opposite teams stats
    document.getElementById('opp-total-games').textContent = results.opposite_teams.games;

    document.getElementById('opp-p1-name').textContent = player1.replace(/_/g, ' ');
    document.getElementById('p1-opp-wins').textContent = results.opposite_teams[player1].wins;
    document.getElementById('p1-opp-pct').textContent = results.opposite_teams[player1].win_pct;
    document.getElementById('p1-good-games').textContent = results.opposite_teams[player1].when_good.games;
    document.getElementById('p1-good-wins').textContent = results.opposite_teams[player1].when_good.wins;
    document.getElementById('p1-good-pct').textContent = results.opposite_teams[player1].when_good.win_pct;
    document.getElementById('p1-evil-games').textContent = results.opposite_teams[player1].when_evil.games;
    document.getElementById('p1-evil-wins').textContent = results.opposite_teams[player1].when_evil.wins;
    document.getElementById('p1-evil-pct').textContent = results.opposite_teams[player1].when_evil.win_pct;

    document.getElementById('opp-p2-name').textContent = player2.replace(/_/g, ' ');
    document.getElementById('p2-opp-wins').textContent = results.opposite_teams[player2].wins;
    document.getElementById('p2-opp-pct').textContent = results.opposite_teams[player2].win_pct;
    document.getElementById('p2-good-games').textContent = results.opposite_teams[player2].when_good.games;
    document.getElementById('p2-good-wins').textContent = results.opposite_teams[player2].when_good.wins;
    document.getElementById('p2-good-pct').textContent = results.opposite_teams[player2].when_good.win_pct;
    document.getElementById('p2-evil-games').textContent = results.opposite_teams[player2].when_evil.games;
    document.getElementById('p2-evil-wins').textContent = results.opposite_teams[player2].when_evil.wins;
    document.getElementById('p2-evil-pct').textContent = results.opposite_teams[player2].when_evil.win_pct;

    // Game IDs
    document.getElementById('h2h-game-ids-list').textContent = results.game_ids.length > 0
        ? results.game_ids.join(', ')
        : '-';

    // Show results
    resultsDiv.style.display = 'block';
    noResultsDiv.style.display = 'none';
}

// ==========================================
// TABLE SORTING
// ==========================================

/**
 * Handle table header click for sorting.
 * @param {HTMLElement} th - Table header element
 */
function handleSort(th) {
    const table = th.closest('table');
    const tableId = table.id;
    const sortKey = th.dataset.sort;

    // Toggle sort direction
    if (currentSortColumn[tableId] === sortKey) {
        currentSortAscending[tableId] = !currentSortAscending[tableId];
    } else {
        currentSortColumn[tableId] = sortKey;
        currentSortAscending[tableId] = false; // Default to descending
    }

    // Update visual indicators
    table.querySelectorAll('th').forEach(header => {
        header.classList.remove('sorted-asc', 'sorted-desc');
    });
    th.classList.add(currentSortAscending[tableId] ? 'sorted-asc' : 'sorted-desc');

    // Re-render appropriate tab
    if (tableId === 'scripts-table') {
        updateScriptsTab();
    } else if (tableId === 'characters-table') {
        sortCharactersTable(sortKey, currentSortAscending[tableId]);
    } else if (tableId === 'player-scripts-table' || tableId === 'player-roles-table') {
        sortGenericTable(table, sortKey, currentSortAscending[tableId]);
    }
}

/**
 * Sort the characters table.
 * @param {string} sortKey - Column to sort by
 * @param {boolean} ascending - Sort direction
 */
function sortCharactersTable(sortKey, ascending) {
    const tbody = document.getElementById('characters-body');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    const colIndex = {
        'character': 0,
        'role_type': 1,
        'win_pct': 2,
        'wins': 3,
        'games': 4
    }[sortKey];

    rows.sort((a, b) => {
        let aVal = a.cells[colIndex].textContent.trim();
        let bVal = b.cells[colIndex].textContent.trim();

        // Handle percentage values
        if (aVal.endsWith('%')) aVal = parseFloat(aVal);
        if (bVal.endsWith('%')) bVal = parseFloat(bVal);

        // Handle numeric values
        if (!isNaN(aVal) && !isNaN(bVal)) {
            aVal = parseFloat(aVal);
            bVal = parseFloat(bVal);
        }

        if (ascending) {
            return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        } else {
            return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
        }
    });

    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Sort a generic table.
 * @param {HTMLElement} table - Table element
 * @param {string} sortKey - Column to sort by
 * @param {boolean} ascending - Sort direction
 */
function sortGenericTable(table, sortKey, ascending) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr:not(.total-row)'));
    const totalRows = Array.from(tbody.querySelectorAll('tr.total-row'));

    const headers = Array.from(table.querySelectorAll('th[data-sort]'));
    const colIndex = headers.findIndex(h => h.dataset.sort === sortKey);

    if (colIndex === -1) return;

    rows.sort((a, b) => {
        let aVal = a.cells[colIndex].textContent.trim();
        let bVal = b.cells[colIndex].textContent.trim();

        // Handle percentage values
        if (aVal.endsWith('%')) aVal = parseFloat(aVal);
        if (bVal.endsWith('%')) bVal = parseFloat(bVal);

        // Handle numeric values
        if (!isNaN(aVal) && !isNaN(bVal)) {
            aVal = parseFloat(aVal);
            bVal = parseFloat(bVal);
        }

        if (ascending) {
            return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        } else {
            return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
        }
    });

    // Clear and re-append: total rows first, then sorted rows
    tbody.innerHTML = '';
    totalRows.forEach(row => tbody.appendChild(row));
    rows.forEach(row => tbody.appendChild(row));
}
