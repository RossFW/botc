/**
 * BotC Dimensions - Skill Data
 *
 * Core skill definitions sourced from player experience.
 * Fusion skills are added as they're defined through brainstorming.
 */

export const CORE_SKILLS = [
    {
        id: 'logic',
        name: 'Logic',
        icon: '🧠',
        color: '#fbbf24',
        description: 'Solving the game through deduction and reasoning about incomplete information.',
        article: `
            <p>The ability to make rational conclusions based purely on the information available. Great logical players can solve the game single-handedly for the good team, and can make stronger decisions as an evil player that make the game increasingly challenging.</p>
            <p>Logic is a skill that new players begin at vastly different levels of competency. For some players the logic puzzles in BotC are immediately intuitive - but many new players prefer to let others solve the game.</p>
            <p>Similarly, logic is a slow skill to grow if a player isn't already logically inclined. Game knowledge helps with this a great deal, but other players never quite become "the solver" - preferring to lean on the more social axis as they grow in experience.</p>
        `
    },
    {
        id: 'game-knowledge',
        name: 'Game Knowledge',
        icon: '📚',
        color: '#4ade80',
        description: 'The experience that separates a veteran BotC player from a logical new player.',
        article: `
            <p>Game knowledge is the understanding of the rules and mechanics of BotC. Players with great game knowledge can solve storyteller puzzles simply by having seen them before (e.g. when the Recluse misregisters for the Investigator).</p>
            <p>Many players can inherently have strong logical skill (especially ones familiar with other deductive reasoning games) but game knowledge is the experience that separates a veteran BotC player from a "smart" new player.</p>
            <p>Given enough time and rules clarifications, a logically inclined player might solve the same puzzles that a veteran with great game knowledge can, but games don't last forever and many of the rules can be unintuitive for new players at first.</p>
            <h3>Game Knowledge on Evil</h3>
            <p>Another distinguishing factor is that game knowledge serves double-duty when on the evil team. Knowing patterns of play allows for faster, more convincing and damaging disinformation. In the worst cases, totally new players with no game knowledge can misrepresent their bluffs, or act in a way that gives themselves up simply because they don't know how players typically act as the role they're bluffing.</p>
            <p>For the strongest evil veterans, targeted lies send the good team down convincing false paths, evil members coordinate and target their own abilities in more devastating ways, and when put on the spot it's easier for a veteran to spin up a reasonable false world.</p>
            <h3>The Multiplicative Boost</h3>
            <p>In a way game knowledge is a multiplicative boost to all other axis of skill: it's easier to form logic lines, form convincing lies, persuade the rest of the town, and pick up tells when you're ultra familiar with the game.</p>
        `
    },
    {
        id: 'deception',
        name: 'Deception',
        icon: '🎭',
        color: '#f87171',
        description: 'Knowing when and how to lie — on both teams.',
        article: `
            <p>The ability to lie convincingly is a key asset in any social deduction game. Most players understand the inherent advantage of being skilled in deception while on the evil team. It takes some time before new players grow more comfortable with the idea of lying as a good player. Knowing when and how to lie while on the good team is critical in becoming stronger.</p>
            <h3>Deception on the Good Team</h3>
            <p>Playing as good, the typical prescription for new players is to tell the truth since you don't want to make it harder for the rest of the good team to solve. This is good advice for the late game, but horrible advice for the beginning (and often middle) of a BotC game. All that matters is killing the Demon before the end of the game, and it's oftentimes better to confuse the town alongside the evil team temporarily to glean extra information for the late game.</p>
            <p>A common pattern in Trouble Brewing is to ask openly on the first day who are the outsiders and first-night-only roles. This seems harmless but in reality it gives a huge edge for the evil team since it eliminates a wide range of potential targets, allowing the demon to target critical information roles with greater likelihood. New players often feel like the game was completely out of their control when they draw (i.e) the Saint out of the bag. In reality, they took away all their potential options by telling the entire town their true role well before they were even considered for nomination. If the Saint can convince the demon they are worth killing, it's a huge upside for the town since it removes a dangerous role whilst saving other relevant townsfolk from being targeted.</p>
            <h3>Cross-Game Pattern Consistency</h3>
            <p>Lying as good also pays dividends when actually evil (when playing with the same group consistently like we do). Players that establish that they always tell the truth about their role when good will struggle to act the same way when evil. In the example above, claiming Saint publicly on the first dawn when good makes it less credible in the future when playing as a minion and given Saint as a bluff. Savvy social players pick up on patterns between games and can suss out an evil player based on inconsistency in their strategy like this.</p>
            <p>Establishing a baseline tendency to lie in general at the beginning of the game, regardless of one's alignment, offers flexibility in evil games because players won't expect your first claim to be honest regardless. This gives you more time to devise a true bluff that you'll stick with through the end of the game, since you can pass off your initial false claims as attempts at strategy.</p>
            <h3>Growing the Skill</h3>
            <p>Deception is a skill some players inherently have. Others struggle immensely to lie even when forced to as an evil player. In my experience, players can absolutely grow in this skill even if they're not immediately disposed to it. Lying as a good player helps grow this skill faster since most games will be on the good team.</p>
        `
    },
    {
        id: 'persuasion',
        name: 'Persuasion',
        icon: '🗣️',
        color: '#60a5fa',
        description: 'Getting it right is only half the battle — you still have to get the vote.',
        article: `
            <p>The ability to convince the town of your perspective is another key skill for becoming a great BotC player. No matter how well one can solve the game, failing to win other players to one's side will result in defeat.</p>
            <p>Even a quiet player can be a strong persuader, making the right points to the right players in private during the day can be just as effective as commanding the floor publicly during nominations.</p>
            <h3>The Most Underrated Axis</h3>
            <p>Persuasion, to me, is the most underrated skill axis. Sometimes frustratingly, the loudest player can command the town more effectively than the smartest player. A common sentiment shared by players to me as the storyteller after a game is "I called it" or "I got it exactly right" even though the game ended in an evil win. Getting it right is only half the battle — do not sit quietly during a critical vote while the evil player tells the fellow town members emphatically to vote the other way.</p>
            <h3>Growing the Skill</h3>
            <p>Persuasion is the axis that I believe most players have a baseline level of competency when first playing. Humans are social and persuasion is a key skill in life, more so than deception. Some players are naturally louder, others are naturally convincing (especially alongside the other axis of skill). My advice to players wishing to become better at persuading others is to speak more during games until it feels natural.</p>
        `
    },
    {
        id: 'social-insight',
        name: 'Social Insight',
        icon: '👁️',
        color: '#a78bfa',
        description: 'Highest variance, highest ceiling — a correct read solves a coin flip, a wrong one loses the game.',
        article: `
            <p>As a storyteller, it's easy to presume that games will be solved by logic and strategic gameplay. The fifth and final axis is devoted to the skill of solving through social reads.</p>
            <p>Social insight is more nebulous than other skills when applied incorrectly — tunnel vision on a misplaced social read can wreak havoc on a game by pitting two good players against each other. But a correct social read can also allow for solving a game that otherwise might have been a coin flip.</p>
            <h3>Familiarity Matters</h3>
            <p>This skill is highest variance when playing with a group of players you have no prior experience with. It's dangerous to make assumptions about players without a baseline expectation of their behavior — especially if they're skilled veteran players.</p>
            <p>When playing with a consistent group, social intuition becomes more viable and more valuable, especially against players who are otherwise strong but have subtle tells you can pick up on.</p>
            <h3>Social Insight on Evil</h3>
            <p>Social insight serves a different purpose as an evil player. A valuable application is knowing who the other good players are suspicious of, to set up a clear framing toward the end of the game. Failure to do this effectively can convict the demon by process of implicit elimination, even when the logic would dictate an even chance among the remaining players of being the demon.</p>
        `
    }
];

