/**
 * BotC Dimensions — Interactive Skill Tree
 * Hubs expand on click to reveal labeled subskill nodes.
 * Hub borders use parent-skill color gradients.
 * Phase filter dims non-matching nodes.
 */
import { CORE_SKILLS, FUSION_SKILLS } from './skills.js';

// === State ===
// alignment toggle removed — both sides shown in sidebar
let selectedNode = null;
let hoveredNode = null;
let expandedHub = null; // which hub is currently expanded
let activePhase = 'all';
let nodes = [];
let edges = [];
let expandedSubNodes = []; // dynamically created when a hub expands
let canvasWidth = 0;
let canvasHeight = 0;
let animFrame = 0;
let expandProgress = 0; // 0-1 animation

const TIER_COLORS = { 1: '#60a5fa', 2: '#a78bfa', 3: '#f472b6', 4: '#fb923c', 5: '#fbbf24' };
const TIER_LABELS = { 1: 'Attribute', 2: 'Skill', 3: 'Skill', 4: 'Skill', 5: 'Mastery' };

function getNodeLabel(node) {
    if (node.type === 'hub') return 'Skill';
    if (node.type === 'subskill') return 'Skill';
    return TIER_LABELS[node.tier || 1];
}

function getNodeSize(node) {
    if (node.type === 'hub') return 28;
    return node.tier === 1 ? 34 : 20;
}

function isNodeInPhase(node, phase) {
    if (phase === 'all' || node.tier === 1) return true;
    return node.phases ? node.phases.includes(phase) : true;
}

function getParentColors(node) {
    return (node.parents || []).map(pid => {
        const p = CORE_SKILLS.find(s => s.id === pid);
        return p ? p.color : '#a78bfa';
    });
}

// === Init ===
const canvas = document.getElementById('skill-graph');
if (!canvas) throw new Error('No #skill-graph canvas');
const ctx = canvas.getContext('2d');
const tooltip = document.getElementById('tooltip');

function init() {
    buildGraph();
    setupEvents();
    resize();
    animate();
}

// === Layout ===
function getNodePositions() {
    return {
        'deception':          { x: 0.50, y: 0.08 },
        'logic':              { x: 0.08, y: 0.38 },
        'persuasion':         { x: 0.92, y: 0.38 },
        'game-knowledge':     { x: 0.22, y: 0.82 },
        'social-insight':     { x: 0.78, y: 0.82 },
        'initial-bluff':      { x: 0.26, y: 0.24 },
        'social-credibility': { x: 0.88, y: 0.62 },
        'role-determination': { x: 0.24, y: 0.56 },
        'voting-blocks':      { x: 0.64, y: 0.44 },
        'world-building':     { x: 0.56, y: 0.66 },
        'winrate-math':       { x: 0.12, y: 0.70 },
    };
}

function buildGraph() {
    const positions = getNodePositions();
    nodes = [];
    edges = [];

    CORE_SKILLS.forEach(skill => {
        nodes.push({ ...skill, tier: 1, pos: positions[skill.id], parents: [] });
    });

    FUSION_SKILLS.forEach(fusion => {
        if (fusion.type === 'subskill') return;
        if (positions[fusion.id]) {
            nodes.push({ ...fusion, pos: positions[fusion.id] });
        }
    });

    const coreIds = CORE_SKILLS.map(s => s.id);
    for (let i = 0; i < coreIds.length; i++) {
        for (let j = i + 1; j < coreIds.length; j++) {
            edges.push({ from: coreIds[i], to: coreIds[j], type: 'web' });
        }
    }

    FUSION_SKILLS.filter(f => f.type !== 'subskill').forEach(skill => {
        (skill.parents || []).forEach(pid => {
            if (coreIds.includes(pid)) {
                edges.push({ from: pid, to: skill.id, type: 'skill' });
            }
        });
    });
}

