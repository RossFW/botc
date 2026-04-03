# Blood on the Clocktower Stats & Strategy

A web app for tracking ELO ratings, game analytics, and strategy for Blood on the Clocktower.

## Structure

```
botc/
├── botc-web/                    (Main website)
│   ├── index.html               (Leaderboard — ELO rankings)
│   ├── analytics.html           (Analytics — scripts, characters, players, head-to-head)
│   ├── strategy.html            (Strategy — skill tree + strategy articles)
│   ├── css/
│   │   ├── styles.css           (Shared base styles & CSS variables)
│   │   ├── analytics.css        (Analytics-specific styles)
│   │   ├── dimensions.css       (Skill tree & detail panel styles)
│   │   └── strategy.css         (Strategy article & filter styles)
│   └── js/
│       ├── app.js               (Leaderboard main)
│       ├── analyticsApp.js      (Analytics main)
│       ├── analytics.js         (Analytics data processing)
│       ├── skillTree.js         (Canvas-based skill tree)
│       ├── skills.js            (Skill data — core axes + fusion skills)
│       ├── strategy.js          (Strategy page filters + charts)
│       ├── supabase.js          (Supabase data layer)
│       ├── elo.js               (ELO calculations)
│       ├── gameEntry.js         (Game entry form)
│       ├── autocomplete.js      (Input autocomplete)
│       └── config.js            (Game configuration)
├── brainstorm/                  (Working docs — not deployed)
│   ├── fusions.md               (Skill fusion definitions)
│   └── INTERVIEW_PROMPT.md      (Brainstorming prompt)
└── README.md
```

## Running Locally

```bash
cd botc-web
python3 -m http.server 8000
```

Then open http://localhost:8000

## Data

All game data is stored in Supabase (PostgreSQL). No local data files needed.

## Pages

- **Leaderboard**: ELO rankings, game entry, player rating history
- **Analytics**: Win rates by script, character stats, player breakdowns, head-to-head matchups
- **Strategy**: Interactive skill mastery tree with 5 core axes (Logic, Game Knowledge, Deception, Persuasion, Social Insight) and strategy articles organized by game phase and alignment

## Color Accessibility

Good = Blue (#60a5fa), Evil = Orange (#f97316) — colorblind-friendly palette replacing the traditional green/red.