// Skill nodes — techniques that emerge from combining core axes
// type: 'skill' (standalone) or 'hub' (contains subskills)
// subskills reference their hub via hubId
export const FUSION_SKILLS = [
    // === Skill 1: Initial Bluff Selection ===
    {
        id: 'initial-bluff',
        name: 'Initial Bluff Selection',
        parents: ['game-knowledge', 'deception'],
        tier: 2,
        type: 'skill',
        phases: ['pre-game'],
        description: 'The pre-game decision of what role to claim, made after drawing your token. You need to know the role list well enough to pick a convincing claim, and the deception chops to sell it.',
        article: `
            <h3>Evil — Minion Bluff Selection</h3>
            <p>A minion choosing their initial bluff weighs three axes:</p>

            <h4>Axis 1: Count Disruption</h4>
            <p>Can this bluff mess with the outsider count logic that good relies on? Claiming an outsider when outsider-modifying characters (e.g., Fang Gu) are on the script obscures the true count, making remainder logic harder for good to solve.</p>
            <p>A free outsider slot is low-risk — worst case, you back out later by claiming you were bluffing because you're actually a powerful role (e.g., Fortune Teller trying to hide) or a protection role (e.g., Soldier trying to bait a kill).</p>
            <p>The key risk is <strong>double-claiming</strong> a role that's actually in play, which leads to a 1-for-1 trade. In a 10-player game (7 town, 0 outsiders, 2 minion, 1 demon), going down to 6-0-1-1 makes every subsequent trade ratio bad for evil.</p>

            <h4>Axis 2: Information Pollution</h4>
            <p><strong>Active bluffs</strong> (e.g., Fortune Teller claiming two good players registered as demon) create false leads that pit good against good. This is the high-impact play.</p>
            <p><strong>Passive bluffs</strong> (e.g., Mayor) just give you cover — you're claiming you exist but not providing info that disrupts town's solving. Low risk, low reward.</p>
            <p>Evil's structural problem: good is slightly favored to win even with random guessing at most player counts. Evil cannot afford to play passive.</p>

            <h4>Axis 3: Survivability (Minion)</h4>
            <p>Minions should generally be willing to die on the sword in place of the demon. <strong>Loud minions</strong> (e.g., Boomdandy) may actively want to die. <strong>Quiet minions</strong> may want to stay alive to keep using their ability.</p>

            <h4>Additional Considerations</h4>
            <ul>
                <li>You may not coordinate with your demon immediately — if evil visibly huddles early, good can tag the group once one member is identified</li>
                <li>Calibrate vagueness: too specific too early risks double-claims; too cagey and you get called out as bluffless (a common beginner tell)</li>
                <li>Spin a personal narrative for <em>why</em> you're playing the way you are</li>
                <li>Make it hard for good to determine which demon/minions are in play</li>
            </ul>

            <h3>Evil — Demon Bluff Selection</h3>
            <p>The demon faces the same two axes plus <strong>survivability</strong>: can you die without losing?</p>
            <p>If you have a safety net (Scarlet Woman, or you are Imp/Fang Gu/Zombuul), you can afford riskier bluffs. If not, every role type creates tension:</p>
            <ul>
                <li><strong>Recurring info role:</strong> Town doesn't want you to die, but suspicious if you keep surviving night kills</li>
                <li><strong>Protection role:</strong> Self-protection (e.g., Soldier) can explain surviving, but it's suspicious if kills occur and your protection never procs. Protecting others (e.g., Monk) has the same issue — if people keep dying on your watch, your claim weakens</li>
                <li><strong>Start-of-game role:</strong> Low execution cost — your "ability" is already used</li>
                <li><strong>Once-per-game role:</strong> After your ability fires, town has less reason to keep you alive</li>
            </ul>
            <p>The demon generally wants to <strong>ingratiate themselves with town</strong> — appear valuable enough to keep alive, but not so powerful that surviving becomes its own red flag.</p>

            <h3>Good — Townsfolk Role Presentation</h3>
            <p>Good-side "bluffing" is about <strong>controlling what evil knows about you</strong>. The core tradeoff: hiding too much can hurt your own team's ability to solve.</p>
            <p>By ability timing:</p>
            <ul>
                <li><strong>Start-of-game info</strong> (Investigator, Librarian): Revealing early tells evil who you pinged — they may kill those players</li>
                <li><strong>Recurring info</strong> (Fortune Teller, Empath): High-value kill target. Obscure this role to keep your info stream alive</li>
                <li><strong>Self-protection roles</strong> (Soldier): Can claim something juicier to bait a wasted kill — e.g., claim Fortune Teller as Soldier, evil wastes a night kill and you don't die</li>
                <li><strong>Other-protection roles</strong> (Monk): Hiding your role lets you protect key players without evil knowing who to target around you</li>
                <li><strong>First-night-only roles:</strong> Don't reveal early so evil "wastes" a kill into you</li>
            </ul>

            <h3>Good — Outsider Role Presentation</h3>
            <p>Outsiders have two axes: <strong>hidden vs. public</strong> and <strong>want to die vs. want to survive</strong>.</p>
            <ul>
                <li><strong>Want to stay hidden</strong> (Mutant, Damsel, Plague Doctor): Revealing is dangerous</li>
                <li><strong>Want to be public</strong> (Recluse, Saint): Being known serves your ability</li>
                <li><strong>Want to die</strong> (Saint in certain contexts): Bluff to invite execution</li>
                <li><strong>Want to survive</strong> (Plague Doctor, Damsel): Bluff to stay off the radar</li>
            </ul>
        `
    },

    // === Hub: Determining Other Players' Roles ===
    {
        id: 'role-determination',
        name: 'Determining Roles',
        parents: ['logic', 'game-knowledge', 'social-insight'],
        tier: 3,
        type: 'hub',
        phases: ['day-1', 'every-day'],
        description: 'Reading the board — figuring out what roles are in play, what information exists, and who holds what. Good maps the board to execute the demon. Evil maps it to counter.',
        article: `
            <p>Determining other players' roles is the central information-gathering challenge of BotC. Good's goal is to map the board accurately enough to identify and execute the demon before running out of executions. Evil's goal is to understand what good knows so they can spin counter-narratives and target kills effectively.</p>
            <p>This breaks down into three skills: <strong>Info Gathering</strong> - the tools for extracting information and when to use them. <strong>Reaction Reading</strong> - what social tells reveal. <strong>Evil Board Reading</strong> - reverse-engineering what good knows.</p>
        `
    },
    {
        id: 'info-gathering',
        name: 'Info Gathering',
        parents: ['game-knowledge', 'logic'],
        tier: 2,
        type: 'subskill',
        hubId: 'role-determination',
        phases: ['day-1', 'every-day', '2nd-to-last-day'],
        description: 'The tools for extracting role information and the timing of when to use them.',
        article: `
            <h3>The Tools</h3>
            <p>There are several mechanical tools for extracting role information. Each has a different commitment level and risk profile:</p>
            <ul>
                <li><strong>3-for-3s:</strong> Trade 3 possible roles with another player - your real role is most likely one of them. Lower commitment, good for early game. Gives directional info without full exposure.</li>
                <li><strong>Hard claims:</strong> 1-for-1 role trade. Higher commitment, builds stronger trust but reveals more to anyone listening (including evil).</li>
                <li><strong>Partial reveals:</strong> Indicate above/below your role on the character sheet, or just confirm townsfolk vs. outsider. Minimal exposure.</li>
                <li><strong>False claims to force honesty:</strong> E.g., claim Dreamer info on a player (saying they registered as one of two roles) to pressure them into a hard claim. Uses deception in service of information gathering.</li>
            </ul>

            <h3>Timing</h3>
            <p>When to push for information is as important as how. Push too late and there's too much info to unpack at the end - evil's misinformation hits harder when there's no time to verify, and everyone's social credit is low from lying all game. Push too early and you give evil free targeting data for night kills, and evil can adapt their bluffs to avoid contradictions with what you've revealed.</p>
            <p>Sometimes you can't wait for the optimal moment. If evil is pushing a narrative against you, you may need to prove your good points before you die rather than waiting.</p>

            <h3>Good - Gathering to Solve</h3>
            <p>As good, the goal is to build an accurate picture of the board while controlling how much evil learns about you. How much of town should know your role depends on what you are - if everyone knows you're the Fortune Teller, evil knows exactly who to kill or poison. Too private and you can't build trust or coordinate with your team.</p>

            <h3>Evil - Performing the Gathering</h3>
            <p>As evil, you use the same tools but for different reasons. You need to look like you're solving the game the way you normally would as good - if you typically do 3-for-3s early, you should do them as evil too. Your behavior needs to match your baseline or observant players will notice the inconsistency. The tools also serve you directly: 3-for-3s that include your bluff among plausible options build your cover, and gathering info about what roles are actually in play lets you avoid double-claims, target night kills better, and set up a player to be framed later.</p>
        `
    },
    {
        id: 'reaction-reading',
        name: 'Reaction Reading',
        parents: ['social-insight'],
        tier: 2,
        type: 'subskill',
        hubId: 'role-determination',
        phases: ['day-1', 'every-day', '2nd-to-last-day', 'final-day'],
        description: 'Reading how people respond when pushed, called out, or asked to claim. Highest value against players you have a behavioral baseline for.',
        article: `
            <h3>Reading Reactions</h3>
            <p>Small tells matter in BotC. How a player responds when pushed, called out, or asked to claim can reveal information that logic alone can't provide.</p>
            <p>A player who is flabbergasted when called out for being evil may be genuinely surprised (good) or performing (evil). Distinguishing between the two requires a <strong>behavioral baseline</strong> — which is why this skill is most valuable when playing with a consistent group.</p>

            <h4>When to Trust Social Reads</h4>
            <ul>
                <li><strong>High value:</strong> Against players you've played with before and have a baseline for</li>
                <li><strong>Medium value:</strong> Against new players who haven't learned to mask tells yet</li>
                <li><strong>Dangerous:</strong> Against strangers or skilled veterans who can perform convincingly</li>
            </ul>

            <h4>The Danger</h4>
            <p>Reaction reading is powerful but must be cross-referenced with logic. Evil can deliberately manufacture reactions - a minion acting "caught" to bait execution, a demon acting resigned to mimic a sacrificing minion.</p>
        `
    },
    {
        id: 'evil-board-reading',
        name: 'Evil Board Reading',
        parents: ['logic', 'game-knowledge', 'social-insight'],
        tier: 3,
        type: 'subskill',
        hubId: 'role-determination',
        phases: ['day-1', 'every-day', '2nd-to-last-day', 'final-day'],
        description: 'Figuring out what good knows, who to kill, who to frame - and being able to argue a convincing evil team that protects your demon.',
        article: `
            <h3>Evil Board Reading</h3>
            <p>Evil already knows who their teammates are. The challenge is figuring out what <strong>good</strong> knows — and what good <em>is</em>.</p>

            <h4>Why Evil Needs to Read the Board</h4>
            <ul>
                <li><strong>What info does good have?</strong> So you can spin counter-narratives consistent with (or strategically contradicting) their information</li>
                <li><strong>Who to kill at night:</strong> Target high-value info roles, protect evil teammates from being exposed</li>
                <li><strong>Who to frame:</strong> Set up good players as suspects for the late game</li>
                <li><strong>Double-claim decisions:</strong> If you have more social credit than the real role-holder, you can double-claim and win the credibility fight</li>
            </ul>

            <h4>The Evil Litmus Test</h4>
            <p>If someone asked you "who is the evil team?" at any point in the game, you should have an answer. If you can't, you're going to have a tough time convincing others to your side. That answer needs to make a convincing case that your demon isn't the demon - ideally with a logical story for why those players are evil that fits the information town has seen.</p>
        `
    },

    // === Execution Politics ===
    {
        id: 'voting-blocks',
        name: 'Execution Politics',
        parents: ['logic', 'social-insight', 'persuasion'],
        tier: 3,
        type: 'hub',
        phases: ['day-1', 'every-day', '2nd-to-last-day', 'final-day'],
        description: 'Votes are the mechanism that actually wins and loses games. Everything else - logic, worlds, reads, credibility - only matters if it translates into the right execution.',
        article: `
            <p>Votes are the mechanism that actually wins and loses games in Blood on the Clocktower. You can solve the game perfectly, build the right world, and read every player correctly - but if you can't translate that into the right execution, none of it matters. Conversely, evil can be outplayed on every other axis and still win if they control enough votes at the right moment.</p>
            <p>Execution Politics breaks down into three skills: <strong>Vote Math</strong> - the structural numbers behind voting power. <strong>Voting Tells</strong> - what you can infer from how people vote. <strong>Coalition Building</strong> - getting people aligned to vote with you.</p>
        `
    },
    {
        id: 'vote-math',
        name: 'Vote Math',
        parents: ['logic'],
        tier: 2,
        type: 'subskill',
        hubId: 'voting-blocks',
        phases: ['day-1', 'every-day', '2nd-to-last-day', 'final-day'],
        description: 'The structural numbers behind voting power - block sizes, dead votes, and the thresholds that determine when each team has already won or lost.',
        article: `
            <p>The number of evil players scales with game size: 2 evil (1 demon + 1 minion) at 7-9 players, 3 evil (1 demon + 2 minions) at 10-14, and 4 evil (1 demon + 3 minions) at 15+. Evil votes together with full information. Good is fragmented - they don't know who's on their team.</p>

            <h3>How the Game Shrinks</h3>
            <p>Each full day/night cycle removes roughly 2 players - one to execution, one to the demon's night kill. The game ends at final 3, where there's one last execution. If good doesn't execute the demon on that final vote, evil wins.</p>
            <p>In a 10-player game with 3 evil: good gets about 4 executions across the game. They need to hit the demon with one of them. Every missed execution is a wasted vote, and the evil-to-alive ratio gets worse each round. By the time you're at 5 alive with 3 evil still standing, evil controls 60% of the living votes - good needs dead votes just to have a chance at pushing an execution through.</p>

            <h3>When to Worry</h3>
            <p>The critical question at any point in the game is: how many evil players have we actually eliminated? The more evil still alive relative to the total, the harder it is to push the right execution. In a 10-player game, if no evil has died by the time you're at 5 alive, evil has a 3-to-2 living advantage. In a 7-player game with 2 evil, the math is more forgiving but the margin for error is thinner - fewer total executions to work with.</p>

            <h3>Dead Vote Economy</h3>
            <p>Dead players get one vote to use for the rest of the game. The typical recommendation is to save dead votes for the final day, when they matter most. But if you're unsure whether any evil has been eliminated near the final 5 or final 6 - or even final 8 and below in larger games with more evil players - there are arguments to spend a good dead vote early to swing a vote against evil's coordinated block. If evil's living votes already outnumber good's, waiting for the final day may be too late.</p>
            <p>Evil can use the same logic. Dead minion votes can be spent early to protect the demon when good is trying to push an execution through.</p>
        `
    },
    {
        id: 'voting-tells',
        name: 'Voting Tells',
        parents: ['logic', 'social-insight'],
        tier: 2,
        type: 'subskill',
        hubId: 'voting-blocks',
        phases: ['day-1', 'every-day', '2nd-to-last-day', 'final-day'],
        description: 'What you can infer from how people vote - pure observation, not action.',
        article: `
            <p>Votes aren't just decisions - they're data. Every nomination and vote count tells you something about who is aligned with whom.</p>

            <h3>What Good Can Read</h3>
            <p>A nomination that gets overwhelming votes early (e.g., 9/10) likely means the target is non-demon - evil piled on to look aligned with town. When a player has votes stacking up and then a new nomination pulls those votes onto someone else, that lift is a tell - watch who nominated and who shifted. Late in the game, if you can't get someone executed, evil is likely a large portion of who's left and is actively blocking.</p>

            <h3>What Evil Can Read and Obscure</h3>
            <p>Watch for good players building consensus around the demon. If you see alignment forming, that's your signal to redirect attention elsewhere. But reading is only half of it - high-performing evil players deliberately create noise in the voting data. They nominate each other, vote against each other, and avoid patterns that reveal the underlying coalition. If evil always protects the same players and always votes together, the voting tells become too easy for good to read. The best evil teams make their voting behavior indistinguishable from fragmented good players who simply disagree.</p>
        `
    },

    // === Hub: World Building ===
    {
        id: 'world-building',
        name: 'World Building',
        parents: ['logic', 'game-knowledge', 'deception', 'persuasion'],
        tier: 4,
        type: 'hub',
        phases: ['day-1', 'every-day', '2nd-to-last-day', 'final-day'],
        description: 'Constructing, testing, and advocating for theories about the game state. Good builds worlds to find truth. Evil builds false worlds to sell as truth.',
        article: `
            <p>A "world" is a complete hypothesis about the game state: <em>"If X is the demon, Y is the drunk, and Z is the poisoner, then these pieces of info are true and these are false - does that hold up?"</em> Good builds worlds to find truth. Evil builds false worlds to sell as truth.</p>
            <p>This breaks down into three skills: <strong>World Elimination</strong> - narrowing which evil teams are possible. <strong>World Testing</strong> - checking specific hypotheses against available info. <strong>World Selling</strong> - evil's offensive skill of constructing and pushing convincing false narratives.</p>
        `
    },
    {
        id: 'world-elimination',
        name: 'World Elimination',
        parents: ['logic', 'game-knowledge'],
        tier: 2,
        type: 'subskill',
        hubId: 'world-building',
        phases: ['day-1', 'every-day', '2nd-to-last-day'],
        description: 'Narrowing which evil team compositions are possible based on kill patterns, storyteller announcements, ability triggers, and role count math.',
        article: `
            <h3>How World Elimination Works</h3>
            <p>The game's mechanics leak information that constrains the possible evil teams. World elimination is the process of ruling out impossible compositions before you start testing specific hypotheses.</p>

            <h4>Mechanical Evidence</h4>
            <ul>
                <li><strong>Kill patterns:</strong> Only 1 kill per night → probably not a Shabaloth (who kills 2).</li>
                <li><strong>Announcements:</strong> No Fearmonger announcement even though Fearmonger is on the script → Fearmonger is probably not in play, which increases odds of other minions (e.g., Poisoner).</li>
                <li><strong>Ability triggers:</strong> If a role's expected effect doesn't happen, either it's not in play or someone is drunk/poisoned.</li>
                <li><strong>Role count math:</strong> Known outsider/minion counts constrain which modifying roles are in play (e.g., Baron adds outsiders).</li>
            </ul>

            <h4>For Evil</h4>
            <p>Be aware of what good can eliminate — selling a world that contradicts observable mechanics puts you at odds with the players who noticed. But it doesn't always matter. If your coalition is large enough, you can win the vote even with a world that some players have ruled out. The question is whether the players with the mechanical evidence can convince enough others before you do.</p>
        `
    },
    {
        id: 'world-testing',
        name: 'World Testing',
        parents: ['logic', 'game-knowledge'],
        tier: 2,
        type: 'subskill',
        hubId: 'world-building',
        phases: ['every-day', '2nd-to-last-day', 'final-day'],
        description: 'Taking a specific hypothesis and checking whether all available information is consistent with it. Assume one thing is true and trace its implications.',
        article: `
            <h3>How World Testing Works</h3>
            <p>You assume one thing is true and trace its implications through all available information:</p>
            <ul>
                <li><em>"Marlie has an Empath reading of 0 with Lissie next to her. If Marlie is the sober Empath, we should trust Lissie."</em></li>
                <li><em>"If Ross is the Drunk, then his info is unreliable. Does everyone else's info make sense without his?"</em></li>
                <li><em>"If the Poisoner is in play (from world elimination), who was poisoned on which night? Does that resolve the conflicting info?"</em></li>
            </ul>
            <p>Each test either holds up (possible world) or creates contradictions (eliminated world). The goal is to narrow down to worlds where one explanation is clearly strongest.</p>

            <h4>The Challenge of Time</h4>
            <p>Good has limited days to test all plausible worlds, and evil is continuously adding noise. Many games are <strong>nondeterministic</strong> — there isn't enough info to fully solve, so you're often arguing for the most likely world rather than the proven one.</p>

            <h4>Evil's Counter</h4>
            <p>Know which worlds good is testing so you can reinforce the false ones and undermine the true one. If good is close to testing the correct world, redirect their attention toward a different hypothesis.</p>
        `
    },
    {
        id: 'world-selling',
        name: 'World Selling',
        parents: ['deception', 'persuasion', 'game-knowledge'],
        tier: 3,
        type: 'subskill',
        hubId: 'world-building',
        phases: ['every-day', '2nd-to-last-day', 'final-day'],
        description: 'Evil\'s core offensive skill: constructing and selling a coherent false world. Not just hiding, but actively making good second-guess correct deductions. Includes storyteller communication.',
        article: `
            <h3>Evil's Core Offensive Skill</h3>
            <p>Evil isn't just lying about their own role (that's Initial Bluff Selection). World selling is building a <strong>complete alternative narrative</strong> — who's drunk, who's poisoned, who the "real" evil team is — and making it logically consistent enough that good adopts it.</p>
            <p>Evil's job isn't to hide — it's to make good <strong>second-guess correct deductions</strong>. Good is already slightly favored to win at most player counts even with random guessing (see Win Rate Math). That means playing passively as evil is a losing strategy. Evil needs to actively muddy the waters so that good's structural advantage doesn't translate into finding the demon.</p>

            <h4>Coordinated World Selling</h4>
            <p>The whole evil team pushes one false world. Easier, cleaner, and the storyteller can reinforce it. When the demon communicates a clear narrative to the ST, the ST can use discretionary decisions (drunk/poisoned info, ability resolutions) to support that narrative.</p>
            <p>The ST wiki explicitly says to <em>"listen to the bluffs of the evil players and run your game accordingly."</em></p>

            <h4>Independent/Chaotic World Selling</h4>
            <p>Evil members push different theories, adding noise for good to dig through. Can include evil-on-evil conflict as a deliberate play — as long as the demon survives, executing a minion wastes good's executions. Works best when the demon has high social credibility.</p>

            <h4>The Storyteller Dynamic</h4>
            <ul>
                <li>The ST is neutral on who wins but supports whichever team is weaker</li>
                <li>The ST has discretionary decisions: what info a poisoned/drunk player receives, where to place the Innkeeper's drunk, etc.</li>
                <li>If evil gives the ST a clear, coherent plan, the ST can shape these decisions to support it — without breaking any rules</li>
                <li><strong>The catch:</strong> If evil is dominating, the ST starts tilting discretionary info toward good. A too-strong evil position triggers ST correction.</li>
            </ul>

            <h4>What Makes a False World Convincing</h4>
            <p>Ideally, a false world survives world elimination - it doesn't contradict observable mechanics. But this isn't strictly required. What matters is whether the players who can disprove your world can convince enough others before you lock in your coalition. A world that contradicts one player's info but aligns with five others' expectations can still win the vote.</p>
            <p>The strongest false worlds are consistent with info good already believes - good's default is to trust their own information, so building on that foundation is easier than fighting it. Drunk or poisoned players' false info can become "evidence" for your narrative. The main thing to avoid is creating contradictions that multiple players can independently verify - that turns scattered doubt into organized opposition.</p>
        `
    },

    // === Skill: Coalition Building ===
    {
        id: 'coalition-building',
        name: 'Coalition Building',
        parents: ['logic', 'persuasion', 'social-insight'],
        tier: 3,
        type: 'subskill',
        hubId: 'voting-blocks',
        phases: ['day-1', 'every-day', '2nd-to-last-day', 'final-day'],
        description: 'Aligning players to vote with you. Every execution is a coalition moment.',
        article: `
            <p>Every day requires a coalition for who to execute. Sometimes it's built on a full logical framework, sometimes a single data point, sometimes just a read. Coalition building is not a final-day skill - it's continuous from the first vote to the last. The narrative builds incrementally, and every early vote impacts the underlying voting power of each team going forward.</p>

            <p>Coalition building is <strong>preventative, not reactive</strong>. For both teams, the critical work happens before the decisive moment. If you haven't built social trust by the time you need to push a narrative, no amount of logic will save you. If good has already solidified a coalition against you as evil, no tactic will break it. You need X+1 votes to outvote evil with X people - and earning those votes starts long before the final day.</p>

            <p>The inputs shift as the game progresses. Early on, less has been revealed, so coalition building leans on social insight, vibes, and limited logic. As the game advances and more information surfaces, logic takes over as the primary driver. But at every stage, the fundamental challenge is the same: get enough people aligned to execute the right player.</p>

            <h3>Good - Getting the Team on the Correct Narrative</h3>
            <p>Good's coalition challenge is the counterpart to evil's World Selling. Even when you've identified the correct world, multiple headwinds work against you. Evil is actively counter-persuading in real time. Good players have competing theories based on their own info. Some of that info is wrong from drunk or poisoned players, and the game is often unsolved - so you're frequently arguing for the most likely world, not presenting proof.</p>

            <p>The primary driver for good is the strength of the logic. If the logic is airtight, good players will follow it regardless of who presents it. But when logic alone falls short, you need social trust already banked. If you've spent your credibility pushing hard all game, people may tune you out or turn against you at the moment it matters most. Sometimes you simply don't convince town, and that's the game.</p>

            <h3>Evil - Protecting the Demon Through Votes</h3>
            <p>Evil's coalition building is deeply intertwined with World Selling - the false world you construct IS what your coalition is built around. If good has already formed a coalition around a world where you're the evil candidate, it is very difficult to break that existing bond. Evil needs to build their coalition before good solidifies one.</p>

            <p>Evil has tactical tools to protect the demon. A minion can nominate a good player and pull votes away from the demon. Evil-on-evil conflict - a demon going after a minion - can look good-aligned and buy trust with town.</p>

            <p>But every tactic has a double edge. Sacrificing a minion buys credibility ("we found one evil!"), but you lose a frame target for later and reduce evil's voting power. Savvy players may read it as throwing the minion under the bus. And if the remaining evil players keep voting together after the sacrifice, the coordination becomes visible - so you've effectively lost more than one vote.</p>
        `
    },

    // === Skill: Social Credibility Management ===
    {
        id: 'social-credibility',
        name: 'Social Credibility',
        parents: ['persuasion', 'social-insight'],
        tier: 2,
        type: 'skill',
        phases: ['day-1', 'every-day', '2nd-to-last-day', 'final-day'],
        description: 'How believably good do you seem? The resource that determines whether anyone listens.',
        article: `
            <p>Social credibility is how believably good you seem to the rest of the town. It determines whether anyone listens when you speak, follows your reads, or votes with you. A player who's been right all game can push a final-day execution and get followed. A player who's been lying all game can have the correct answer and convince no one. The difference is credibility.</p>

            <p>Credibility fluctuates throughout the game like a bar - rising and falling based on your actions. It's mostly a passive byproduct of how you play rather than something you consciously optimize. Voting with the group, being right about past reads, presenting clear logic, and confirming other players' info all build it up. Pushing too hard for executions, leading too many votes, contradicting the group, and being wrong about past reads all spend it. Lie nonstop and you become the boy who cried wolf - no one believes you even when you finally have the truth.</p>

            <p>Social credibility sits at the intersection of Persuasion and Social Insight. Persuasion is what you spend credibility on - convincing others to act on your perspective. Social Insight is how you read where your credibility stands with different players and how to build it. Knowing who trusts you, who is skeptical, and who you've already lost is itself a social read. Without that awareness, you might spend credibility you don't have or fail to use it when you've built enough.</p>

            <h3>Evil's Credibility Advantage</h3>
            <p>Evil can coast on free credibility early in the game simply by agreeing with town, confirming others' reads, and acting good-aligned. These are easy deposits when you already know who the evil team is. The strategy is to bank credibility throughout the game and spend it on the final day - pushing a mislynch on a good player with the trust you've accumulated. Evil doesn't need to convince the whole town, just a couple of good players to vote their way. That's the goal: win enough people to your side to protect the demon when it counts.</p>
            <p>The danger is that credibility-building tactics can be read as exactly that. Savvy players may notice someone meta-gaming credibility - for example, voting out a minion to look trustworthy. And if you lead too many votes or push too hard too early, the credibility you're trying to build gets spent before it matters.</p>
        `
    },

    // === Hub: Win Rate Math ===
    {
        id: 'winrate-math',
        name: 'Win Rate Math',
        parents: ['game-knowledge'],
        tier: 2,
        type: 'hub',
        phases: ['pre-game'],
        description: 'The structural math behind win rates and Day 1 execution decisions. Understanding these baselines tells you what the game structure alone implies before abilities, reads, or social pressure enter the picture.',
        article: `
            <p>Before abilities, reads, or social pressure enter the picture, the game's structure alone implies certain win rates. Understanding these baselines tells you where each team starts and where the structural advantages lie.</p>

            <h3>Key Structural Findings</h3>
            <ul>
                <li><strong>Odd player counts favor Good;</strong> even counts favor Evil</li>
                <li>Good's baseline ranges from 49% to 62% - a 13-point swing from player count alone</li>
                <li>N=10 is the sweet spot for Evil; N=15 is the hardest for Evil</li>
                <li>Skipping Day 1 execution has massive and counterintuitive effects depending on odd/even count</li>
            </ul>
            <p>This breaks down into four sections: <strong>Good's Baseline Win Rate</strong>, <strong>Evil's Baseline Win Rate</strong>, <strong>Good Skipping Day 1</strong>, and <strong>Evil Skipping Day 1</strong>.</p>
        `
    },
    {
        id: 'good-baseline',
        name: "Good's Baseline Win Rate",
        parents: ['game-knowledge'],
        tier: 2,
        type: 'subskill',
        hubId: 'winrate-math',
        chartId: 'good-baseline',
        phases: ['pre-game'],
        description: 'Good\'s win probability by player count assuming completely random executions.',
        article: `
            <h3>Good's Structural Position</h3>
            <p>Good wins 49-62% of the time at baseline with completely random executions. Good is slightly favored at most player counts even before abilities enter the picture.</p>

            <h3>Odd vs. Even</h3>
            <p><strong>Odd player counts consistently favor Good</strong> because the extra townsfolk gives more room for error. At 9P, 11P, 13P, and 15P, good has 59-62% baseline - a strong structural cushion. At even counts, good dips to 49-54%, and at 10P specifically, good is mathematically unfavored at 49%.</p>

            <div class="collapsible-section">
                <button class="collapsible-header" onclick="this.parentElement.classList.toggle('open')">
                    <span class="collapsible-title">How the Model Works</span>
                    <span class="collapsible-arrow">&#9662;</span>
                </button>
                <div class="collapsible-body">
                    <p>The model uses a dynamic programming recursion that simulates the game turn by turn. Each day, a random player is executed. Each night, the demon kills a random non-demon player. The game ends when the demon is executed (good wins) or only 2 players remain (evil wins). The DP calculates the probability of good winning from every possible game state.</p>
                    <p><strong>Assumptions:</strong> Random execution, random demon kill, no abilities, no information. This isolates the structural effect of player count and team composition.</p>
                </div>
            </div>
        `
    },
    {
        id: 'evil-baseline',
        name: "Evil's Baseline Win Rate",
        parents: ['game-knowledge'],
        tier: 2,
        type: 'subskill',
        hubId: 'winrate-math',
        chartId: 'evil-baseline',
        phases: ['pre-game'],
        description: 'Evil\'s win probability by player count — the mirror of Good\'s baseline. Shows where the game structure favors Evil before any abilities or social play.',
        article: `
            <h3>Evil's Structural Position</h3>
            <p>The mirror of Good's baseline. N=10 is the <strong>only player count where evil is structurally favored</strong> at 51%. Even counts generally favor evil (46-51%), while odd counts are an uphill battle (38-46%).</p>

            <h3>What This Means for Evil Strategy</h3>
            <p>At odd counts, evil faces a significant structural disadvantage and must rely on strong social play, deception, and world selling to overcome it. At even counts - especially 10P - evil has the math on their side and should play to their structural advantage.</p>
        `
    },
    {
        id: 'good-skip-d1',
        name: 'Good Skipping Day 1',
        parents: ['game-knowledge'],
        tier: 2,
        type: 'subskill',
        hubId: 'winrate-math',
        chartId: 'good-skip-d1',
        phases: ['pre-game'],
        description: 'The math on whether Good should execute or skip on Day 1. The answer depends entirely on whether the player count is odd or even — and the swings are massive.',
        article: `
            <h3>Should Good Skip Day 1 Execution?</h3>
            <p>The answer depends entirely on whether the player count is odd or even — and the swings are massive.</p>

            <h4>At Even Counts: Consider Skipping</h4>
            <p>Skipping Day 1 gains Good <strong>+3 to +6 points</strong>. The mechanism: skipping converts even-sized execution rounds into odd-sized ones, improving per-round demon-hit odds.</p>
            <ul>
                <li>8P: 51% → 54% (+3 points)</li>
                <li>10P: 49% → 54% (+5 points) — <strong>flips the matchup from evil-favored to good-favored</strong></li>
                <li>12P: 54% → 59% (+5 points)</li>
                <li>14P: 53% → 59% (+6 points)</li>
            </ul>

            <h4>At Odd Counts: Always Execute</h4>
            <p>Skipping Day 1 costs Good <strong>8-11 points</strong> — devastating.</p>
            <ul>
                <li>9P: 59% → 51% (-8 points)</li>
                <li>11P: 59% → 49% (-10 points) — flips the matchup</li>
                <li>13P: 59% → 48% (-11 points) — the biggest swing</li>
                <li>15P: 62% → 53% (-9 points)</li>
            </ul>

            <h4>The Rule</h4>
            <p><strong>Execute at odd player counts. Consider skipping at even player counts.</strong> The math is clear and the swings are large enough to matter.</p>
        `
    },
    {
        id: 'evil-skip-d1',
        name: 'Evil Skipping Day 1',
        parents: ['game-knowledge'],
        tier: 2,
        type: 'subskill',
        hubId: 'winrate-math',
        chartId: 'evil-skip-d1',
        phases: ['pre-game'],
        description: 'How Good\'s Day 1 execution decision affects Evil\'s win rate. The mirror perspective — what Evil wants Good to do at each player count.',
        article: `
            <h3>How Day 1 Decisions Affect Evil</h3>
            <p>The mirror perspective — what evil wants good to do at each player count.</p>

            <h4>Evil Wants Good to Skip at Odd Counts</h4>
            <p>Evil gains <strong>8-11 points</strong> when good skips at odd counts:</p>
            <ul>
                <li>9P: 41% → 49% (+8 points)</li>
                <li>11P: 41% → 51% (+10 points) — flips the matchup to evil-favored</li>
                <li>13P: 41% → 52% (+11 points)</li>
                <li>15P: 38% → 47% (+9 points)</li>
            </ul>

            <h4>Evil Wants Good to Execute at Even Counts</h4>
            <p>Evil loses <strong>3-6 points</strong> when good skips at even counts:</p>
            <ul>
                <li>8P: 49% → 46% (-3 points)</li>
                <li>10P: 51% → 46% (-5 points) — loses evil's only structural edge</li>
                <li>12P: 46% → 41% (-5 points)</li>
                <li>14P: 47% → 41% (-6 points)</li>
            </ul>

            <h4>Strategic Implication</h4>
            <p>Evil should <strong>push for no execution at odd counts</strong> and <strong>push for execution at even counts</strong>. This can be subtle — arguing that "we don't have enough info to execute safely on Day 1" at a 9-player game is mathematically advantageous for evil even though it sounds reasonable.</p>
        `
    }
];
