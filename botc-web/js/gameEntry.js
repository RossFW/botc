/**
 * Game Entry Module for Blood on the Clocktower Stats
 * Handles the game submission form and Supabase integration
 */

import { validateAccessCode, submitGame, getStoredCode, storeCode } from './supabase.js';

// DOM Elements
let modal, codeStep, formStep, codeInput, verifyBtn, codeError;
let team1Input, team2Input, evilTeamRadios, winnerRadios;
let scriptSelect, storytellerInput, submitBtn, submitError, submitSuccess;

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

    // Store callback
    window._onGameAdded = onGameAdded;

    // Set up event listeners
    setupEventListeners();

    // Check for stored code
    checkStoredCode();
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

    // ESC key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
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
 * Open the game entry modal
 */
function openModal() {
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

    // Submit
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';

    try {
        const code = getStoredCode();
        await submitGame(gameData, code);

        showSuccess(submitSuccess, 'Game submitted successfully!');

        // Clear form
        clearForm();

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
        submitBtn.textContent = 'Submit Game';
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