// === Expand/collapse hubs ===
function expandHub(hub) {
    expandedHub = hub;
    expandProgress = 0;
    const subs = FUSION_SKILLS.filter(f => f.hubId === hub.id);
    const hubPos = hub.pos;
    const expandRadius = 0.14;

    // Manual subskill positions for specific hubs
    const subPositions = {
        'winrate-math': {
            'good-baseline': { x: 0.04, y: 0.52 },
            'evil-baseline': { x: 0.18, y: 0.52 },
            'good-skip-d1': { x: 0.28, y: 0.68 },
            'evil-skip-d1': { x: 0.04, y: 0.82 },
        }
    };
    const subPositions_extra = {
        'voting-blocks': {
            'vote-math': { x: 0.52, y: 0.28 },
            'voting-tells': { x: 0.76, y: 0.28 },
            'coalition-building': { x: 0.52, y: 0.56 },
        },
        'role-determination': {
            'info-gathering': { x: 0.34, y: 0.34 },
            'evil-board-reading': { x: 0.10, y: 0.52 },
            'reaction-reading': { x: 0.36, y: 0.66 },
        }
    };
    Object.assign(subPositions, subPositions_extra);
    const manualPositions = subPositions[hub.id];

    // Distribute evenly, offset to avoid overlapping hub label below
    expandedSubNodes = subs.map((sub, i) => {
        if (manualPositions && manualPositions[sub.id]) {
            return { ...sub, pos: manualPositions[sub.id] };
        }
        // Start from top-left, spread around upper hemisphere + sides to avoid bottom label
        const angleSpread = Math.PI * 1.6; // ~290 degrees, skip the bottom
        const startAngle = -Math.PI * 0.9; // start from upper-left
        const angle = subs.length === 1
            ? -Math.PI / 2 // single sub goes straight up
            : startAngle + (i / (subs.length - 1)) * angleSpread;
        return {
            ...sub,
            pos: {
                x: Math.max(0.06, Math.min(0.94, hubPos.x + Math.cos(angle) * expandRadius)),
                y: Math.max(0.06, Math.min(0.90, hubPos.y + Math.sin(angle) * expandRadius * 0.85))
            }
        };
    });
}

function collapseHub() {
    expandedHub = null;
    expandedSubNodes = [];
    expandProgress = 0;
}

// === Canvas ===
function resize() {
    const container = canvas.parentElement;
    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvasWidth = rect.width;
    canvasHeight = Math.max(550, rect.height);
    canvas.width = canvasWidth * dpr;
    canvas.height = canvasHeight * dpr;
    canvas.style.width = canvasWidth + 'px';
    canvas.style.height = canvasHeight + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

function toPixel(pos) {
    return { x: pos.x * canvasWidth, y: pos.y * canvasHeight };
}

function hexPath(cx, cy, radius) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
        const angle = (Math.PI / 3) * i - Math.PI / 2;
        const x = cx + radius * Math.cos(angle);
        const y = cy + radius * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.closePath();
}

function drawGradientBorder(cx, cy, radius, colors, lineWidth, alpha) {
    if (colors.length === 0) return;
    if (colors.length === 1) {
        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, Math.PI * 2);
        ctx.strokeStyle = colors[0] + alpha;
        ctx.lineWidth = lineWidth;
        ctx.stroke();
        return;
    }
    const segAngle = (Math.PI * 2) / colors.length;
    colors.forEach((c, i) => {
        ctx.beginPath();
        ctx.arc(cx, cy, radius, segAngle * i - Math.PI / 2, segAngle * (i + 1) - Math.PI / 2);
        ctx.strokeStyle = c + alpha;
        ctx.lineWidth = lineWidth;
        ctx.stroke();
    });
}

