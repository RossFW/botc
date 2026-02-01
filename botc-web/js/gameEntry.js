/**
 * Game Entry Module for Blood on the Clocktower Stats
 * Handles the game submission form and Supabase integration
 */

import {
    validateAccessCode,
    validateAccessCodeWithLevel,
    submitGame,
    updateGame,
    getStoredCode,
    storeCode,
    getStoredPermissionLevel,
    storePermissionLevel,
    searchGames as searchGamesApi,
    getGameById,
    fetchScripts
} from './supabase.js';

// Cache for scripts
let scriptsCache = null;

// DOM Elements - Game Entry Modal
let modal, codeStep, formStep, codeInput, verifyBtn, codeError;
let team1Input, team2Input, evilTeamRadios, winnerRadios;
let scriptSelect, storytellerInput, submitBtn, submitError, submitSuccess;
let formTitle, formSubtitle;

// DOM Elements - Game Search Modal
let searchModal, editCodeStep, searchStep, editCodeInput, verifyEditCodeBtn, editCodeError;
let gameSearchInput, searchGamesBtn, searchResults;

// Edit mode state
let editMode = false;
let currentEditGameId = null;

/**
 * Initialize the game entry module
 */
export function initGameEntry(onGameAdded) {
    // Get DOM elements
    modal = document.getElementById('game-entry-modal');
    codeStep = document.getElementById('code-step');
    formStep = document.getElementById('form-step');
    codeInput = document.getElementById('confirmation-code');
    verifyBtn = document.getElementById('verify-code-btn');
    codeError = document.getElementById('code-error');

    team1Input = document.getElementById('team1-input');
    team2Input = document.getElementById('team2-input');
    evilTeamRadios = document.querySelectorAll('input[name="evil-team"]');
    winnerRadios = document.querySelectorAll('input[name="winner"]');
    scriptSelect = document.getElementById('script-select');
    storytellerInput = document.getElementById('storyteller-input');
    submitBtn = document.getElementById('submit-game-btn');
    submitError = document.getElementById('submit-error');
    submitSuccess = document.getElementById('submit-success');
    formTitle = document.getElementById('form-title');
    formSubtitle = document.getElementById('form-subtitle');

    // Game Search Modal elements
    searchModal = document.getElementById('game-search-modal');
    editCodeStep = document.getElementById('edit-code-step');
    searchStep = document.getElementById('search-step');
    editCodeInput = document.getElementById('edit-confirmation-code');
    verifyEditCodeBtn = document.getElementById('verify-edit-code-btn');
    editCodeError = document.getElementById('edit-code-error');
    gameSearchInput = document.getElementById('game-search-input');
    searchGamesBtn = document.getElementById('search-games-btn');
    searchResults = document.getElementById('search-results');

    // Store callback
    window._onGameAdded = onGameAdded;

    // Set up event listeners
    setupEventListeners();

    // Check for stored code
    checkStoredCode();

    // Load scripts from database
    loadScripts();
}

/**
 * Load scripts from the database and populate the dropdown
 */