function render() {
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    // Expand animation
    if (expandedHub) {
        expandProgress = Math.min(1, expandProgress + 0.06);
    }

    const accentColor = '96, 165, 250';
    const centerGlow = ctx.createRadialGradient(
        canvasWidth / 2, canvasHeight / 2, 0,
        canvasWidth / 2, canvasHeight / 2, canvasWidth * 0.4
    );
    centerGlow.addColorStop(0, `rgba(${accentColor}, 0.05)`);
    centerGlow.addColorStop(1, 'transparent');
    ctx.fillStyle = centerGlow;
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    // Determine which node's parent edges to highlight
    let highlightParentIds = null;
    let highlightNodeId = null;
    if (selectedNode) {
        if (selectedNode.type === 'subskill' && expandedHub) {
            // Subskill selected: highlight hub's parent edges
            highlightParentIds = expandedHub.parents || [];
            highlightNodeId = expandedHub.id;
        } else {
            highlightParentIds = selectedNode.parents || [];
            highlightNodeId = selectedNode.id;
        }
    }

    // Draw edges
    edges.forEach(edge => {
        const fromNode = nodes.find(n => n.id === edge.from);
        const toNode = nodes.find(n => n.id === edge.to);
        if (!fromNode || !toNode) return;
        const from = toPixel(fromNode.pos);
        const to = toPixel(toNode.pos);
        const fromIn = isNodeInPhase(fromNode, activePhase);
        const toIn = isNodeInPhase(toNode, activePhase);
        // When any node is selected, dim edges not connected to it
        const selEdgeDimmed = selectedNode &&
            edge.from !== (highlightNodeId || '') && edge.to !== (highlightNodeId || '');
        const dimmed = !(fromIn && toIn) || selEdgeDimmed;

        // Check if this edge should be highlighted (connected to selected node's relationships)
        let isHighlighted = false;
        if (highlightNodeId && edge.type === 'skill') {
            if (selectedNode && selectedNode.tier === 1) {
                // Core skill: highlight all skill-type edges from this core
                isHighlighted = edge.from === highlightNodeId || edge.to === highlightNodeId;
            } else if (highlightParentIds) {
                // Skill/hub: highlight edges to parents
                isHighlighted = (edge.to === highlightNodeId && highlightParentIds.includes(edge.from)) ||
                    (edge.from === highlightNodeId && highlightParentIds.includes(edge.to));
            }
        }

        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);

        if (isHighlighted) {
            const color = selectedNode.color || TIER_COLORS[selectedNode.tier || 1];
            ctx.strokeStyle = color + '80';
            ctx.lineWidth = 2.5;
            ctx.shadowColor = color;
            ctx.shadowBlur = 8;
        } else if (dimmed) {
            ctx.strokeStyle = 'rgba(45, 55, 72, 0.04)';
            ctx.lineWidth = 1;
        } else if (edge.type === 'web') {
            ctx.strokeStyle = `rgba(${accentColor}, 0.05)`;
            ctx.lineWidth = 1;
        } else {
            ctx.strokeStyle = 'rgba(45, 55, 72, 0.2)';
            ctx.lineWidth = 1.5;
        }
        ctx.stroke();
        ctx.shadowBlur = 0;
    });

    // Draw expanded subskill connections
    if (expandedHub && expandProgress > 0) {
        const hubPos = toPixel(expandedHub.pos);
        const hubColors = getParentColors(expandedHub);
        const hubLineColor = hubColors.length === 1 ? hubColors[0] + '50' : 'rgba(167, 139, 250, 0.3)';
        expandedSubNodes.forEach(sub => {
            const sp = toPixel(sub.pos);
            const x = hubPos.x + (sp.x - hubPos.x) * expandProgress;
            const y = hubPos.y + (sp.y - hubPos.y) * expandProgress;
            ctx.beginPath();
            ctx.moveTo(hubPos.x, hubPos.y);
            ctx.lineTo(x, y);
            ctx.strokeStyle = hubLineColor;
            ctx.lineWidth = 1.5;
            ctx.stroke();
        });
    }

    // Draw nodes
    nodes.forEach(node => {
        const pos = toPixel(node.pos);
        const tier = node.tier || 1;
        const baseSize = getNodeSize(node);
        const isSelected = selectedNode && selectedNode.id === node.id;
        const isHovered = hoveredNode && hoveredNode.id === node.id;
        const isExpanded = expandedHub && expandedHub.id === node.id;
        const phaseDimmed = !isNodeInPhase(node, activePhase);
        // When a node is selected, dim unrelated nodes
        let selectionDimmed = false;
        if (selectedNode && !isSelected) {
            if (selectedNode.tier === 1) {
                // Core skill selected: keep children (skills that list it as parent)
                const isChild = (node.parents || []).includes(selectedNode.id);
                selectionDimmed = !isChild;
            } else {
                // Skill/hub/subskill selected: keep its parent core skills and expanded hub
                const selParents = (selectedNode.type === 'subskill' && expandedHub ? expandedHub.parents : selectedNode.parents) || [];
                selectionDimmed = !selParents.includes(node.id) &&
                    !(expandedHub && expandedHub.id === node.id);
            }
        }
        const dimmed = phaseDimmed || selectionDimmed;

        const pulse = tier === 1 ? Math.sin(animFrame * 0.02 + CORE_SKILLS.findIndex(s => s.id === node.id)) * 1.2 : 0;
        const expandBoost = isExpanded ? baseSize * 0.3 * expandProgress : 0;
        const size = (isSelected ? baseSize * 1.1 : isHovered ? baseSize * 1.05 : baseSize) + pulse + expandBoost;
        const parentColors = getParentColors(node);
        const color = node.color || TIER_COLORS[tier];

        // Glow for selected/hovered
        if ((isSelected || isHovered) && !phaseDimmed) {
            ctx.shadowColor = color;
            ctx.shadowBlur = isSelected ? 18 : 10;
        }

        // Dark fill
        if (tier === 1) {
            hexPath(pos.x, pos.y, size);
        } else {
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, size, 0, Math.PI * 2);
        }
        ctx.fillStyle = `rgba(15, 20, 35, ${dimmed ? 0.3 : 0.88})`;
        ctx.fill();

        // Border — hubs get parent-color gradient, others get single color
        if (node.type === 'hub' && parentColors.length > 0 && !dimmed) {
            drawGradientBorder(pos.x, pos.y, size, parentColors, isSelected ? 3 : 2.5, isSelected ? 'ff' : 'aa');
        } else {
            if (tier === 1) {
                hexPath(pos.x, pos.y, size);
            } else {
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, size, 0, Math.PI * 2);
            }
            ctx.strokeStyle = dimmed ? color + '12' : isSelected ? color : color + '70';
            ctx.lineWidth = isSelected ? 3 : 2;
            ctx.stroke();
        }
        ctx.shadowBlur = 0;

        // Content
        ctx.globalAlpha = dimmed ? 0.12 : 1;

        if (tier === 1) {
            ctx.font = '22px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(node.icon, pos.x, pos.y);
        } else if (node.type === 'hub') {
            // Parent color dots in center
            const dotR = size * 0.25;
            const pAngle = Math.PI * 2 / parentColors.length;
            parentColors.forEach((c, i) => {
                const a = pAngle * i - Math.PI / 2;
                ctx.beginPath();
                ctx.arc(pos.x + Math.cos(a) * dotR, pos.y + Math.sin(a) * dotR, 3.5, 0, Math.PI * 2);
                ctx.fillStyle = c + 'cc';
                ctx.fill();
            });

            // Subskill count badge
            const subCount = FUSION_SKILLS.filter(f => f.hubId === node.id).length;
            if (subCount > 0 && !isExpanded) {
                const badgeX = pos.x + size * 0.7;
                const badgeY = pos.y - size * 0.7;
                ctx.beginPath();
                ctx.arc(badgeX, badgeY, 9, 0, Math.PI * 2);
                ctx.fillStyle = '#a78bfa';
                ctx.fill();
                ctx.font = 'bold 9px -apple-system, sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = '#ffffff';
                ctx.fillText(subCount, badgeX, badgeY);
            }
        } else {
            // Regular skill: parent dots
            const dotR = size * 0.35;
            const angleStep = (Math.PI * 2) / parentColors.length;
            parentColors.forEach((c, i) => {
                const a = angleStep * i - Math.PI / 2;
                ctx.beginPath();
                ctx.arc(pos.x + Math.cos(a) * dotR, pos.y + Math.sin(a) * dotR, 3.5, 0, Math.PI * 2);
                ctx.fillStyle = c + 'cc';
                ctx.fill();
            });
        }
        ctx.globalAlpha = 1;

        // Label
        const labelY = pos.y + size + 12;
        const fontSize = tier === 1 ? '600 13px' : '500 10px';
        const lineHeight = tier === 1 ? 15 : 12;
        ctx.font = `${fontSize} -apple-system, BlinkMacSystemFont, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillStyle = dimmed ? 'rgba(234, 234, 234, 0.06)' : 'rgba(234, 234, 234, 0.85)';

        const maxW = tier === 1 ? 110 : 90;
        wrapText(node.name, pos.x, labelY, maxW, lineHeight);
    });

    // Draw expanded subskill nodes
    if (expandedHub && expandProgress > 0.1) {
        const hubPos = toPixel(expandedHub.pos);

        expandedSubNodes.forEach(sub => {
            const targetPos = toPixel(sub.pos);
            const px = hubPos.x + (targetPos.x - hubPos.x) * expandProgress;
            const py = hubPos.y + (targetPos.y - hubPos.y) * expandProgress;
            const subSize = 14 * expandProgress;
            const isSubHovered = hoveredNode && hoveredNode.id === sub.id;
            const isSubSelected = selectedNode && selectedNode.id === sub.id;
            const alpha = expandProgress;

            ctx.globalAlpha = alpha;

            // Glow — use subskill's own parent colors
            const subColors = getParentColors(sub);
            const glowColor = subColors.length === 1 ? subColors[0] : '#a78bfa';
            if (isSubSelected || isSubHovered) {
                ctx.shadowColor = glowColor;
                ctx.shadowBlur = 10;
            }

            // Fill
            ctx.beginPath();
            ctx.arc(px, py, subSize, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(15, 20, 35, 0.9)';
            ctx.fill();

            // Parent-color gradient border (subskill's own parents)
            if (subColors.length > 0) {
                drawGradientBorder(px, py, subSize, subColors, isSubSelected ? 2.5 : 1.5, isSubSelected ? 'cc' : '88');
            } else {
                ctx.strokeStyle = isSubSelected ? glowColor : glowColor + '88';
                ctx.lineWidth = isSubSelected ? 2.5 : 1.5;
                ctx.stroke();
            }
            ctx.shadowBlur = 0;

            // Label — always show when expanded
            ctx.font = (isSubHovered || isSubSelected) ? '600 10px -apple-system, sans-serif' : '500 9px -apple-system, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillStyle = `rgba(234, 234, 234, ${alpha * ((isSubHovered || isSubSelected) ? 0.95 : 0.7)})`;
            wrapText(sub.name, px, py + subSize + 6, 80, 10);

            ctx.globalAlpha = 1;
        });
    }
}

function wrapText(text, x, y, maxW, lineH) {
    const rawLines = text.split('\n');
    const lines = [];
    rawLines.forEach(raw => {
        const words = raw.split(' ');
        let cur = words[0];
        for (let w = 1; w < words.length; w++) {
            const test = cur + ' ' + words[w];
            if (ctx.measureText(test).width > maxW) {
                lines.push(cur);
                cur = words[w];
            } else cur = test;
        }
        lines.push(cur);
    });
    lines.forEach((l, i) => ctx.fillText(l, x, y + i * lineH));
}

// === Animation ===
function animate() {
    animFrame++;
    render();
    requestAnimationFrame(animate);
}

// === Interaction ===
function getNodeAt(mx, my) {
    // Check expanded subskills first (on top)
    if (expandedHub && expandProgress > 0.5) {
        const hubPos = toPixel(expandedHub.pos);
        for (let i = expandedSubNodes.length - 1; i >= 0; i--) {
            const sub = expandedSubNodes[i];
            const tp = toPixel(sub.pos);
            const sx = hubPos.x + (tp.x - hubPos.x) * expandProgress;
            const sy = hubPos.y + (tp.y - hubPos.y) * expandProgress;
            const dx = mx - sx;
            const dy = my - sy;
            if (dx * dx + dy * dy <= 24 * 24) return sub;
        }
    }

    // Then main nodes
    for (let i = nodes.length - 1; i >= 0; i--) {
        const node = nodes[i];
        const pos = toPixel(node.pos);
        const hitSize = getNodeSize(node) + 8;
        const dx = mx - pos.x;
        const dy = my - pos.y;
        if (dx * dx + dy * dy <= hitSize * hitSize) return node;
    }
    return null;
}

function setupEvents() {
    canvas.addEventListener('mousemove', e => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const node = getNodeAt(mx, my);

        if (node !== hoveredNode) {
            hoveredNode = node;
            canvas.style.cursor = node ? 'pointer' : 'default';
            if (node) {
                tooltip.querySelector('.tooltip-name').textContent = node.name.replace(/\n/g, ' ');
                tooltip.querySelector('.tooltip-tier').textContent = getNodeLabel(node);
                tooltip.style.display = 'block';
            } else {
                tooltip.style.display = 'none';
            }
        }
        if (node) {
            let tx = e.clientX - canvas.parentElement.getBoundingClientRect().left + 16;
            let ty = e.clientY - canvas.parentElement.getBoundingClientRect().top - 10;
            if (tx + 220 > canvasWidth) tx -= 240;
            if (ty < 0) ty = 10;
            tooltip.style.left = tx + 'px';
            tooltip.style.top = ty + 'px';
        }
    });

    canvas.addEventListener('mouseleave', () => {
        hoveredNode = null;
        tooltip.style.display = 'none';
    });

    canvas.addEventListener('click', e => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const node = getNodeAt(mx, my);

        if (node) {
            if (node.type === 'hub') {
                // Toggle hub expand
                if (expandedHub && expandedHub.id === node.id) {
                    collapseHub();
                } else {
                    expandHub(node);
                }
                selectedNode = node;
                showDetail(node);
            } else {
                if (expandedHub && node.type !== 'subskill') {
                    collapseHub();
                }
                selectedNode = node;
                showDetail(node);
            }
        } else {
            selectedNode = null;
            collapseHub();
            hideDetail();
        }
    });

    document.getElementById('sidebar-close').addEventListener('click', () => {
        selectedNode = null;
        collapseHub();
        hideDetail();
    });

    // Phase pills (inline on strategy page)
    document.querySelectorAll('.phase-pill').forEach(btn => {
        btn.addEventListener('click', () => {
            activePhase = btn.dataset.phase;
            document.querySelectorAll('.phase-pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    document.addEventListener('phaseChanged', (e) => {
        activePhase = e.detail.phase;
    });

    window.addEventListener('resize', resize);
}

function showDetail(node) {
    const empty = document.getElementById('sidebar-empty');
    const content = document.getElementById('sidebar-content');
    const tier = node.tier || 1;

    empty.style.display = 'none';
    content.style.display = 'block';
    content.className = 'sidebar-content';

    document.getElementById('detail-icon').textContent =
        tier === 1 ? node.icon : '🔗';
    document.getElementById('detail-name').textContent = node.name.replace(/\n/g, ' ');
    const tierEl = document.getElementById('detail-tier');
    tierEl.textContent = getNodeLabel(node);
    tierEl.className = `detail-tier tier-${tier}`;

    document.getElementById('detail-description').textContent = node.description || '';

    // Parents
    const parentsSection = document.getElementById('detail-parents');
    const parentTags = document.getElementById('parent-tags');
    if (node.parents && node.parents.length > 0 && tier > 1) {
        parentsSection.style.display = 'block';
        parentTags.innerHTML = '';
        node.parents.forEach(pid => {
            const parent = CORE_SKILLS.find(s => s.id === pid);
            if (parent) {
                const tag = document.createElement('span');
                tag.className = `skill-tag ${pid}`;
                tag.textContent = parent.name;
                tag.addEventListener('click', () => {
                    const pn = nodes.find(n => n.id === pid);
                    if (pn) { selectedNode = pn; showDetail(pn); }
                });
                parentTags.appendChild(tag);
            }
        });
    } else {
        parentsSection.style.display = 'none';
    }

    // Content: chart (if any), then article
    const alignContainer = document.getElementById('detail-alignments');
    alignContainer.innerHTML = '';

    // Chart above article for winrate subskills
    if (node.chartId) {
        const chartWrapper = document.createElement('div');
        chartWrapper.style.cssText = 'position:relative;height:220px;width:100%;margin:12px 0 16px;';
        const chartCanvas = document.createElement('canvas');
        chartCanvas.id = 'sidebar-chart';
        chartWrapper.appendChild(chartCanvas);
        alignContainer.appendChild(chartWrapper);
        // Render chart after it's in the DOM
        setTimeout(() => {
            if (sidebarChart) { sidebarChart.destroy(); sidebarChart = null; }
            sidebarChart = renderWinrateChart(document.getElementById('sidebar-chart'), node.chartId);
        }, 0);
    }

    if (node.article) {
        const articleDiv = document.createElement('div');
        articleDiv.className = 'detail-article';
        articleDiv.innerHTML = node.article;
        alignContainer.appendChild(articleDiv);
    }

    // Connected skills
    const fusionsSection = document.getElementById('detail-fusions');
    const fusionTags = document.getElementById('fusion-tags');
    let connectedItems = [];
    let sectionTitle = 'Skills';

    if (tier === 1) {
        connectedItems = FUSION_SKILLS.filter(f => f.parents.includes(node.id) && f.type !== 'subskill');
        sectionTitle = 'Connected Skills';
    } else if (node.type === 'hub') {
        connectedItems = FUSION_SKILLS.filter(f => f.hubId === node.id);
        sectionTitle = 'Contains';
    } else if (node.type === 'subskill' && node.hubId) {
        const hub = FUSION_SKILLS.find(f => f.id === node.hubId);
        if (hub) connectedItems = [hub];
        connectedItems = connectedItems.concat(FUSION_SKILLS.filter(f => f.hubId === node.hubId && f.id !== node.id));
        sectionTitle = 'Part of';
    }

    if (connectedItems.length > 0) {
        fusionsSection.style.display = 'block';
        fusionsSection.querySelector('h3').textContent = sectionTitle;
        fusionTags.innerHTML = '';
        connectedItems.forEach(item => {
            const tag = document.createElement('span');
            tag.className = 'skill-tag fusion';
            tag.textContent = item.name;
            tag.addEventListener('click', () => {
                // If clicking a subskill tag, expand the hub and select it
                if (item.type === 'subskill' && item.hubId) {
                    const hub = nodes.find(n => n.id === item.hubId);
                    if (hub && (!expandedHub || expandedHub.id !== hub.id)) expandHub(hub);
                    // Wait for expand, then select
                    setTimeout(() => {
                        const subNode = expandedSubNodes.find(s => s.id === item.id);
                        if (subNode) { selectedNode = subNode; showDetail(subNode); }
                    }, 200);
                } else {
                    const fn = nodes.find(n => n.id === item.id);
                    if (fn) { selectedNode = fn; showDetail(fn); }
                }
            });
            fusionTags.appendChild(tag);
        });
    } else {
        fusionsSection.style.display = 'none';
    }

    // Clean up old chart if no chartId (chart now renders in alignments container)
    const articleEl = document.getElementById('detail-article');
    if (!node.chartId && sidebarChart) { sidebarChart.destroy(); sidebarChart = null; }
    articleEl.style.display = 'none';
    articleEl.innerHTML = '';

    // Scroll sidebar to top when showing new content
    document.getElementById('detail-sidebar').scrollTop = 0;
}

let sidebarChart = null;

// === Win Rate Charts ===
const WR_PLAYERS = [7, 8, 9, 10, 11, 12, 13, 14, 15];
const WR_LABELS = WR_PLAYERS.map(n => n + 'P');
const WR_GOOD_EXEC = [54, 51, 59, 49, 59, 54, 59, 53, 62];
const WR_GOOD_SKIP = [44, 54, 51, 54, 49, 59, 48, 59, 53];
const WR_EVIL_EXEC = WR_GOOD_EXEC.map(v => 100 - v);
const WR_EVIL_SKIP = WR_GOOD_SKIP.map(v => 100 - v);

function wrBarColors(base, alt) {
    return WR_PLAYERS.map(n => n % 2 === 1 ? base : alt);
}

const wrFiftyLine = {
    id: 'fiftyLine',
    afterDraw(chart) {
        const y = chart.scales.y.getPixelForValue(50);
        const ctx = chart.ctx;
        ctx.save();
        ctx.setLineDash([6, 4]);
        ctx.strokeStyle = 'rgba(160, 160, 160, 0.3)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(chart.chartArea.left, y);
        ctx.lineTo(chart.chartArea.right, y);
        ctx.stroke();
        ctx.fillStyle = 'rgba(160, 160, 160, 0.5)';
        ctx.font = '10px -apple-system, sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText('50%', chart.chartArea.right, y - 5);
        ctx.restore();
    }
};

function wrChartOpts(yLabel, showLegend) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: showLegend, labels: { color: '#a0a0a0', usePointStyle: true, pointStyle: 'rect', font: { size: 10 } } } },
        scales: {
            y: { min: 30, max: 70, grid: { color: 'rgba(45, 55, 72, 0.3)' }, ticks: { color: '#a0a0a0', callback: v => v + '%', font: { size: 10 } }, title: { display: true, text: yLabel, color: '#a0a0a0', font: { size: 10 } } },
            x: { grid: { display: false }, ticks: { color: '#a0a0a0', font: { size: 10 } } }
        },
        animation: { duration: 600, easing: 'easeOutQuart' }
    };
}

function renderWinrateChart(canvas, chartId) {
    const configs = {
        'good-baseline': {
            datasets: [{ label: 'Good Win %', data: WR_GOOD_EXEC, backgroundColor: wrBarColors('rgba(74, 222, 128, 0.6)', 'rgba(74, 222, 128, 0.35)'), borderColor: wrBarColors('#4ade80', 'rgba(74, 222, 128, 0.6)'), borderWidth: 1, borderRadius: 4 }],
            opts: wrChartOpts('Good Win %', false)
        },
        'evil-baseline': {
            datasets: [{ label: 'Evil Win %', data: WR_EVIL_EXEC, backgroundColor: wrBarColors('rgba(248, 113, 113, 0.35)', 'rgba(248, 113, 113, 0.6)'), borderColor: wrBarColors('rgba(248, 113, 113, 0.6)', '#f87171'), borderWidth: 1, borderRadius: 4 }],
            opts: wrChartOpts('Evil Win %', false)
        },
        'good-skip-d1': {
            datasets: [
                { label: 'Execute Day 1', data: WR_GOOD_EXEC, backgroundColor: 'rgba(74, 222, 128, 0.5)', borderColor: '#4ade80', borderWidth: 1, borderRadius: 4 },
                { label: 'Skip Day 1', data: WR_GOOD_SKIP, backgroundColor: 'rgba(96, 165, 250, 0.5)', borderColor: '#60a5fa', borderWidth: 1, borderRadius: 4 }
            ],
            opts: wrChartOpts('Good Win %', true)
        },
        'evil-skip-d1': {
            datasets: [
                { label: 'Good Executes Day 1', data: WR_EVIL_EXEC, backgroundColor: 'rgba(248, 113, 113, 0.5)', borderColor: '#f87171', borderWidth: 1, borderRadius: 4 },
                { label: 'Good Skips Day 1', data: WR_EVIL_SKIP, backgroundColor: 'rgba(251, 191, 36, 0.5)', borderColor: '#fbbf24', borderWidth: 1, borderRadius: 4 }
            ],
            opts: wrChartOpts('Evil Win %', true)
        }
    };

    const cfg = configs[chartId];
    if (!cfg) return null;

    return new Chart(canvas, {
        type: 'bar',
        data: { labels: WR_LABELS, datasets: cfg.datasets },
        options: cfg.opts,
        plugins: [wrFiftyLine]
    });
}

function hideDetail() {
    const empty = document.getElementById('sidebar-empty');
    const content = document.getElementById('sidebar-content');
    empty.style.display = 'flex';
    content.style.display = 'none';
    if (sidebarChart) { sidebarChart.destroy(); sidebarChart = null; }
}

init();