async function loadScripts() {
    try {
        const scripts = await fetchScripts();
        if (scripts && scripts.length > 0) {
            scriptsCache = scripts;

            // Clear existing options and populate with database scripts
            scriptSelect.innerHTML = '';
            scripts.forEach(script => {
                const option = document.createElement('option');
                option.value = script.name;
                option.textContent = script.name;
                scriptSelect.appendChild(option);
            });
        }
        // If no scripts from database, keep the hardcoded options
    } catch (error) {
        console.warn('Could not load scripts from database, using defaults:', error);
        // Keep hardcoded options as fallback
    }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Add Game button
    const addGameBtn = document.getElementById('add-game-btn');
    if (addGameBtn) {
        addGameBtn.addEventListener('click', openModal);
    }

    // Modal close button
    const closeBtn = modal.querySelector('.modal-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    // Click outside modal to close
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // ESC key to close modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (searchModal && searchModal.classList.contains('active')) {
                closeSearchModal();
            } else if (modal.classList.contains('active')) {
                closeModal();
            }
        }
    });

    // Verify code button
    verifyBtn.addEventListener('click', verifyCode);

    // Enter key on code input
    codeInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            verifyCode();
        }
    });

    // Submit game button
    submitBtn.addEventListener('click', submitGameForm);

    // Help toggle button
    const helpToggleBtn = document.getElementById('help-toggle-btn');
    const helpContent = document.getElementById('help-content');
    if (helpToggleBtn && helpContent) {
        helpToggleBtn.addEventListener('click', () => {
            helpToggleBtn.classList.toggle('active');
            helpContent.classList.toggle('show');
        });
    }

    // Edit Game button
    const editGameBtn = document.getElementById('edit-game-btn');
    if (editGameBtn) {
        editGameBtn.addEventListener('click', openSearchModal);
    }

    // Search modal close button
    if (searchModal) {
        const searchCloseBtn = searchModal.querySelector('.modal-close');
        if (searchCloseBtn) {
            searchCloseBtn.addEventListener('click', closeSearchModal);
        }

        // Click outside to close
        searchModal.addEventListener('click', (e) => {
            if (e.target === searchModal) {
                closeSearchModal();
            }
        });
    }

    // Verify edit code button
    if (verifyEditCodeBtn) {
        verifyEditCodeBtn.addEventListener('click', verifyEditCode);
    }

    // Enter key on edit code input
    if (editCodeInput) {
        editCodeInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                verifyEditCode();
            }
        });
    }

    // Search games button
    if (searchGamesBtn) {
        searchGamesBtn.addEventListener('click', performGameSearch);
    }

    // Enter key on search input
    if (gameSearchInput) {
        gameSearchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                performGameSearch();
            }
        });
    }
}

/**
 * Check if user has a stored code and auto-verify
 */
async function checkStoredCode() {
    const storedCode = getStoredCode();
    if (storedCode) {
        const isValid = await validateAccessCode(storedCode);
        if (isValid) {
            showFormStep();
        }
    }
}

/**
 * Open the game entry modal (for adding new games)
 */
function openModal() {
    // Reset to add mode
    resetToAddMode();

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Check if we already have a valid code
    const storedCode = getStoredCode();
    if (storedCode) {
        showFormStep();
    } else {
        showCodeStep();
    }

    // Clear any previous errors/success messages
    hideError(codeError);
    hideError(submitError);
    hideSuccess(submitSuccess);
}

/**
 * Close the game entry modal
 */
function closeModal() {
    modal.classList.remove('active');
    document.body.style.overflow = '';

    // Reset edit mode if closing
    if (editMode) {
        resetToAddMode();
    }
}

/**
 * Show the code input step
 */
function showCodeStep() {
    codeStep.style.display = 'block';
    formStep.style.display = 'none';
    codeInput.value = '';
    codeInput.focus();
}

/**
 * Show the form step
 */
function showFormStep() {
    codeStep.style.display = 'none';
    formStep.style.display = 'block';
}

/**
 * Verify the confirmation code
 */
async function verifyCode() {
    const code = codeInput.value.trim();

    if (!code) {
        showError(codeError, 'Please enter a code');
        return;
    }

    verifyBtn.disabled = true;
    verifyBtn.textContent = 'Verifying...';

    try {
        const isValid = await validateAccessCode(code);

        if (isValid) {
            storeCode(code);
            hideError(codeError);
            showFormStep();
        } else {
            showError(codeError, 'Invalid code. Please try again.');
        }
    } catch (error) {
        showError(codeError, 'Error verifying code. Please try again.');
        console.error('Code verification error:', error);
    } finally {
        verifyBtn.disabled = false;
        verifyBtn.textContent = 'Verify';
    }
}

/**
 * Parse team input text into player objects
 */
function parseTeamInput(text) {
    const lines = text.trim().split('\n');
    const players = [];

    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        const parts = trimmed.split(/\s+/);
        if (parts.length < 1) continue;

        const name = parts[0];
        const roleStr = parts[1] || '';
        const teamHint = parts[2] || null;

        // Process roles (split on +)
        const rawRoles = roleStr ? roleStr.split('+') : [''];
        const roles = rawRoles.map(r => standardizeRole(r));
        const finalRole = roles[roles.length - 1] || '';

        // Process team hint for initial team
        let initialTeam = null;
        if (teamHint) {
            if (teamHint.includes('->')) {
                initialTeam = capitalize(teamHint.split('->')[0]);
            } else {
                initialTeam = capitalize(teamHint);
            }
        }

        players.push({
            name,
            role: finalRole,
            roles,
            initial_team: initialTeam
        });
    }

    return players;
}

/**
 * Standardize a role name
 */
function standardizeRole(role) {
    if (!role) return '';
    const segments = role.split('_');
    return segments.map(seg => {
        if (!seg) return seg;
        return seg[0].toUpperCase() + seg.slice(1).toLowerCase();
    }).join('_');
}

/**
 * Capitalize first letter
 */
function capitalize(str) {
    if (!str) return str;
    return str[0].toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Submit the game form
 */
async function submitGameForm() {
    // Clear previous messages
    hideError(submitError);
    hideSuccess(submitSuccess);

    // Validate inputs
    const team1Text = team1Input.value.trim();
    const team2Text = team2Input.value.trim();

    if (!team1Text || !team2Text) {
        showError(submitError, 'Please enter players for both teams');
        return;
    }

    const evilTeam = document.querySelector('input[name="evil-team"]:checked');
    const winner = document.querySelector('input[name="winner"]:checked');

    if (!evilTeam || !winner) {
        showError(submitError, 'Please select which team is Evil and which team won');
        return;
    }

    const storyteller = storytellerInput.value.trim();
    if (!storyteller) {
        showError(submitError, 'Please enter the storyteller name');
        return;
    }

    // Parse teams
    const team1Players = parseTeamInput(team1Text);
    const team2Players = parseTeamInput(team2Text);

    if (team1Players.length === 0 || team2Players.length === 0) {
        showError(submitError, 'Please enter at least one player per team');
        return;
    }

    // Assign teams based on evil selection
    const evilTeamNum = parseInt(evilTeam.value);
    const team1Team = evilTeamNum === 1 ? 'Evil' : 'Good';
    const team2Team = evilTeamNum === 2 ? 'Evil' : 'Good';

    // Assign team and initial_team to players
    for (const p of team1Players) {
        p.team = team1Team;
        if (!p.initial_team) p.initial_team = team1Team;
    }
    for (const p of team2Players) {
        p.team = team2Team;
        if (!p.initial_team) p.initial_team = team2Team;
    }

    // Determine winning team
    const winnerNum = parseInt(winner.value);
    const winningTeam = winnerNum === 1 ? team1Team : team2Team;

    // Build game data
    const gameData = {
        players: [...team1Players, ...team2Players],
        winning_team: winningTeam,
        game_mode: scriptSelect.value,
        story_teller: storyteller
    };

    // Submit or Update
    submitBtn.disabled = true;
    submitBtn.textContent = editMode ? 'Updating...' : 'Submitting...';

    try {
        const code = getStoredCode();

        if (editMode && currentEditGameId) {
            // Update existing game
            await updateGame(currentEditGameId, gameData, code);
            showSuccess(submitSuccess, `Game #${currentEditGameId} updated successfully!`);
        } else {
            // Submit new game
            await submitGame(gameData, code);
            showSuccess(submitSuccess, 'Game submitted successfully!');
        }

        // Clear form and reset mode
        clearForm();
        resetToAddMode();

        // Refresh the leaderboard
        if (window._onGameAdded) {
            await window._onGameAdded();
        }

        // Close modal after a delay
        setTimeout(() => {
            closeModal();
            hideSuccess(submitSuccess);
        }, 1500);

    } catch (error) {
        showError(submitError, error.message || 'Failed to submit game. Please try again.');
        console.error('Submit error:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = editMode ? 'Update Game' : 'Submit Game';
    }
}

/**
 * Clear the form
 */
function clearForm() {
    team1Input.value = '';
    team2Input.value = '';
    evilTeamRadios.forEach(r => r.checked = false);
    winnerRadios.forEach(r => r.checked = false);
    scriptSelect.selectedIndex = 0;
    storytellerInput.value = '';
}

/**
 * Show error message
 */
function showError(element, message) {
    element.textContent = message;
    element.style.display = 'block';
}

/**
 * Hide error message
 */
function hideError(element) {
    element.style.display = 'none';
}

/**
 * Show success message
 */
function showSuccess(element, message) {
    element.textContent = message;
    element.style.display = 'block';
}

/**
 * Hide success message
 */
function hideSuccess(element) {
    element.style.display = 'none';
}

// ==========================================
// EDIT MODE FUNCTIONS
// ==========================================

/**
 * Open the game search modal
 */
function openSearchModal() {
    searchModal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Check if we have edit permission stored
    const level = getStoredPermissionLevel();
    if (level === 'edit') {
        showSearchStep();
    } else {
        showEditCodeStep();
    }

    // Clear any previous errors
    if (editCodeError) hideError(editCodeError);
    if (searchResults) searchResults.innerHTML = '';
}

/**
 * Close the game search modal
 */
function closeSearchModal() {
    searchModal.classList.remove('active');
    document.body.style.overflow = '';
}

/**
 * Show the edit code input step
 */
function showEditCodeStep() {
    editCodeStep.style.display = 'block';
    searchStep.style.display = 'none';
    editCodeInput.value = '';
    editCodeInput.focus();
}

/**
 * Show the search step
 */
function showSearchStep() {
    editCodeStep.style.display = 'none';
    searchStep.style.display = 'block';
    gameSearchInput.value = '';
    gameSearchInput.focus();
}

/**
 * Verify the edit confirmation code
 */
async function verifyEditCode() {
    const code = editCodeInput.value.trim();

    if (!code) {
        showError(editCodeError, 'Please enter a code');
        return;
    }

    verifyEditCodeBtn.disabled = true;
    verifyEditCodeBtn.textContent = 'Verifying...';

    try {
        const level = await validateAccessCodeWithLevel(code);

        if (level === 'edit') {
            storeCode(code);
            storePermissionLevel(level);
            hideError(editCodeError);
            showSearchStep();
        } else if (level === 'submit') {
            showError(editCodeError, 'This code only allows adding games, not editing. Use the edit code.');
        } else {
            showError(editCodeError, 'Invalid code. Please try again.');
        }
    } catch (error) {
        showError(editCodeError, 'Error verifying code. Please try again.');
        console.error('Edit code verification error:', error);
    } finally {
        verifyEditCodeBtn.disabled = false;
        verifyEditCodeBtn.textContent = 'Verify';
    }
}

/**
 * Escape HTML to prevent XSS attacks
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Perform game search (XSS-safe)
 */
async function performGameSearch() {
    const query = gameSearchInput.value.trim();

    if (!query) {
        searchResults.innerHTML = '<div class="no-results">Please enter a search term</div>';
        return;
    }

    searchGamesBtn.disabled = true;
    searchGamesBtn.textContent = 'Searching...';

    try {
        const games = await searchGamesApi(query);

        if (games.length === 0) {
            searchResults.innerHTML = '<div class="no-results">No games found matching your search</div>';
        } else {
            // Clear previous results
            searchResults.innerHTML = '';

            // Build results safely using DOM methods to prevent XSS
            games.forEach(game => {
                const card = document.createElement('div');
                card.className = 'game-result-card';
                card.dataset.gameId = game.game_id;

                const header = document.createElement('div');
                header.className = 'game-result-header';

                const gameIdSpan = document.createElement('span');
                gameIdSpan.className = 'game-result-id';
                gameIdSpan.textContent = `Game #${game.game_id}`;

                const winnerSpan = document.createElement('span');
                winnerSpan.className = `game-result-winner ${(game.winning_team || '').toLowerCase()}`;
                winnerSpan.textContent = `${game.winning_team} Won`;

                header.appendChild(gameIdSpan);
                header.appendChild(winnerSpan);

                const details = document.createElement('div');
                details.className = 'game-result-details';

                const scriptSpan = document.createElement('span');
                scriptSpan.textContent = game.game_mode || 'Unknown Script';

                const stSpan = document.createElement('span');
                stSpan.textContent = `ST: ${game.story_teller || 'Unknown'}`;

                const dateSpan = document.createElement('span');
                dateSpan.textContent = game.date ? new Date(game.date).toLocaleDateString() : '';

                details.appendChild(scriptSpan);
                details.appendChild(stSpan);
                details.appendChild(dateSpan);

                card.appendChild(header);
                card.appendChild(details);

                // Add click handler
                card.addEventListener('click', () => {
                    loadGameForEdit(game.game_id);
                });

                searchResults.appendChild(card);
            });
        }
    } catch (error) {
        searchResults.innerHTML = '<div class="no-results">Error searching games. Please try again.</div>';
        console.error('Search error:', error);
    } finally {
        searchGamesBtn.disabled = false;
        searchGamesBtn.textContent = 'Search';
    }
}

/**
 * Load a game for editing
 */
async function loadGameForEdit(gameId) {
    try {
        const game = await getGameById(gameId);

        // Set edit mode
        editMode = true;
        currentEditGameId = gameId;

        // Close search modal and open game entry modal
        closeSearchModal();

        // Populate the form
        populateFormWithGame(game);

        // Update form title
        formTitle.innerHTML = `Edit Game #${gameId} <span class="edit-mode-badge">EDITING</span>`;
        formSubtitle.textContent = 'Modify the game details below';
        formStep.classList.add('edit-mode');
        submitBtn.textContent = 'Update Game';

        // Show the game entry modal
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        codeStep.style.display = 'none';
        formStep.style.display = 'block';

    } catch (error) {
        console.error('Error loading game:', error);
        alert('Failed to load game for editing. Please try again.');
    }
}

/**
 * Populate the form with existing game data
 */
function populateFormWithGame(game) {
    // Separate players by team
    const evilPlayers = game.players.filter(p => p.team === 'Evil');
    const goodPlayers = game.players.filter(p => p.team === 'Good');

    // Determine which team is team 1 (Evil team)
    const team1IsEvil = true; // We'll put Evil in Team 1
    const team1Players = evilPlayers;
    const team2Players = goodPlayers;

    // Format players for textarea
    team1Input.value = formatPlayersForTextarea(team1Players);
    team2Input.value = formatPlayersForTextarea(team2Players);

    // Set evil team radio (Team 1 = Evil)
    evilTeamRadios.forEach(r => {
        r.checked = r.value === '1';
    });

    // Set winner radio
    const winnerTeamNum = game.winning_team === 'Evil' ? '1' : '2';
    winnerRadios.forEach(r => {
        r.checked = r.value === winnerTeamNum;
    });

    // Set script
    scriptSelect.value = game.game_mode || 'Trouble Brewing';

    // Set storyteller
    storytellerInput.value = game.story_teller || '';
}

/**
 * Format players array for textarea display
 */
function formatPlayersForTextarea(players) {
    return players.map(p => {
        let line = p.name;

        // Add roles
        if (p.roles && p.roles.length > 0) {
            line += ' ' + p.roles.join('+');
        } else if (p.role) {
            line += ' ' + p.role;
        }

        // Add team hint if initial team differs from final team
        if (p.initial_team && p.initial_team !== p.team) {
            line += ' ' + p.initial_team + '->' + p.team;
        }

        return line;
    }).join('\n');
}

/**
 * Reset to add mode (not edit mode)
 */
function resetToAddMode() {
    editMode = false;
    currentEditGameId = null;
    formTitle.textContent = 'Add New Game';
    formSubtitle.textContent = 'Enter game details below';
    formStep.classList.remove('edit-mode');
    submitBtn.textContent = 'Submit Game';
    clearForm();
}
