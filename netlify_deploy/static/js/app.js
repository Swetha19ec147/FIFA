// Client-Side FIFA World Cup 2026 Predictor & Simulator Engine
// Completely serverless Jamstack Architecture.

// Global State
let teams = [];
let activeTab = 'predictor';
let activeSubTab = 'events';
let selectedHome = '';
let selectedAway = '';

// World Cup Tournament State
let tourneyView = 'groups'; // 'groups' or 'bracket'
let currentGroup = 'Group A';
let groupStandings = {}; // groupName -> list of team objects
let groupFixtures = {}; // groupName -> list of match objects
let groupsSimulatedCount = 0; // count of simulated groups

// Knockout Bracket State
let knockoutRounds = {
    r32: [], // 16 matches
    r16: [], // 8 matches
    qf: [],  // 4 matches
    sf: [],  // 2 matches
    final: [] // 1 match
};
let tourneySimulated = false;

// Simulation State
let simTimer = null;
let simIsActive = false;
let simMinute = 0;
let simHome = '';
let simAway = '';
let simHomeElo = 1500;
let simAwayElo = 1500;
let simStats = {
    home_goals: 0,
    away_goals: 0,
    home_red_cards: 0,
    away_red_cards: 0,
    home_shots: 0,
    away_shots: 0,
    home_sot: 0,
    away_sot: 0,
    home_corners: 0,
    away_corners: 0,
    home_fouls: 0,
    away_fouls: 0,
    possession_home: 50,
    possession_away: 50
};
let activeBracketMatch = null; // Reference to match being simulated in bracket

// Live Tracker State
let activeTrackerMode = 'simulated';
let livePoller = null;
let liveFixtureId = null;
let liveHome = '';
let liveAway = '';

// Chart.js Instances
let liveChart = null;
let eloChart = null;

// Real-World API-Sports IDs for Official International Crests
const TEAM_IDS = {
    'Argentina': 26, 'France': 2, 'Spain': 9, 'England': 10,
    'Brazil': 6, 'Portugal': 27, 'Netherlands': 11, 'Italy': 28,
    'Germany': 25, 'Colombia': 29, 'Uruguay': 30, 'Croatia': 3,
    'Belgium': 1, 'Morocco': 31, 'Denmark': 21, 'Japan': 12,
    'Switzerland': 13, 'Senegal': 14, 'USA': 32, 'Sweden': 15,
    'Ukraine': 16, 'Austria': 17, 'Mexico': 33, 'Ecuador': 34,
    'Turkey': 18, 'Poland': 24, 'Australia': 19, 'Hungary': 20,
    'Canada': 35, 'South Korea': 22, 'Chile': 36, 'Nigeria': 37,
    'Czechia': 23, 'Algeria': 38, 'Ivory Coast': 39, 'Scotland': 100,
    'Cameroon': 40, 'Iran': 41, 'Egypt': 42, 'Peru': 43,
    'Ghana': 44, 'Paraguay': 45, 'Wales': 101, 'Venezuela': 46,
    'Tunisia': 47, 'Saudi Arabia': 48, 'Qatar': 49, 'Iraq': 50
};

// Real-World Kit Color Palette for Jerseys
const TEAM_COLORS = {
    'Argentina': { primary: '#75AADB', secondary: '#FFFFFF' },
    'France': { primary: '#002395', secondary: '#FF0000' },
    'Spain': { primary: '#C60B1E', secondary: '#FBE116' },
    'England': { primary: '#FFFFFF', secondary: '#000033' },
    'Brazil': { primary: '#FFDF00', secondary: '#009B3A' },
    'Portugal': { primary: '#E42518', secondary: '#046A38' },
    'Netherlands': { primary: '#FF4F00', secondary: '#FFFFFF' },
    'Italy': { primary: '#002F6C', secondary: '#FFFFFF' },
    'Germany': { primary: '#FFFFFF', secondary: '#000000' },
    'Colombia': { primary: '#FCD116', secondary: '#003893' },
    'Uruguay': { primary: '#0081C6', secondary: '#FFFFFF' },
    'Croatia': { primary: '#FF0000', secondary: '#FFFFFF' },
    'Morocco': { primary: '#C1272D', secondary: '#006233' },
    'Japan': { primary: '#000080', secondary: '#FFFFFF' },
    'Senegal': { primary: '#FFFFFF', secondary: '#00853F' },
    'USA': { primary: '#0A2240', secondary: '#E0162B' },
    'Mexico': { primary: '#006341', secondary: '#FFFFFF' },
    'Canada': { primary: '#FF0000', secondary: '#FFFFFF' },
    'default': { primary: '#10B981', secondary: '#1E293B' }
};

// Helper: Factorial
function factorial(n) {
    let res = 1;
    for (let i = 2; i <= n; i++) res *= i;
    return res;
}

// Helper: Poisson probability density function
function poissonProb(k, lamb) {
    if (lamb <= 0) return k === 0 ? 1.0 : 0.0;
    return Math.pow(lamb, k) * Math.exp(-lamb) / factorial(k);
}

// ----------------------------------------------------
// AI Predictor Engine (Random Forest & Poisson)
// ----------------------------------------------------

function getTeamFormFeatures(homeTeam, awayTeam) {
    let h_pts = 1.0, h_gf = 1.0, h_ga = 1.0;
    let a_pts = 1.0, a_gf = 1.0, a_ga = 1.0;

    const hHistory = MODEL_DATA.team_history[homeTeam] || [];
    if (hHistory.length > 0) {
        const lastN = hHistory.slice(-5);
        h_pts = lastN.reduce((sum, x) => sum + x[0], 0) / lastN.length;
        h_gf = lastN.reduce((sum, x) => sum + x[1], 0) / lastN.length;
        h_ga = lastN.reduce((sum, x) => sum + x[2], 0) / lastN.length;
    }

    const aHistory = MODEL_DATA.team_history[awayTeam] || [];
    if (aHistory.length > 0) {
        const lastN = aHistory.slice(-5);
        a_pts = lastN.reduce((sum, x) => sum + x[0], 0) / lastN.length;
        a_gf = lastN.reduce((sum, x) => sum + x[1], 0) / lastN.length;
        a_ga = lastN.reduce((sum, x) => sum + x[2], 0) / lastN.length;
    }

    const sortedTeams = [homeTeam, awayTeam].sort();
    const key = `${sortedTeams[0]}__${sortedTeams[1]}`;
    const pastMatches = MODEL_DATA.h2h_history[key] || [];
    let h2h_diff = 0.0;
    if (pastMatches.length > 0) {
        const last3 = pastMatches.slice(-3);
        let netGds = [];
        for (const match of last3) {
            if (match.home === homeTeam) {
                netGds.push(match.home_goals - match.away_goals);
            } else {
                netGds.push(match.away_goals - match.home_goals);
            }
        }
        h2h_diff = netGds.reduce((sum, x) => sum + x, 0) / netGds.length;
    }

    return { h_pts, h_gf, h_ga, a_pts, a_gf, a_ga, h2h_diff };
}

function predictTree(nodes, features) {
    let nodeIdx = 0;
    while (true) {
        const node = nodes[nodeIdx];
        if (node.left === -1) {
            return node.value;
        }
        const val = features[node.feature];
        if (val <= node.threshold) {
            nodeIdx = node.left;
        } else {
            nodeIdx = node.right;
        }
    }
}

function predictRF(forest, features) {
    const sum = [0.0, 0.0, 0.0];
    for (const nodes of forest) {
        const val = predictTree(nodes, features);
        sum[0] += val[0]; // Away
        sum[1] += val[1]; // Draw
        sum[2] += val[2]; // Home
    }
    const total = sum[0] + sum[1] + sum[2];
    return [sum[0] / total, sum[1] / total, sum[2] / total];
}

function predictPreMatch(homeTeam, awayTeam) {
    const homeElo = MODEL_DATA.current_elos[homeTeam] || 1500.0;
    const awayElo = MODEL_DATA.current_elos[awayTeam] || 1500.0;
    const eloDiff = homeElo + 90.0 - awayElo;

    const form = getTeamFormFeatures(homeTeam, awayTeam);

    const features = [
        eloDiff,
        form.h_pts, form.a_pts,
        form.h_gf, form.a_gf,
        form.h_ga, form.a_ga,
        form.h2h_diff
    ];

    const rfProbs = predictRF(MODEL_DATA.forest, features); // [Away, Draw, Home]
    const pAwayClf = rfProbs[0];
    const pDrawClf = rfProbs[1];
    const pHomeClf = rfProbs[2];

    const hStrength = MODEL_DATA.strengths[homeTeam] || { att_home: 1.0, def_home: 1.0 };
    const aStrength = MODEL_DATA.strengths[awayTeam] || { att_away: 1.0, def_away: 1.0 };

    let lambdaHome = hStrength.att_home * aStrength.def_away * MODEL_DATA.avg_hg;
    let muAway = aStrength.att_away * hStrength.def_home * MODEL_DATA.avg_ag;

    const eloFactor = eloDiff / 400.0;
    lambdaHome *= (1.0 + 0.20 * eloFactor);
    muAway *= (1.0 - 0.20 * eloFactor);

    lambdaHome = Math.max(0.1, Math.min(4.0, lambdaHome));
    muAway = Math.max(0.1, Math.min(4.0, muAway));

    const maxGoals = 8;
    const scoreGrid = Array.from({ length: maxGoals }, () => new Float64Array(maxGoals));
    let gridSum = 0.0;

    for (let h = 0; h < maxGoals; h++) {
        for (let a = 0; a < maxGoals; a++) {
            const prob = poissonProb(h, lambdaHome) * poissonProb(a, muAway);
            scoreGrid[h][a] = prob;
            gridSum += prob;
        }
    }

    if (gridSum > 0) {
        for (let h = 0; h < maxGoals; h++) {
            for (let a = 0; a < maxGoals; a++) {
                scoreGrid[h][a] /= gridSum;
            }
        }
    }

    let pHomeWinPoisson = 0.0;
    let pDrawPoisson = 0.0;
    let pAwayWinPoisson = 0.0;

    for (let h = 0; h < maxGoals; h++) {
        for (let a = 0; a < maxGoals; a++) {
            if (h > a) pHomeWinPoisson += scoreGrid[h][a];
            else if (h < a) pAwayWinPoisson += scoreGrid[h][a];
            else pDrawPoisson += scoreGrid[h][a];
        }
    }

    let pAway = 0.5 * pAwayClf + 0.5 * pAwayWinPoisson;
    let pDraw = 0.5 * pDrawClf + 0.5 * pDrawPoisson;
    let pHome = 0.5 * pHomeClf + 0.5 * pHomeWinPoisson;

    const tot = pHome + pDraw + pAway;
    pHome /= tot;
    pDraw /= tot;
    pAway /= tot;

    let maxVal = -1.0;
    let predictedHomeGoals = 0;
    let predictedAwayGoals = 0;
    for (let h = 0; h < maxGoals; h++) {
        for (let a = 0; a < maxGoals; a++) {
            if (scoreGrid[h][a] > maxVal) {
                maxVal = scoreGrid[h][a];
                predictedHomeGoals = h;
                predictedAwayGoals = a;
            }
        }
    }

    return {
        home_team: homeTeam,
        away_team: awayTeam,
        home_elo: homeElo,
        away_elo: awayElo,
        home_win_prob: pHome,
        draw_prob: pDraw,
        away_win_prob: pAway,
        expected_goals_home: lambdaHome,
        expected_goals_away: muAway,
        predicted_score: `${predictedHomeGoals}-${predictedAwayGoals}`,
        predicted_home_goals: predictedHomeGoals,
        predicted_away_goals: predictedAwayGoals,
        factors: {
            elo_diff: eloDiff,
            home_form_points: form.h_pts,
            away_form_points: form.a_pts,
            h2h_diff: form.h2h_diff
        }
    };
}

// ----------------------------------------------------
// FIFA World Cup Tournament Sim State Engine
// ----------------------------------------------------

function initTournament() {
    groupsSimulatedCount = 0;
    tourneySimulated = false;
    document.getElementById('btn-advance-knockout').disabled = true;
    
    // Initialize standings & schedule fixtures
    for (const groupName in MODEL_DATA.groups) {
        const groupTeams = MODEL_DATA.groups[groupName];
        groupStandings[groupName] = groupTeams.map(teamName => ({
            team: teamName,
            played: 0, won: 0, drawn: 0, lost: 0, gf: 0, ga: 0, gd: 0, points: 0, form: []
        }));
        
        // 6 fixtures per group round-robin
        groupFixtures[groupName] = [
            { id: `${groupName}_m1`, home: groupTeams[0], away: groupTeams[1], goals_home: null, goals_away: null, played: false },
            { id: `${groupName}_m2`, home: groupTeams[2], away: groupTeams[3], goals_home: null, goals_away: null, played: false },
            { id: `${groupName}_m3`, home: groupTeams[0], away: groupTeams[2], goals_home: null, goals_away: null, played: false },
            { id: `${groupName}_m4`, home: groupTeams[1], away: groupTeams[3], goals_home: null, goals_away: null, played: false },
            { id: `${groupName}_m5`, home: groupTeams[3], away: groupTeams[0], goals_home: null, goals_away: null, played: false },
            { id: `${groupName}_m6`, home: groupTeams[1], away: groupTeams[2], goals_home: null, goals_away: null, played: false }
        ];
    }
    
    renderGroupData();
    initTickerMatches();
}

function handleGroupChange(val) {
    currentGroup = val;
    renderGroupData();
}

function renderGroupData() {
    const standings = groupStandings[currentGroup];
    const fixtures = groupFixtures[currentGroup];
    
    // Render standings table
    const tbody = document.getElementById('group-standings-tbody');
    tbody.innerHTML = '';
    
    standings.forEach((row, idx) => {
        const tr = document.createElement('tr');
        if (idx < 2) tr.className = 'top-spot'; // Qualified
        
        const crest = getTeamCrestHTML(row.team);
        tr.innerHTML = `
            <td><strong>${idx + 1}</strong></td>
            <td><div style="display:flex; align-items:center;">${crest}<strong>${row.team}</strong></div></td>
            <td>${row.played}</td>
            <td>${row.won}</td>
            <td>${row.drawn}</td>
            <td>${row.lost}</td>
            <td>${row.gd > 0 ? '+' + row.gd : row.gd}</td>
            <td><strong>${row.points}</strong></td>
        `;
        tbody.appendChild(tr);
    });

    // Render fixtures list
    const container = document.getElementById('group-fixtures-container');
    container.innerHTML = '';
    
    fixtures.forEach(match => {
        const item = document.createElement('div');
        item.className = 'match-item';
        
        const homeCrest = getTeamCrestHTML(match.home);
        const awayCrest = getTeamCrestHTML(match.away);
        
        const scoreDisplay = match.played 
            ? `${match.goals_home} - ${match.goals_away}` 
            : `vs`;
            
        item.innerHTML = `
            <span class="match-team home">${homeCrest}${match.home}</span>
            <span class="match-score" style="cursor:pointer;" onclick="loadMatchToCenter('${match.home}', '${match.away}', '${match.id}')">${scoreDisplay}</span>
            <span class="match-team away">${match.away}${awayCrest}</span>
        `;
        container.appendChild(item);
    });
}

function loadMatchToCenter(home, away, matchId) {
    activeBracketMatch = matchId;
    selectFixture(home, away);
}

function simulateMatchInstance(home, away) {
    const pred = predictPreMatch(home, away);
    // Draw scores from Poisson lambda distributions
    let gh = 0, ga = 0;
    let pSum = 0;
    let r = Math.random();
    
    // Simulate scores using Poisson
    for (let h = 0; h < 8; h++) {
        for (let a = 0; a < 8; a++) {
            pSum += poissonProb(h, pred.expected_goals_home) * poissonProb(a, pred.expected_goals_away);
            if (r <= pSum) {
                gh = h;
                ga = a;
                return { gh, ga };
            }
        }
    }
    return { gh: Math.floor(pred.expected_goals_home), ga: Math.floor(pred.expected_goals_away) };
}

function updateStandingsRow(row, gf, ga, points, win, draw, loss) {
    row.played += 1;
    row.gf += gf;
    row.ga += ga;
    row.gd = row.gf - row.ga;
    row.points += points;
    if (win) { row.won += 1; row.form.push('W'); }
    else if (draw) { row.drawn += 1; row.form.push('D'); }
    else if (loss) { row.lost += 1; row.form.push('L'); }
}

function recalculateStandings(groupName) {
    const standings = groupStandings[groupName];
    const fixtures = groupFixtures[groupName];
    
    // Reset standings count
    standings.forEach(row => {
        row.played = 0; row.won = 0; row.drawn = 0; row.lost = 0;
        row.gf = 0; row.ga = 0; row.gd = 0; row.points = 0; row.form = [];
    });
    
    fixtures.forEach(f => {
        if (!f.played) return;
        const hRow = standings.find(r => r.team === f.home);
        const aRow = standings.find(r => r.team === f.away);
        
        if (f.goals_home > f.goals_away) {
            updateStandingsRow(hRow, f.goals_home, f.goals_away, 3, true, false, false);
            updateStandingsRow(aRow, f.goals_away, f.goals_home, 0, false, false, true);
        } else if (f.goals_home < f.goals_away) {
            updateStandingsRow(hRow, f.goals_home, f.goals_away, 0, false, false, true);
            updateStandingsRow(aRow, f.goals_away, f.goals_home, 3, true, false, false);
        } else {
            updateStandingsRow(hRow, f.goals_home, f.goals_away, 1, false, true, false);
            updateStandingsRow(aRow, f.goals_away, f.goals_home, 1, false, true, false);
        }
    });
    
    // Sort Standings: Pts DESC, GD DESC, GF DESC, alphabetically ASC
    standings.sort((a, b) => {
        if (b.points !== a.points) return b.points - a.points;
        if (b.gd !== a.gd) return b.gd - a.gd;
        if (b.gf !== a.gf) return b.gf - a.gf;
        return a.team.localeCompare(b.team);
    });
}

function simulateSelectedGroup() {
    const fixtures = groupFixtures[currentGroup];
    fixtures.forEach(match => {
        if (match.played) return;
        const score = simulateMatchInstance(match.home, match.away);
        match.goals_home = score.gh;
        match.goals_away = score.ga;
        match.played = true;
    });
    recalculateStandings(currentGroup);
    renderGroupData();
    checkAllGroupsSimulated();
}

function simulateAllGroups() {
    for (const groupName in MODEL_DATA.groups) {
        const fixtures = groupFixtures[groupName];
        fixtures.forEach(match => {
            if (match.played) return;
            const score = simulateMatchInstance(match.home, match.away);
            match.goals_home = score.gh;
            match.goals_away = score.ga;
            match.played = true;
        });
        recalculateStandings(groupName);
    }
    renderGroupData();
    checkAllGroupsSimulated();
}

function checkAllGroupsSimulated() {
    let allDone = true;
    for (const groupName in groupFixtures) {
        if (groupFixtures[groupName].some(f => !f.played)) {
            allDone = false;
        }
    }
    if (allDone) {
        document.getElementById('btn-advance-knockout').disabled = false;
        document.getElementById('btn-advance-knockout').classList.add('pulse-glow');
    }
}

function advanceToKnockouts() {
    // 1. Collect qualifiers (top 2 from each of the 12 groups = 24 teams)
    const qualifiers = [];
    const thirdPlaces = [];
    
    for (const groupName in groupStandings) {
        const standings = groupStandings[groupName];
        qualifiers.push(standings[0].team); // winner
        qualifiers.push(standings[1].team); // runner up
        thirdPlaces.push(standings[2]);     // third place
    }
    
    // 2. Determine 8 best third-placed teams
    thirdPlaces.sort((a, b) => {
        if (b.points !== a.points) return b.points - a.points;
        if (b.gd !== a.gd) return b.gd - a.gd;
        if (b.gf !== a.gf) return b.gf - a.gf;
        return a.team.localeCompare(b.team);
    });
    
    const bestThirds = thirdPlaces.slice(0, 8).map(x => x.team);
    
    // 3. Seed the Round of 32
    // Seeding matches: winners of groups A-L + runners up A-L + 8 best thirds.
    const roundOf32Matches = [];
    
    const seedMapping = [
        { home: groupStandings["Group A"][0].team, away: bestThirds[0] }, // Winner A vs 3rd_1
        { home: groupStandings["Group B"][1].team, away: groupStandings["Group C"][1].team }, // Runner B vs Runner C
        { home: groupStandings["Group C"][0].team, away: bestThirds[1] }, // Winner C vs 3rd_2
        { home: groupStandings["Group D"][1].team, away: groupStandings["Group E"][1].team }, // Runner D vs Runner E
        { home: groupStandings["Group E"][0].team, away: bestThirds[2] }, // Winner E vs 3rd_3
        { home: groupStandings["Group F"][1].team, away: groupStandings["Group G"][1].team }, // Runner F vs Runner G
        { home: groupStandings["Group G"][0].team, away: bestThirds[3] }, // Winner G vs 3rd_4
        { home: groupStandings["Group H"][1].team, away: groupStandings["Group I"][1].team }, // Runner H vs Runner I
        { home: groupStandings["Group I"][0].team, away: bestThirds[4] }, // Winner I vs 3rd_5
        { home: groupStandings["Group J"][1].team, away: groupStandings["Group K"][1].team }, // Runner J vs Runner K
        { home: groupStandings["Group K"][0].team, away: bestThirds[5] }, // Winner K vs 3rd_6
        { home: groupStandings["Group L"][1].team, away: groupStandings["Group A"][1].team }, // Runner L vs Runner A
        { home: groupStandings["Group B"][0].team, away: bestThirds[6] }, // Winner B vs 3rd_7
        { home: groupStandings["Group D"][0].team, away: bestThirds[7] }, // Winner D vs 3rd_8
        { home: groupStandings["Group F"][0].team, away: groupStandings["Group H"][0].team }, // Winner F vs Winner H
        { home: groupStandings["Group J"][0].team, away: groupStandings["Group L"][0].team }  // Winner J vs Winner L
    ];
    
    knockoutRounds.r32 = seedMapping.map((map, idx) => ({
        id: `r32_${idx}`,
        home: map.home,
        away: map.away,
        goals_home: null,
        goals_away: null,
        played: false,
        winner: null
    }));
    
    // Reset subsequent rounds
    knockoutRounds.r16 = Array.from({length: 8}, (_, i) => ({ id: `r16_${i}`, home: null, away: null, goals_home: null, goals_away: null, played: false, winner: null }));
    knockoutRounds.qf = Array.from({length: 4}, (_, i) => ({ id: `qf_${i}`, home: null, away: null, goals_home: null, goals_away: null, played: false, winner: null }));
    knockoutRounds.sf = Array.from({length: 2}, (_, i) => ({ id: `sf_${i}`, home: null, away: null, goals_home: null, goals_away: null, played: false, winner: null }));
    knockoutRounds.final = [{ id: 'final_0', home: null, away: null, goals_home: null, goals_away: null, played: false, winner: null }];
    
    switchTourneyView('bracket');
}

function switchTourneyView(viewName) {
    tourneyView = viewName;
    document.querySelectorAll('.tourney-view-section').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('#tab-tourney-groups, #tab-tourney-bracket').forEach(el => el.classList.remove('active'));
    
    if (viewName === 'groups') {
        document.getElementById('tourney-view-groups').classList.add('active');
        const gt = document.getElementById('tab-tourney-groups');
        if (gt) gt.classList.add('active');
    } else if (viewName === 'bracket') {
        document.getElementById('tourney-view-bracket').classList.add('active');
        const bt = document.getElementById('tab-tourney-bracket');
        if (bt) bt.classList.add('active');
        renderKnockoutBracket();
    } else if (viewName === 'live') {
        document.getElementById('tourney-view-live').classList.add('active');
    }
}

function renderKnockoutBracket() {
    const container = document.getElementById('bracket-bracket-visual');
    if (!knockoutRounds.r32.length) {
        container.innerHTML = `<div class="timeline-placeholder">Simulate all group stage matches to generate the Knockout Bracket.</div>`;
        return;
    }
    
    container.innerHTML = '';
    
    const rounds = [
        { title: "Round of 32", matches: knockoutRounds.r32 },
        { title: "Round of 16", matches: knockoutRounds.r16 },
        { title: "Quarterfinals", matches: knockoutRounds.qf },
        { title: "Semifinals", matches: knockoutRounds.sf },
        { title: "Final", matches: knockoutRounds.final }
    ];
    
    rounds.forEach(round => {
        const roundCol = document.createElement('div');
        roundCol.className = 'bracket-round';
        
        const roundTitle = document.createElement('div');
        roundTitle.className = 'bracket-round-title';
        roundTitle.textContent = round.title;
        roundCol.appendChild(roundTitle);
        
        round.matches.forEach(match => {
            const node = document.createElement('div');
            node.className = `bracket-match-node`;
            if (match.played) node.classList.add('completed');
            if (activeBracketMatch === match.id) node.classList.add('active-sim');
            
            node.onclick = () => {
                if (match.home && match.away) {
                    loadMatchToCenter(match.home, match.away, match.id);
                }
            };
            
            const homeText = match.home || "TBD";
            const awayText = match.away || "TBD";
            const homeScore = match.played ? match.goals_home : "-";
            const awayScore = match.played ? match.goals_away : "-";
            
            const homeWinnerClass = match.winner === match.home ? 'winner' : '';
            const awayWinnerClass = match.winner === match.away ? 'winner' : '';
            
            const crestHome = match.home ? getTeamCrestHTML(match.home) : "";
            const crestAway = match.away ? getTeamCrestHTML(match.away) : "";
            
            node.innerHTML = `
                <div class="bracket-team-row ${homeWinnerClass}">
                    <div style="display:flex; align-items:center;">${crestHome}<span>${homeText}</span></div>
                    <span class="bracket-team-score">${homeScore}</span>
                </div>
                <div class="bracket-team-row ${awayWinnerClass}">
                    <div style="display:flex; align-items:center;">${crestAway}<span>${awayText}</span></div>
                    <span class="bracket-team-score">${awayScore}</span>
                </div>
            `;
            roundCol.appendChild(node);
        });
        
        container.appendChild(roundCol);
    });
}

function simulateBracketMatch(match) {
    if (match.played || !match.home || !match.away) return;
    
    const score = simulateMatchInstance(match.home, match.away);
    match.goals_home = score.gh;
    match.goals_away = score.ga;
    match.played = true;
    
    // Knockouts must resolve ties (simulate penalties)
    if (score.gh === score.ga) {
        if (Math.random() < 0.5) {
            match.goals_home += 1; // Simulated win
            match.winner = match.home;
        } else {
            match.goals_away += 1;
            match.winner = match.away;
        }
    } else {
        match.winner = score.gh > score.ga ? match.home : match.away;
    }
}

function feedWinnerToNextRound(matchIndex, winnerTeam, currentRoundKey) {
    let nextRoundKey = "";
    let nextIndex = Math.floor(matchIndex / 2);
    let isAwaySide = (matchIndex % 2 === 1);
    
    if (currentRoundKey === 'r32') nextRoundKey = 'r16';
    else if (currentRoundKey === 'r16') nextRoundKey = 'qf';
    else if (currentRoundKey === 'qf') nextRoundKey = 'sf';
    else if (currentRoundKey === 'sf') nextRoundKey = 'final';
    else return; // Final winner ends tournament
    
    const nextMatch = knockoutRounds[nextRoundKey][nextIndex];
    if (isAwaySide) {
        nextMatch.away = winnerTeam;
    } else {
        nextMatch.home = winnerTeam;
    }
}

function simulateFullKnockout() {
    const roundOrder = ['r32', 'r16', 'qf', 'sf', 'final'];
    
    roundOrder.forEach(roundKey => {
        const matches = knockoutRounds[roundKey];
        matches.forEach((match, idx) => {
            if (match.played) return;
            if (match.home && match.away) {
                simulateBracketMatch(match);
                feedWinnerToNextRound(idx, match.winner, roundKey);
            }
        });
    });
    
    renderKnockoutBracket();
}

// ----------------------------------------------------
// Mathematical Simulation & Prediction Helpers
// ----------------------------------------------------

function predictLive(homeTeam, awayTeam, currentMinute, homeGoals, awayGoals, homeRedCards, awayRedCards) {
    const preMatch = predictPreMatch(homeTeam, awayTeam);
    const lambdaPre = preMatch.expected_goals_home;
    const muPre = preMatch.expected_goals_away;

    const remainingTime = Math.max(0, 90 - currentMinute);
    const timeFactor = remainingTime / 90.0;

    let lambdaRem = lambdaPre * timeFactor;
    let muRem = muPre * timeFactor;

    for (let i = 0; i < homeRedCards; i++) {
        lambdaRem *= 0.75;
        muRem *= 1.25;
    }
    for (let i = 0; i < awayRedCards; i++) {
        lambdaRem *= 1.25;
        muRem *= 0.75;
    }

    const maxRem = 8;
    let pHomeRem = Array.from({ length: maxRem }, (_, i) => poissonProb(i, lambdaRem));
    let pAwayRem = Array.from({ length: maxRem }, (_, i) => poissonProb(i, muRem));

    const sumH = pHomeRem.reduce((a, b) => a + b, 0);
    const sumA = pAwayRem.reduce((a, b) => a + b, 0);

    if (sumH > 0) pHomeRem = pHomeRem.map(p => p / sumH);
    else {
        pHomeRem = Array(maxRem).fill(0);
        pHomeRem[0] = 1.0;
    }

    if (sumA > 0) pAwayRem = pAwayRem.map(p => p / sumA);
    else {
        pAwayRem = Array(maxRem).fill(0);
        pAwayRem[0] = 1.0;
    }

    let pHomeWin = 0.0;
    let pDraw = 0.0;
    let pAwayWin = 0.0;

    for (let r_h = 0; r_h < maxRem; r_h++) {
        for (let r_a = 0; r_a < maxRem; r_a++) {
            const prob = pHomeRem[r_h] * pAwayRem[r_a];
            const finalHome = homeGoals + r_h;
            const finalAway = awayGoals + r_a;

            if (finalHome > finalAway) {
                pHomeWin += prob;
            } else if (finalHome < finalAway) {
                pAwayWin += prob;
            } else {
                pDraw += prob;
            }
        }
    }

    const totalProb = pHomeWin + pDraw + pAwayWin;
    if (totalProb > 0) {
        pHomeWin /= totalProb;
        pDraw /= totalProb;
        pAwayWin /= totalProb;
    } else {
        pHomeWin = 0.33;
        pDraw = 0.33;
        pAwayWin = 0.34;
    }

    return {
        minute: currentMinute,
        home_goals: homeGoals,
        away_goals: awayGoals,
        home_win_prob: pHomeWin,
        draw_prob: pDraw,
        away_win_prob: pAwayWin
    };
}

const TEAM_PLAYERS = {
    'Argentina': ['Messi', 'Alvarez', 'Lautaro Martinez', 'Mac Allister', 'De Paul', 'Di Maria', 'Enzo Fernandez'],
    'France': ['Mbappe', 'Griezmann', 'Giroud', 'Dembele', 'Kolo Muani', 'Coman', 'Tchouameni', 'Camavinga'],
    'Spain': ['Lamine Yamal', 'Morata', 'Dani Olmo', 'Nico Williams', 'Pedri', 'Gavi', 'Rodri', 'Oyarzabal'],
    'England': ['Kane', 'Bellingham', 'Saka', 'Foden', 'Palmer', 'Watkins', 'Rashford', 'Rice'],
    'Brazil': ['Vinicius Jr', 'Rodrygo', 'Neymar', 'Martinelli', 'Richarlison', 'Raphinha', 'Paqueta', 'Endrick'],
    'Portugal': ['Cristiano Ronaldo', 'Bruno Fernandes', 'Bernardo Silva', 'Joao Felix', 'Leao', 'Ramos', 'Diogo Jota'],
    'Netherlands': ['Depay', 'Gakpo', 'Weghorst', 'Malen', 'Simons', 'Dumfries', 'Van Dijk', 'Frimpong'],
    'Italy': ['Chiesa', 'Retegui', 'Barella', 'Raspadori', 'Scamacca', 'Pellegrini', 'Frattesi'],
    'Germany': ['Musiala', 'Wirtz', 'Havertz', 'Fullkrug', 'Sane', 'Gnabry', 'Muller', 'Gundogan'],
    'Colombia': ['Luis Diaz', 'James Rodriguez', 'Borre', 'Duran', 'Sinisterra', 'Arias'],
    'Uruguay': ['Darwin Nunez', 'Suarez', 'Valverde', 'Pellistri', 'Araujo', 'De Arrascaeta'],
    'Croatia': ['Modric', 'Kramaric', 'Perisic', 'Pasalic', 'Petkovic', 'Kovacic'],
    'Belgium': ['De Bruyne', 'Lukaku', 'Trossard', 'Doku', 'Bakayoko', 'Tielemans'],
    'Morocco': ['Ziyech', 'En-Nesyri', 'Diaz', 'Hakimi', 'Amrabat', 'Boufal'],
    'Japan': ['Mitoma', 'Minamino', 'Kubo', 'Maeda', 'Endo', 'Doan'],
    'Senegal': ['Sadio Mane', 'Sarr', 'Jackson', 'Dia', 'Gueye'],
    'USA': ['Pulisic', 'Balogun', 'Weah', 'McKennie', 'Reyna', 'Aaronson'],
    'Mexico': ['Santiago Gimenez', 'Quiñones', 'Lozano', 'Martin', 'Chavez'],
    'Canada': ['Jonathan David', 'Alphonso Davies', 'Larin', 'Buchanan', 'Eustaquio'],
    'Egypt': ['Salah', 'Mostafa Mohamed', 'Trezeguet', 'Marmoush'],
    'South Korea': ['Son', 'Hwang Hee-chan', 'Lee Kang-in', 'Cho Gue-sung'],
    'Sweden': ['Isak', 'Gyokeres', 'Kulusevski', 'Forsberg', 'Elanga'],
    'Poland': ['Lewandowski', 'Zielinski', 'Szymanski', 'Buksa', 'Piatek'],
    'Nigeria': ['Osimhen', 'Lookman', 'Chukwueze', 'Iheanacho', 'Boniface', 'Iwobi'],
    'Algeria': ['Mahrez', 'Bounedjah', 'Aouar', 'Gouiri', 'Benrahma'],
    'Ivory Coast': ['Haller', 'Adingra', 'Kessie', 'Boga', 'Pepe', 'Singo'],
    'Ecuador': ['Valencia', 'Caicedo', 'Paez', 'Sarmiento', 'Estupinian'],
    'Turkey': ['Arda Guler', 'Yilmaz', 'Calhanoglu', 'Akturkoglu', 'Tosun'],
    'Australia': ['Duke', 'Boyle', 'Goodwin', 'Irankunda'],
    'Switzerland': ['Embolo', 'Shaqiri', 'Amdouni', 'Xhaka', 'Vargas'],
    'Denmark': ['Hojlund', 'Eriksen', 'Wind', 'Poulsen', 'Hojbjerg'],
    'Austria': ['Arnautovic', 'Sabitzer', 'Gregoritsch', 'Laimer', 'Baumgartner'],
    'Ukraine': ['Dovbyk', 'Mudryk', 'Tsygankov', 'Yaremchuk', 'Sudakov'],
    'Czechia': ['Schick', 'Chory', 'Soucek', 'Provod'],
    'Hungary': ['Szoboszlai', 'Varga', 'Sallai', 'Kleinheisler'],
    'Wales': ['James', 'Wilson', 'Johnson', 'Moore'],
    'Paraguay': ['Almiron', 'Enciso', 'Sanabria', 'Romero'],
    'Ghana': ['Kudus', 'Inaki Williams', 'Jordan Ayew', 'Semenyo'],
    'Chile': ['Alexis Sanchez', 'Vargas', 'Brereton Diaz', 'Valdes'],
    'Peru': ['Lapadula', 'Guerrero', 'Flores', 'Quispe'],
    'Venezuela': ['Rondon', 'Savariano', 'Machis', 'Soteldo'],
    'Tunisia': ['Msakni', 'Achouri', 'Rafia', 'Laidouni'],
    'Saudi Arabia': ['Al-Dawsari', 'Al-Shehri', 'Al-Buraikan', 'Ghareeb'],
    'Qatar': ['Afif', 'Almoez Ali', 'Al-Haydos'],
    'Iraq': ['Aymen Hussein', 'Ali Jasim', 'Resan']
};

function getRandomScorer(team) {
    const list = TEAM_PLAYERS[team];
    if (list && list.length > 0) {
        return list[Math.floor(Math.random() * list.length)];
    }
    const generic = ['Martinez', 'Smith', 'Rodriguez', 'Gomez', 'Müller', 'Silva', 'Tanaka', 'Kim', 'Ali', 'Jones', 'Sosa', 'Mensah', 'Diallo', 'Ivanov'];
    return generic[Math.floor(Math.random() * generic.length)];
}

function simulateStep(homeTeam, awayTeam, minute) {
    const hStrength = MODEL_DATA.strengths[homeTeam] || {};
    const aStrength = MODEL_DATA.strengths[awayTeam] || {};

    let h_shot_rate = (hStrength.avg_shots || 12.0) / 90.0;
    let a_shot_rate = (aStrength.avg_shots || 11.0) / 90.0;
    let h_corner_rate = (hStrength.avg_corners || 5.0) / 90.0;
    let a_corner_rate = (aStrength.avg_corners || 4.5) / 90.0;

    let h_foul_rate = 10.5 / 90.0;
    let a_foul_rate = 11.0 / 90.0;
    let h_yellow_rate = (hStrength.avg_yellow || 1.8) / 90.0;
    let a_yellow_rate = (aStrength.avg_yellow || 2.0) / 90.0;
    let h_red_rate = (hStrength.avg_red || 0.02) / 90.0;
    let a_red_rate = (aStrength.avg_red || 0.02) / 90.0;

    const preMatch = predictPreMatch(homeTeam, awayTeam);
    let h_goal_rate = preMatch.expected_goals_home / 90.0;
    let a_goal_rate = preMatch.expected_goals_away / 90.0;

    const home_red_cards = simStats.home_red_cards;
    const away_red_cards = simStats.away_red_cards;

    const h_red_penalty = Math.pow(0.8, home_red_cards);
    const a_red_penalty = Math.pow(0.8, away_red_cards);

    h_goal_rate *= h_red_penalty * Math.pow(1.2, away_red_cards);
    a_goal_rate *= a_red_penalty * Math.pow(1.2, home_red_cards);
    h_shot_rate *= h_red_penalty * Math.pow(1.15, away_red_cards);
    a_shot_rate *= a_red_penalty * Math.pow(1.15, home_red_cards);

    const events = [];

    // Shots
    if (Math.random() < h_shot_rate) {
        simStats.home_shots += 1;
        if (Math.random() < 0.4) {
            simStats.home_sot += 1;
        }
    }
    if (Math.random() < a_shot_rate) {
        simStats.away_shots += 1;
        if (Math.random() < 0.4) {
            simStats.away_sot += 1;
        }
    }

    // Corners
    if (Math.random() < h_corner_rate) {
        simStats.home_corners += 1;
        events.push({ type: 'corner', team: 'home', desc: `${minute}' Corner for ${homeTeam}.` });
    }
    if (Math.random() < a_corner_rate) {
        simStats.away_corners += 1;
        events.push({ type: 'corner', team: 'away', desc: `${minute}' Corner for ${awayTeam}.` });
    }

    // Fouls
    if (Math.random() < h_foul_rate) {
        simStats.home_fouls += 1;
    }
    if (Math.random() < a_foul_rate) {
        simStats.away_fouls += 1;
    }

    // Yellow Cards
    if (Math.random() < h_yellow_rate) {
        events.push({ type: 'yellow', team: 'home', desc: `🟨 ${minute}' Yellow Card for ${homeTeam} player.` });
    }
    if (Math.random() < a_yellow_rate) {
        events.push({ type: 'yellow', team: 'away', desc: `🟨 ${minute}' Yellow Card for ${awayTeam} player.` });
    }

    // Red Cards
    if (simStats.home_red_cards < 4 && Math.random() < h_red_rate) {
        simStats.home_red_cards += 1;
        events.push({ type: 'red', team: 'home', desc: `🟥 ${minute}' RED CARD! ${homeTeam} are down to ${11 - simStats.home_red_cards} men.` });
    }
    if (simStats.away_red_cards < 4 && Math.random() < a_red_rate) {
        simStats.away_red_cards += 1;
        events.push({ type: 'red', team: 'away', desc: `🟥 ${minute}' RED CARD! ${awayTeam} are down to ${11 - simStats.away_red_cards} men.` });
    }

    // Goals (modelled as Poisson event)
    let goal_scored_home = false;
    
    if (Math.random() < h_goal_rate) {
        simStats.home_goals += 1;
        simStats.home_shots = Math.max(simStats.home_shots, simStats.home_goals);
        simStats.home_sot = Math.max(simStats.home_sot, simStats.home_goals);
        goal_scored_home = true;

        const scorer = getRandomScorer(homeTeam);
        events.push({
            type: 'goal',
            team: 'home',
            desc: `⚽ ${minute}' GOAL! ${homeTeam} ${simStats.home_goals} - ${simStats.away_goals} ${awayTeam}. ${scorer} scores with a beautiful finish!`
        });
    }

    if (Math.random() < a_goal_rate && !goal_scored_home) {
        simStats.away_goals += 1;
        simStats.away_shots = Math.max(simStats.away_shots, simStats.away_goals);
        simStats.away_sot = Math.max(simStats.away_sot, simStats.away_goals);

        const scorer = getRandomScorer(awayTeam);
        events.push({
            type: 'goal',
            team: 'away',
            desc: `⚽ ${minute}' GOAL! ${homeTeam} ${simStats.home_goals} - ${simStats.away_goals} ${awayTeam}. ${scorer} strikes it into the bottom corner!`
        });
    }

    // Calculate live prediction
    const livePred = predictLive(homeTeam, awayTeam, minute, simStats.home_goals, simStats.away_goals, simStats.home_red_cards, simStats.away_red_cards);

    // Possession calculations
    const basePossession = 50.0 + (preMatch.home_win_prob - preMatch.away_win_prob) * 20.0;
    let possessionHome = Math.round(basePossession + (Math.random() * 10 - 5));
    possessionHome = Math.max(25, Math.min(75, possessionHome));
    simStats.possession_home = possessionHome;
    simStats.possession_away = 100 - possessionHome;

    return {
        success: true,
        minute: minute,
        stats: { ...simStats },
        events: events,
        prediction: {
            home_win_prob: livePred.home_win_prob,
            draw_prob: livePred.draw_prob,
            away_win_prob: livePred.away_win_prob
        }
    };
}

function getTeamCrestHTML(teamName) {
    const teamId = TEAM_IDS[teamName] || 50;
    return `<img src="https://media.api-sports.io/football/teams/${teamId}.png" class="team-crest-img" alt="${teamName} Crest" onerror="this.src='https://media.api-sports.io/football/teams/50.png'">`;
}

function updateJerseyColors(jerseyElementId, teamName) {
    const colors = TEAM_COLORS[teamName] || TEAM_COLORS['default'];
    const jerseyEl = document.getElementById(jerseyElementId);
    if (!jerseyEl) return;
    
    const body = jerseyEl.querySelector('.jersey-body');
    const leftSleeve = jerseyEl.querySelector('.jersey-sleeve.left');
    const rightSleeve = jerseyEl.querySelector('.jersey-sleeve.right');
    const stripe = jerseyEl.querySelector('.jersey-stripe');
    const sponsor = jerseyEl.querySelector('.jersey-sponsor');
    
    // Reset Styles
    if (body) {
        body.style.background = '';
        body.style.backgroundColor = colors.primary;
    }
    if (leftSleeve) {
        leftSleeve.style.background = '';
        leftSleeve.style.backgroundColor = colors.primary;
    }
    if (rightSleeve) {
        rightSleeve.style.background = '';
        rightSleeve.style.backgroundColor = colors.primary;
    }
    if (stripe) {
        stripe.style.background = '';
        stripe.style.display = 'none';
    }
    if (sponsor) {
        sponsor.textContent = 'Visionary';
        sponsor.style.color = colors.secondary;
    }
    
    // Apply Custom Patterns for World Cup Teams
    if (teamName === 'Argentina') {
        if (body) body.style.background = 'linear-gradient(90deg, #75AADB 20%, #FFFFFF 20%, #FFFFFF 40%, #75AADB 40%, #75AADB 60%, #FFFFFF 60%, #FFFFFF 80%, #75AADB 80%)';
        if (leftSleeve) leftSleeve.style.backgroundColor = '#75AADB';
        if (rightSleeve) rightSleeve.style.backgroundColor = '#75AADB';
    }
    else if (teamName === 'Croatia') {
        if (body) body.style.background = 'repeating-linear-gradient(45deg, #FF0000, #FF0000 10px, #FFFFFF 10px, #FFFFFF 20px)';
    }
    else if (teamName === 'USA') {
        if (body) body.style.backgroundColor = '#0A2240';
        if (leftSleeve) leftSleeve.style.backgroundColor = '#E0162B';
        if (rightSleeve) rightSleeve.style.backgroundColor = '#E0162B';
    }
}

// ----------------------------------------------------
// Live Match Center Simulation Loop (Poisson Center)
// ----------------------------------------------------

function selectFixture(home, away) {
    simHome = home;
    simAway = away;
    simHomeElo = Math.round(MODEL_DATA.current_elos[home]) || 1500;
    simAwayElo = Math.round(MODEL_DATA.current_elos[away]) || 1500;
    
    document.getElementById('sim-lbl-home-name').innerHTML = `${getTeamCrestHTML(home)} ${home}`;
    document.getElementById('sim-lbl-away-name').innerHTML = `${away} ${getTeamCrestHTML(away)}`;
    document.getElementById('sim-lbl-home-elo').textContent = `Elo: ${simHomeElo}`;
    document.getElementById('sim-lbl-away-elo').textContent = `Elo: ${simAwayElo}`;
    
    document.getElementById('lbl-live-box-home-name').textContent = home;
    document.getElementById('lbl-live-box-away-name').textContent = away;
    
    updateJerseyColors('sim-jersey-home', home);
    updateJerseyColors('sim-jersey-away', away);
    
    resetSimulation();
    switchTab('simulator');
}

function toggleSimulation() {
    const startBtn = document.getElementById('btn-start-sim');
    const resetBtn = document.getElementById('btn-reset-sim');
    const speedSelect = document.getElementById('select-sim-speed');
    
    if (simIsActive) {
        clearInterval(simTimer);
        simIsActive = false;
        startBtn.textContent = 'Resume Simulation';
        startBtn.className = 'btn btn-primary';
        resetBtn.disabled = false;
        speedSelect.disabled = false;
    } else {
        if (simMinute >= 90) {
            resetSimulation();
        }
        
        simIsActive = true;
        startBtn.textContent = 'Pause Simulation';
        startBtn.className = 'btn btn-secondary';
        resetBtn.disabled = true;
        speedSelect.disabled = true;
        
        const speed = parseInt(speedSelect.value);
        simTimer = setInterval(runSimulationStep, speed);
    }
}

function runSimulationStep() {
    if (!simIsActive) return;
    
    simMinute += 1;
    
    try {
        const data = simulateStep(simHome, simAway, simMinute);
        if (data.success) {
            updateSimUI(data);
        }
    } catch (e) {
        console.error('Error running simulation step:', e);
        clearInterval(simTimer);
    }
}

function updateSimUI(data) {
    simStats = data.stats;
    
    document.getElementById('sim-lbl-goals').textContent = `${simStats.home_goals} - ${simStats.away_goals}`;
    document.getElementById('sim-lbl-time').textContent = `${data.minute}'`;
    
    const tickerContainer = document.getElementById('ticker-matches-container');
    if (tickerContainer && simHome === 'USA' && simAway === 'Colombia') {
        const activeLiveMatch = tickerContainer.querySelector('.ticker-match');
        if (activeLiveMatch) {
            activeLiveMatch.innerHTML = `<span class="ticker-dot"></span> USA ${simStats.home_goals} - ${simStats.away_goals} COL (${data.minute}')`;
        }
    }
    
    document.getElementById('lbl-stat-possession-home').textContent = `${simStats.possession_home}%`;
    document.getElementById('lbl-stat-possession-away').textContent = `${simStats.possession_away}%`;
    document.getElementById('bar-stat-possession').style.width = `${simStats.possession_home}%`;
    
    document.getElementById('lbl-stat-shots-home').textContent = simStats.home_shots;
    document.getElementById('lbl-stat-shots-away').textContent = simStats.away_shots;
    const shotTotal = simStats.home_shots + simStats.away_shots;
    document.getElementById('bar-stat-shots').style.width = shotTotal > 0 ? `${(simStats.home_shots / shotTotal) * 100}%` : '50%';
    
    document.getElementById('lbl-stat-sot-home').textContent = simStats.home_sot;
    document.getElementById('lbl-stat-sot-away').textContent = simStats.away_sot;
    const sotTotal = simStats.home_sot + simStats.away_sot;
    document.getElementById('bar-stat-sot').style.width = sotTotal > 0 ? `${(simStats.home_sot / sotTotal) * 100}%` : '50%';
    
    document.getElementById('lbl-stat-corners-home').textContent = simStats.home_corners;
    document.getElementById('lbl-stat-corners-away').textContent = simStats.away_corners;
    const cornerTotal = simStats.home_corners + simStats.away_corners;
    document.getElementById('bar-stat-corners').style.width = cornerTotal > 0 ? `${(simStats.home_corners / cornerTotal) * 100}%` : '50%';
    
    document.getElementById('lbl-stat-reds-home').textContent = simStats.home_red_cards;
    document.getElementById('lbl-stat-reds-away').textContent = simStats.away_red_cards;
    const redTotal = simStats.home_red_cards + simStats.away_red_cards;
    document.getElementById('bar-stat-reds').style.width = redTotal > 0 ? `${(simStats.home_red_cards / redTotal) * 100}%` : '50%';
    
    const eventsContainer = document.getElementById('events-timeline-container');
    if (data.events && data.events.length > 0) {
        const placeholder = eventsContainer.querySelector('.timeline-placeholder');
        if (placeholder) placeholder.remove();
        
        data.events.forEach(evt => {
            const bubble = document.createElement('div');
            bubble.classList.add('event-bubble', evt.type);
            
            let icon = '📢';
            if (evt.type === 'goal') icon = '⚽';
            else if (evt.type === 'yellow') icon = '🟨';
            else if (evt.type === 'red') icon = '🟥';
            else if (evt.type === 'corner') icon = '🚩';
            
            bubble.innerHTML = `<strong>${icon} ${evt.desc}</strong>`;
            eventsContainer.insertBefore(bubble, eventsContainer.firstChild);
        });
    }
    
    const homeWin = data.prediction.home_win_prob;
    const draw = data.prediction.draw_prob;
    const awayWin = data.prediction.away_win_prob;
    
    document.getElementById('lbl-live-box-home-val').textContent = `${Math.round(homeWin * 100)}%`;
    document.getElementById('lbl-live-box-draw-val').textContent = `${Math.round(draw * 100)}%`;
    document.getElementById('lbl-live-box-away-val').textContent = `${Math.round(awayWin * 100)}%`;
    
    if (liveChart) {
        liveChart.data.labels.push(data.minute);
        liveChart.data.datasets[0].data.push(Math.round(homeWin * 100));
        liveChart.data.datasets[1].data.push(Math.round(draw * 100));
        liveChart.data.datasets[2].data.push(Math.round(awayWin * 100));
        liveChart.update('none');
    }
    
    if (simMinute >= 90) {
        clearInterval(simTimer);
        simIsActive = false;
        
        const startBtn = document.getElementById('btn-start-sim');
        const resetBtn = document.getElementById('btn-reset-sim');
        const speedSelect = document.getElementById('select-sim-speed');
        
        startBtn.textContent = 'Match Finished';
        startBtn.className = 'btn btn-secondary';
        startBtn.disabled = true;
        resetBtn.disabled = false;
        speedSelect.disabled = false;
        
        // Resolve draw ties if it is a bracket match (seeding winner)
        let resolvedGoalsHome = simStats.home_goals;
        let resolvedGoalsAway = simStats.away_goals;
        let pWinner = null;
        
        if (activeBracketMatch && resolvedGoalsHome === resolvedGoalsAway) {
            let shootoutWinner = Math.random() < 0.5 ? 'home' : 'away';
            if (shootoutWinner === 'home') {
                resolvedGoalsHome += 1;
                pWinner = simHome;
                const penaltyBubble = document.createElement('div');
                penaltyBubble.className = 'event-bubble goal';
                penaltyBubble.innerHTML = `<strong>🏆 Penalty Shootout!</strong> ${simHome} wins the shootout and advances!`;
                eventsContainer.insertBefore(penaltyBubble, eventsContainer.firstChild);
            } else {
                resolvedGoalsAway += 1;
                pWinner = simAway;
                const penaltyBubble = document.createElement('div');
                penaltyBubble.className = 'event-bubble goal';
                penaltyBubble.innerHTML = `<strong>🏆 Penalty Shootout!</strong> ${simAway} wins the shootout and advances!`;
                eventsContainer.insertBefore(penaltyBubble, eventsContainer.firstChild);
            }
        } else {
            pWinner = resolvedGoalsHome > resolvedGoalsAway ? simHome : simAway;
        }

        const ftBubble = document.createElement('div');
        ftBubble.className = 'event-bubble';
        ftBubble.style.borderLeftColor = 'var(--text-primary)';
        ftBubble.innerHTML = `<strong>🏁 90' FULL TIME!</strong> The match ends: ${simHome} ${simStats.home_goals} - ${simStats.away_goals} ${simAway}.`;
        eventsContainer.insertBefore(ftBubble, eventsContainer.firstChild);
        
        // Write result back to group matches or bracket matches!
        writeBackMatchOutcome(activeBracketMatch, resolvedGoalsHome, resolvedGoalsAway, pWinner);
    }
}

function writeBackMatchOutcome(matchId, goalsHome, goalsAway, winner) {
    if (!matchId) return;
    
    // Check if it's a group fixture
    if (matchId.startsWith("Group")) {
        const groupName = matchId.substring(0, 7); // Group A
        const match = groupFixtures[groupName].find(f => f.id === matchId);
        if (match) {
            match.goals_home = goalsHome;
            match.goals_away = goalsAway;
            match.played = true;
            recalculateStandings(groupName);
            renderGroupData();
            checkAllGroupsSimulated();
        }
    } else {
        // It's a bracket match
        const rounds = ['r32', 'r16', 'qf', 'sf', 'final'];
        for (const roundKey of rounds) {
            const matches = knockoutRounds[roundKey];
            const idx = matches.findIndex(f => f.id === matchId);
            if (idx !== -1) {
                const match = matches[idx];
                match.goals_home = goalsHome;
                match.goals_away = goalsAway;
                match.played = true;
                match.winner = winner;
                
                // Propagate to next round
                feedWinnerToNextRound(idx, winner, roundKey);
                renderKnockoutBracket();
                break;
            }
        }
    }
}

function resetSimulation() {
    clearInterval(simTimer);
    simIsActive = false;
    simMinute = 0;
    
    simStats = {
        home_goals: 0, away_goals: 0, home_red_cards: 0, away_red_cards: 0,
        home_shots: 0, away_shots: 0, home_sot: 0, away_sot: 0,
        home_corners: 0, away_corners: 0, home_fouls: 0, away_fouls: 0,
        possession_home: 50, possession_away: 50
    };
    
    document.getElementById('sim-lbl-goals').textContent = '0 - 0';
    document.getElementById('sim-lbl-time').textContent = 'Not Started';
    
    const startBtn = document.getElementById('btn-start-sim');
    startBtn.textContent = 'Start Simulation';
    startBtn.className = 'btn btn-primary';
    startBtn.disabled = false;
    
    document.getElementById('btn-reset-sim').disabled = true;
    document.getElementById('select-sim-speed').disabled = false;
    
    const eventsContainer = document.getElementById('events-timeline-container');
    eventsContainer.innerHTML = '<div class="timeline-placeholder">Match events will appear here chronologically once simulated kick-off begins...</div>';
    
    document.getElementById('lbl-stat-possession-home').textContent = '50%';
    document.getElementById('lbl-stat-possession-away').textContent = '50%';
    document.getElementById('bar-stat-possession').style.width = '50%';
    
    document.getElementById('lbl-stat-shots-home').textContent = '0';
    document.getElementById('lbl-stat-shots-away').textContent = '0';
    document.getElementById('bar-stat-shots').style.width = '50%';
    
    document.getElementById('lbl-stat-sot-home').textContent = '0';
    document.getElementById('lbl-stat-sot-away').textContent = '0';
    document.getElementById('bar-stat-sot').style.width = '50%';
    
    document.getElementById('lbl-stat-corners-home').textContent = '0';
    document.getElementById('lbl-stat-corners-away').textContent = '0';
    document.getElementById('bar-stat-corners').style.width = '50%';
    
    document.getElementById('lbl-stat-reds-home').textContent = '0';
    document.getElementById('lbl-stat-reds-away').textContent = '0';
    document.getElementById('bar-stat-reds').style.width = '50%';
    
    seedLiveChartPreMatch();
}

function seedLiveChartPreMatch() {
    if (!simHome || !simAway) return;
    
    try {
        const pred = predictPreMatch(simHome, simAway);
        const h = Math.round(pred.home_win_prob * 100);
        const d = Math.round(pred.draw_prob * 100);
        const a = Math.round(pred.away_win_prob * 100);
        
        document.getElementById('lbl-live-box-home-val').textContent = `${h}%`;
        document.getElementById('lbl-live-box-draw-val').textContent = `${d}%`;
        document.getElementById('lbl-live-box-away-val').textContent = `${a}%`;
        
        if (liveChart) {
            liveChart.data.labels = [0];
            liveChart.data.datasets[0].data = [h];
            liveChart.data.datasets[1].data = [d];
            liveChart.data.datasets[2].data = [a];
            liveChart.update();
        }
    } catch (e) {
        console.error('Error seeding chart:', e);
    }
}

// ----------------------------------------------------
// Players Hub Registry & Match Logs rendering
// ----------------------------------------------------

function initPlayersHub() {
    const select = document.getElementById('player-select-hub');
    if (!select) return;
    
    select.innerHTML = '';
    
    let allP = [];
    if (Object.keys(GLOBAL_PLAYERS_DB).length > 0) {
        Object.values(GLOBAL_PLAYERS_DB).forEach(teamArr => {
            allP.push(...teamArr);
        });
    } else {
        allP = MODEL_DATA.players;
    }
    
    allP.forEach(p => {
        const opt = document.createElement('option');
        const country = p.team || p.country;
        opt.value = p.name;
        opt.textContent = `${p.name} (${country})`;
        select.appendChild(opt);
    });
    
    if (allP.length > 0) {
        handlePlayerHubChange(allP[0].name);
    }
}

function handlePlayerHubChange(playerName) {
    let allP = [];
    if (Object.keys(GLOBAL_PLAYERS_DB).length > 0) {
        Object.values(GLOBAL_PLAYERS_DB).forEach(teamArr => {
            allP.push(...teamArr);
        });
    } else {
        allP = MODEL_DATA.players;
    }
    const player = allP.find(p => p.name === playerName);
    if (!player) return;
    
    // Renders bio card
    const cardContainer = document.getElementById('player-bio-card-container');
    const playerFlagEmoji = getFlagEmoji(player.country || player.team);
    const playerAge = player.age || 'N/A';
    const playerClub = player.club || 'National Team';
    const playerPhoto = player.photo || '/static/img/player_visionary.png';
    
    cardContainer.innerHTML = `
        <div class="player-main-card">
            <div class="player-photo-area">
                <img src="${playerPhoto}" alt="Player Photo" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">
            </div>
            <div class="player-info-area">
                <div class="player-name-lbl">${player.name} ${playerFlagEmoji}</div>
                <div class="player-meta-row">
                    <span>${player.position}</span>
                    <span>Age: ${playerAge}</span>
                    <span class="player-club-tag">${playerClub}</span>
                </div>
                <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:0.25rem;">
                    Rating: <strong style="color:var(--accent-gold); font-size:1rem;">${player.rating.toFixed(2)}</strong>
                </div>
            </div>
        </div>
        
        <div class="player-stats-grid">
            <div class="player-stat-card">
                <span class="player-stat-val">${player.matches}</span>
                <span class="player-stat-lbl">Matches</span>
            </div>
            <div class="player-stat-card">
                <span class="player-stat-val">${player.goals}</span>
                <span class="player-stat-lbl">Goals</span>
            </div>
            <div class="player-stat-card">
                <span class="player-stat-val">${player.assists}</span>
                <span class="player-stat-lbl">Assists</span>
            </div>
        </div>
    `;
    
    // Render match histories logs table
    const tbody = document.getElementById('player-matchlogs-tbody');
    tbody.innerHTML = '';
    
    player.match_history.forEach(log => {
        const tr = document.createElement('tr');
        const ratingColor = log.rating >= 8.5 ? 'var(--accent-brand)' : (log.rating >= 7.5 ? 'var(--text-primary)' : 'var(--text-muted)');
        const outcomeClass = log.result.startsWith('W') ? 'W' : (log.result.startsWith('L') ? 'L' : 'D');
        
        tr.innerHTML = `
            <td>${log.date}</td>
            <td><strong>${log.match}</strong></td>
            <td><strong style="color:${ratingColor};">${log.rating.toFixed(1)}</strong></td>
            <td>${log.goals}</td>
            <td>${log.assists}</td>
            <td>${log.minutes}'</td>
            <td>
                <span class="form-pill ${outcomeClass}" style="width:auto; padding:0 0.4rem; border-radius:3px;">${log.result}</span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function getFlagEmoji(country) {
    const flags = {
        'Argentina': '🇦🇷', 'France': '🇫🇷', 'Spain': '🇪🇸', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'Brazil': '🇧🇷', 'Portugal': '🇵🇹', 'Netherlands': '🇳🇱', 'Italy': '🇮🇹',
        'Germany': '🇩🇪', 'Colombia': '🇨🇴', 'Uruguay': '🇺🇾', 'Croatia': '🇭🇷',
        'Belgium': '🇧🇪', 'Morocco': '🇲🇦', 'Japan': '🇯🇵', 'Senegal': '🇸🇳',
        'USA': '🇺🇸', 'Mexico': '🇲🇽', 'Canada': '🇨🇦', 'Norway': '🇳🇴', 'Egypt': '🇪🇬',
        'South Korea': '🇰🇷', 'Sweden': '🇸🇪'
    };
    return flags[country] || '⚽';
}

// ----------------------------------------------------
// UI Flow Interactions & Tab Controllers
// ----------------------------------------------------

// ----------------------------------------------------
// Real-World Live Tracker Functions
// ----------------------------------------------------

function switchTrackerMode(mode) {
    activeTrackerMode = mode;
    document.getElementById('mode-simulated').classList.toggle('active', mode === 'simulated');
    document.getElementById('mode-live').classList.toggle('active', mode === 'live');
    
    const groupsTab = document.getElementById('tab-tourney-groups');
    const bracketTab = document.getElementById('tab-tourney-bracket');
    
    if (mode === 'live') {
        document.getElementById('live-api-key-panel').style.display = 'block';
        if (groupsTab) groupsTab.style.display = 'none';
        if (bracketTab) bracketTab.style.display = 'none';
        switchTourneyView('live');
        
        // Load API key if available
        const savedKey = localStorage.getItem('apiFootballKey');
        if (savedKey) {
            document.getElementById('api-key-input').value = savedKey;
        }
        
        fetchLiveMatches();
    } else {
        document.getElementById('live-api-key-panel').style.display = 'none';
        if (groupsTab) groupsTab.style.display = 'inline-block';
        if (bracketTab) bracketTab.style.display = 'inline-block';
        switchTourneyView('groups');
        
        if (livePoller) {
            clearInterval(livePoller);
            livePoller = null;
        }
    }
}

function saveApiKey() {
    const key = document.getElementById('api-key-input').value;
    if (key) {
        localStorage.setItem('apiFootballKey', key);
        alert('API Key saved successfully!');
        fetchLiveMatches();
    } else {
        localStorage.removeItem('apiFootballKey');
        alert('API Key cleared. Using mock data.');
        fetchLiveMatches();
    }
}

async function fetchLiveMatches() {
    const container = document.getElementById('real-live-matches-container');
    container.innerHTML = '<div class="timeline-placeholder">Fetching live matches...</div>';
    
    const apiKey = localStorage.getItem('apiFootballKey');
    const headers = {};
    if (apiKey) {
        headers['x-apisports-key'] = apiKey;
    }
    
    try {
        const response = await fetch('/api/live-matches', { headers });
        const data = await response.json();
        
        if (data.success) {
            container.innerHTML = '';
            if (data.data.length === 0) {
                container.innerHTML = '<div class="timeline-placeholder">No matches currently live or scheduled for today.</div>';
                return;
            }
            
            data.data.forEach(match => {
                const item = document.createElement('div');
                item.className = 'match-item';
                
                const homeName = match.teams.home.name;
                const awayName = match.teams.away.name;
                const homeLogo = `<img src="${match.teams.home.logo}" class="team-crest-img" onerror="this.src='https://media.api-sports.io/football/teams/50.png'">`;
                const awayLogo = `<img src="${match.teams.away.logo}" class="team-crest-img" onerror="this.src='https://media.api-sports.io/football/teams/50.png'">`;
                
                // Determine score to display
                let score = 'vs';
                if (match.goals && match.goals.home !== null) {
                    score = `${match.goals.home} - ${match.goals.away}`;
                }
                
                const status = match.status || (match.fixture && match.fixture.status) || {};
                const timeStr = status.elapsed ? `${status.elapsed}'` : (status.short || '');
                
                const fixtureId = match.fixture ? match.fixture.id : match.id;
                
                item.innerHTML = `
                    <span class="match-team home">${homeLogo}${homeName}</span>
                    <div style="display:flex; flex-direction:column; align-items:center; cursor:pointer;" onclick="startLiveMatchTracking(${fixtureId}, '${homeName}', '${awayName}', '${score}', '${timeStr}')">
                        <span class="match-score">${score}</span>
                        <span style="font-size:0.7rem; color:var(--accent-gold);">${timeStr}</span>
                    </div>
                    <span class="match-team away">${awayName}${awayLogo}</span>
                `;
                container.appendChild(item);
            });
        } else {
            container.innerHTML = `<div class="timeline-placeholder">Error: ${data.error}</div>`;
        }
    } catch (e) {
        container.innerHTML = `<div class="timeline-placeholder">Failed to connect to proxy server.</div>`;
    }
}

function startLiveMatchTracking(fixtureId, homeTeam, awayTeam, scoreStr, timeStr) {
    if (simIsActive) toggleSimulation(); // Pause active simulation
    if (livePoller) clearInterval(livePoller);
    
    liveFixtureId = fixtureId;
    liveHome = homeTeam;
    liveAway = awayTeam;
    
    document.getElementById('sim-lbl-home-name').innerHTML = `${getTeamCrestHTML(homeTeam)} ${homeTeam}`;
    document.getElementById('sim-lbl-away-name').innerHTML = `${awayTeam} ${getTeamCrestHTML(awayTeam)}`;
    
    updateJerseyColors('sim-jersey-home', homeTeam);
    updateJerseyColors('sim-jersey-away', awayTeam);
    
    document.getElementById('sim-lbl-goals').textContent = scoreStr || '0 - 0';
    document.getElementById('sim-lbl-time').textContent = timeStr || 'Live';
    
    document.getElementById('btn-start-sim').textContent = 'Tracking Live...';
    document.getElementById('btn-start-sim').className = 'btn btn-secondary';
    document.getElementById('btn-start-sim').disabled = true;
    document.getElementById('btn-reset-sim').disabled = true;
    document.getElementById('select-sim-speed').disabled = true;
    
    pollLiveMatchData();
    livePoller = setInterval(pollLiveMatchData, 20000); // Poll every 20 seconds
}

async function pollLiveMatchData() {
    if (!liveFixtureId) return;
    
    const apiKey = localStorage.getItem('apiFootballKey');
    const headers = {};
    if (apiKey) headers['x-apisports-key'] = apiKey;
    
    try {
        const response = await fetch(`/api/live-match-details?fixture=${liveFixtureId}`, { headers });
        const data = await response.json();
        
        if (data.success) {
            renderLiveMatchData(data);
        }
    } catch (e) {
        console.error('Failed to poll live data', e);
    }
}

function renderLiveMatchData(data) {
    // 1. Update events timeline
    const eventsContainer = document.getElementById('events-timeline-container');
    eventsContainer.innerHTML = '';
    
    const eventsList = data.events || [];
    if (eventsList.length === 0) {
        eventsContainer.innerHTML = '<div class="timeline-placeholder">Waiting for match events...</div>';
    } else {
        // Reverse array to show latest first
        eventsList.slice().reverse().forEach(evt => {
            const bubble = document.createElement('div');
            
            let icon = '📢';
            let typeClass = 'event-bubble';
            if (evt.type === 'Goal') { icon = '⚽'; typeClass += ' goal'; }
            else if (evt.type === 'Card' && evt.detail === 'Yellow Card') { icon = '🟨'; typeClass += ' yellow'; }
            else if (evt.type === 'Card' && evt.detail === 'Red Card') { icon = '🟥'; typeClass += ' red'; }
            else if (evt.type === 'subst') { icon = '🔄'; }
            
            bubble.className = typeClass;
            const timeObj = evt.time || {};
            const time = timeObj.elapsed + (timeObj.extra ? `+${timeObj.extra}` : '');
            const team = (evt.team && evt.team.name) || '';
            const player = (evt.player && evt.player.name) || '';
            const detail = evt.detail || evt.type;
            
            bubble.innerHTML = `<strong>${icon} ${time}'</strong> ${team}: ${detail} - ${player}`;
            eventsContainer.appendChild(bubble);
        });
    }
    
    // 2. Update Stats (Possession, Shots)
    const statsList = data.statistics || [];
    let homeStats = null;
    let awayStats = null;
    
    if (statsList.length >= 2) {
        homeStats = statsList[0].statistics;
        awayStats = statsList[1].statistics;
    }
    
    const findStat = (statsArray, typeName) => {
        if (!statsArray) return 0;
        const s = statsArray.find(x => x.type === typeName);
        if (s && s.value !== null) {
            if (typeof s.value === 'string' && s.value.endsWith('%')) return parseInt(s.value);
            return parseInt(s.value);
        }
        return 0;
    };
    
    const posH = findStat(homeStats, 'Ball Possession') || 50;
    const posA = findStat(awayStats, 'Ball Possession') || 50;
    document.getElementById('lbl-stat-possession-home').textContent = `${posH}%`;
    document.getElementById('lbl-stat-possession-away').textContent = `${posA}%`;
    document.getElementById('bar-stat-possession').style.width = `${posH}%`;
    
    const shotH = findStat(homeStats, 'Total Shots') || 0;
    const shotA = findStat(awayStats, 'Total Shots') || 0;
    document.getElementById('lbl-stat-shots-home').textContent = shotH;
    document.getElementById('lbl-stat-shots-away').textContent = shotA;
    const shotTotal = shotH + shotA;
    document.getElementById('bar-stat-shots').style.width = shotTotal > 0 ? `${(shotH / shotTotal) * 100}%` : '50%';
    
    const sotH = findStat(homeStats, 'Shots on Goal') || 0;
    const sotA = findStat(awayStats, 'Shots on Goal') || 0;
    document.getElementById('lbl-stat-sot-home').textContent = sotH;
    document.getElementById('lbl-stat-sot-away').textContent = sotA;
    const sotTotal = sotH + sotA;
    document.getElementById('bar-stat-sot').style.width = sotTotal > 0 ? `${(sotH / sotTotal) * 100}%` : '50%';
    
    const cornH = findStat(homeStats, 'Corner Kicks') || 0;
    const cornA = findStat(awayStats, 'Corner Kicks') || 0;
    document.getElementById('lbl-stat-corners-home').textContent = cornH;
    document.getElementById('lbl-stat-corners-away').textContent = cornA;
    const cornTotal = cornH + cornA;
    document.getElementById('bar-stat-corners').style.width = cornTotal > 0 ? `${(cornH / cornTotal) * 100}%` : '50%';
    
    const redH = findStat(homeStats, 'Red Cards') || 0;
    const redA = findStat(awayStats, 'Red Cards') || 0;
    document.getElementById('lbl-stat-reds-home').textContent = redH;
    document.getElementById('lbl-stat-reds-away').textContent = redA;
    const redTotal = redH + redA;
    document.getElementById('bar-stat-reds').style.width = redTotal > 0 ? `${(redH / redTotal) * 100}%` : '50%';
}


function switchTab(tabId) {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
    const section = document.getElementById('section-' + tabId);
    if(section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function switchSubTab(subTabId) {
    document.querySelectorAll('.sub-tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.sub-tab').forEach(t => t.classList.remove('active'));
    
    document.getElementById(`subtab-content-${subTabId}`).classList.add('active');
    document.getElementById(`subtab-${subTabId}`).classList.add('active');
    activeSubTab = subTabId;
}

function populateDropdowns() {
    const homeSelect = document.getElementById('home-select');
    const awaySelect = document.getElementById('away-select');
    
    if (!homeSelect || !awaySelect) return;
    
    homeSelect.innerHTML = '';
    awaySelect.innerHTML = '';
    
    const teamNames = Object.keys(MODEL_DATA.current_elos).sort();
    
    teamNames.forEach(team => {
        const opt1 = document.createElement('option');
        opt1.value = team;
        opt1.textContent = `${team} (Elo: ${Math.round(MODEL_DATA.current_elos[team])})`;
        homeSelect.appendChild(opt1);
        
        const opt2 = document.createElement('option');
        opt2.value = team;
        opt2.textContent = `${team} (Elo: ${Math.round(MODEL_DATA.current_elos[team])})`;
        awaySelect.appendChild(opt2);
    });
    
    if (teamNames.length > 1) {
        homeSelect.selectedIndex = teamNames.indexOf('Argentina');
        awaySelect.selectedIndex = teamNames.indexOf('France');
    }
    
    handlePredictorTeamChange();
}

function handlePredictorTeamChange() {
    const home = document.getElementById('home-select').value;
    const away = document.getElementById('away-select').value;
    
    document.getElementById('jersey-lbl-home-name').textContent = home;
    document.getElementById('jersey-lbl-away-name').textContent = away;
    
    updateJerseyColors('jersey-home-preview', home);
    updateJerseyColors('jersey-away-preview', away);
}

function handlePredictSubmit(e) {
    e.preventDefault();
    const home = document.getElementById('home-select').value;
    const away = document.getElementById('away-select').value;
    
    if (home === away) {
        alert("Please select two different countries!");
        return;
    }
    
    selectedHome = home;
    selectedAway = away;
    
    const calculateBtn = document.getElementById('btn-calculate-predictions');
    calculateBtn.disabled = true;
    calculateBtn.textContent = 'Calculating Forecast...';
    
    setTimeout(async () => {
        try {
            const prediction = predictPreMatch(home, away);
            displayPreMatchResults(prediction);
            
            // Fetch Powerplayer Prediction from backend
            try {
                const response = await fetch(`/api/powerplayer?home=${encodeURIComponent(home)}&away=${encodeURIComponent(away)}`);
                const data = await response.json();
                if (data.success) {
                    document.getElementById('powerplayer-dashboard').style.display = 'block';
                    document.getElementById('lbl-powerplayer-name').textContent = data.data.power_player;
                    document.getElementById('lbl-powerplayer-team').textContent = data.data.team;
                    document.getElementById('lbl-powerplayer-rating').textContent = data.data.predicted_rating.toFixed(1);
                    document.getElementById('lbl-powerplayer-reason').textContent = data.data.reason;
                }
            } catch (e) {
                console.warn("Failed to fetch Powerplayer:", e);
                document.getElementById('powerplayer-dashboard').style.display = 'none';
            }
            
        } catch (err) {
            console.error('Prediction failed:', err);
        } finally {
            calculateBtn.disabled = false;
            calculateBtn.textContent = 'Calculate AI Forecast';
        }
    }, 450);
}

function displayPreMatchResults(pred) {
    const resultPanel = document.getElementById('pre-match-result');
    resultPanel.classList.remove('hidden');
    
    const hProb = Math.round(pred.home_win_prob * 100);
    const dProb = Math.round(pred.draw_prob * 100);
    const aProb = Math.round(pred.away_win_prob * 100);
    
    document.getElementById('lbl-prob-home').textContent = `${hProb}%`;
    document.getElementById('lbl-prob-draw').textContent = `${dProb}%`;
    document.getElementById('lbl-prob-away').textContent = `${aProb}%`;
    
    document.getElementById('bar-prob-home').style.width = `${hProb}%`;
    document.getElementById('bar-prob-draw').style.width = `${dProb}%`;
    document.getElementById('bar-prob-away').style.width = `${aProb}%`;
    
    document.getElementById('lbl-predicted-score').textContent = pred.predicted_score;
    document.getElementById('lbl-xg-home').textContent = pred.expected_goals_home.toFixed(2);
    document.getElementById('lbl-xg-away').textContent = pred.expected_goals_away.toFixed(2);
    
    // Load analytical factors insights on sidebar
    const container = document.getElementById('prediction-factors-container');
    container.innerHTML = `
        <div class="stats-list-item">
            <span class="item-name">Elo Rating Gap</span>
            <span class="item-val" style="color:var(--accent-gold);">${Math.round(pred.factors.elo_diff)}</span>
        </div>
        <div class="stats-list-item">
            <span class="item-name">${pred.home_team} Form (Last 5)</span>
            <span class="item-val">${pred.factors.home_form_points.toFixed(1)} PPG</span>
        </div>
        <div class="stats-list-item">
            <span class="item-name">${pred.away_team} Form (Last 5)</span>
            <span class="item-val">${pred.factors.away_form_points.toFixed(1)} PPG</span>
        </div>
        <div class="stats-list-item">
            <span class="item-name">H2H Goal Differential</span>
            <span class="item-val">${pred.factors.h2h_diff > 0 ? '+' : ''}${pred.factors.h2h_diff.toFixed(1)}</span>
        </div>
    `;
}

function launchQuickSimulation() {
    if (!selectedHome || !selectedAway) return;
    activeBracketMatch = null;
    selectFixture(selectedHome, selectedAway);
}

function initTickerMatches() {
    const tickerContainer = document.getElementById('ticker-matches-container');
    if (!tickerContainer) return;
    
    tickerContainer.innerHTML = `
        <span class="ticker-match"><span class="ticker-dot"></span> USA 0 - 0 COL (LIVE)</span>
        <span class="ticker-match">ARG 2 - 1 CRO</span>
        <span class="ticker-match">FRA 3 - 1 NED</span>
        <span class="ticker-match">BRA 2 - 0 ITA</span>
        <span class="ticker-match">ENG 1 - 0 POR</span>
        <span class="ticker-match">ESP 2 - 2 DEN</span>
        <span class="ticker-match">GER 3 - 0 CHI</span>
    `;
}

// ----------------------------------------------------
// Visual Charts & Manual dashboard loaders
// ----------------------------------------------------

function initCharts() {
    const liveCtx = document.getElementById('live-prediction-chart');
    if (liveCtx) {
        liveChart = new Chart(liveCtx, {
            type: 'line',
            data: {
                labels: [0],
                datasets: [
                    {
                        label: 'Home Win %',
                        data: [33],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.03)',
                        borderWidth: 3,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.3
                    },
                    {
                        label: 'Draw %',
                        data: [33],
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.03)',
                        borderWidth: 3,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.3
                    },
                    {
                        label: 'Away Win %',
                        data: [34],
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.03)',
                        borderWidth: 3,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.04)' },
                        ticks: { color: '#a7f3d0', font: { family: 'Inter', size: 10 } }
                    },
                    y: {
                        min: 0, max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.04)' },
                        ticks: { color: '#a7f3d0', font: { family: 'Inter', size: 10 } }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
}

let manualData = null;
let activeManualSection = 'predictor';

function fetchManual() {
    try {
        manualData = MODEL_DATA.manual;
        renderManualNav();
        renderManualContent(activeManualSection);
    } catch (e) {
        console.error('Error loading manual:', e);
    }
}

function renderManualNav() {
    const chaptersList = document.getElementById('manual-chapters-list');
    if (!chaptersList || !manualData) return;
    
    chaptersList.innerHTML = '';
    
    manualData.sections.forEach(sec => {
        const btn = document.createElement('button');
        btn.className = `manual-nav-item ${activeManualSection === sec.id ? 'active' : ''}`;
        btn.onclick = () => selectManualSection(sec.id);
        btn.innerHTML = `<span>${sec.icon}</span> ${sec.title}`;
        chaptersList.appendChild(btn);
    });
    
    const faqBtn = document.createElement('button');
    faqBtn.className = `manual-nav-item ${activeManualSection === 'faq' ? 'active' : ''}`;
    faqBtn.onclick = () => selectManualSection('faq');
    faqBtn.innerHTML = `<span>❓</span> Interactive FAQs`;
    chaptersList.appendChild(faqBtn);
}

function selectManualSection(sectionId) {
    activeManualSection = sectionId;
    renderManualNav();
    renderManualContent(sectionId);
}

function renderManualContent(sectionId) {
    const contentView = document.getElementById('manual-content-view');
    if (!contentView || !manualData) return;
    
    contentView.innerHTML = '';
    
    if (sectionId === 'faq') {
        const headerHTML = `
            <h2 class="widget-title" style="margin-bottom: 0.5rem; font-size: 1.5rem;">❓ Interactive Frequently Asked Questions</h2>
            <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">Click on any question to view the answer.</p>
        `;
        
        let faqsHTML = '<div class="faq-accordion">';
        manualData.faqs.forEach((faq, index) => {
            faqsHTML += `
                <div class="faq-item" id="faq-item-${index}">
                    <button class="faq-header" onclick="toggleFaqAccordion(${index})">
                        <span>${faq.q}</span>
                        <span class="faq-toggle-icon">▼</span>
                    </button>
                    <div class="faq-body">
                        <div class="faq-content">${faq.a}</div>
                    </div>
                </div>
            `;
        });
        faqsHTML += '</div>';
        
        contentView.innerHTML = headerHTML + faqsHTML;
        
    } else {
        const section = manualData.sections.find(s => s.id === sectionId);
        if (!section) return;
        
        const headerHTML = `
            <div style="display:flex; align-items:center; gap: 0.75rem; margin-bottom: 0.5rem;">
                <span style="font-size: 2rem;">${section.icon}</span>
                <h2 style="font-size: 1.5rem; font-weight:800; color: #fff; margin:0;">${section.title}</h2>
            </div>
            <p style="color: var(--text-secondary); font-weight:600; font-size: 0.95rem; margin-bottom: 0.5rem;">${section.subtitle}</p>
            <p style="color: var(--text-muted); font-size: 0.9rem; line-height:1.6; margin-bottom: 1.5rem;">${section.description}</p>
        `;
        
        let contentHTML = '';
        
        if (section.steps) {
            contentHTML += '<div class="stepper-timeline">';
            section.steps.forEach(step => {
                contentHTML += `
                    <div class="stepper-step">
                        <div class="step-badge">${step.num}</div>
                        <div class="step-card">
                            <div class="step-title">${step.title}</div>
                            <div class="step-desc">${step.desc}</div>
                        </div>
                    </div>
                `;
            });
            contentHTML += '</div>';
        } else if (section.details) {
            contentHTML += '<div class="math-grid">';
            section.details.forEach(detail => {
                contentHTML += `
                    <div class="math-card">
                        <h3 style="color: #fff; font-size: 1.1rem; font-weight:700; margin-bottom: 0.5rem;">${detail.name}</h3>
                        <div class="math-formula-box">${detail.formula}</div>
                        <p style="color: var(--text-secondary); font-size: 0.85rem; line-height: 1.5; margin-top: 0.75rem;">${detail.desc}</p>
                    </div>
                `;
            });
            contentHTML += '</div>';
        }
        
        contentView.innerHTML = headerHTML + contentHTML;
    }
}

function toggleFaqAccordion(index) {
    const item = document.getElementById(`faq-item-${index}`);
    if (!item) return;
    
    const isActive = item.classList.contains('active');
    
    document.querySelectorAll('.faq-item').forEach(el => {
        el.classList.remove('active');
        const body = el.querySelector('.faq-body');
        if (body) body.style.maxHeight = null;
    });
    
    if (!isActive) {
        item.classList.add('active');
        const body = item.querySelector('.faq-body');
        if (body) {
            body.style.maxHeight = body.scrollHeight + "px";
        }
    }
}

// ----------------------------------------------------
// Page Loader DomContentLoaded
// ----------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    populateDropdowns();
    initTournament();
    initCharts();
    fetchManual();
    initPlayersHub();
});


// --- NEW ADVANCED LOGIC: SSE & LEADERBOARDS ---
let GLOBAL_PLAYERS_DB = {};

async function loadPlayersData() {
    try {
        const response = await fetch('/static/data/players_db.json');
        GLOBAL_PLAYERS_DB = await response.json();
    } catch (err) {
        console.warn("Failed to load players_db.json, using fallback mocks.", err);
    }
}

function populateLeaderboards() {
    const teamBody = document.getElementById('team-leaderboard-body');
    const playerList = document.getElementById('player-leaderboard-list');
    
    if (!teamBody || !playerList) return;
    
    // Team Leaderboard
    const teams = Object.keys(MODEL_DATA.current_elos).map(t => {
        const elo = MODEL_DATA.current_elos[t];
        const strength = MODEL_DATA.strengths[t] || {};
        const xg = strength.home_attack || 1.5;
        return { name: t, elo, xg };
    }).sort((a, b) => b.elo - a.elo).slice(0, 10);
    
    teamBody.innerHTML = '';
    teams.forEach((t, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>#${i + 1}</strong></td>
            <td><span class="flag-icon">${getFlagEmoji(t.name)}</span> ${t.name}</td>
            <td><strong style="color:var(--accent-gold);">${Math.round(t.elo)}</strong></td>
            <td>${t.xg.toFixed(2)}</td>
        `;
        teamBody.appendChild(tr);
    });
    
    // Player Leaderboard
    let allPlayers = [];
    if (Object.keys(GLOBAL_PLAYERS_DB).length > 0) {
        Object.values(GLOBAL_PLAYERS_DB).forEach(teamArr => {
            allPlayers.push(...teamArr);
        });
    } else {
        MODEL_DATA.players.forEach(p => {
            allPlayers.push({ name: p.name, rating: p.rating, team: p.country, photo: '/static/img/player_visionary.png' });
        });
    }
    
    allPlayers.sort((a, b) => b.rating - a.rating);
    const topPlayers = allPlayers.slice(0, 10);
    
    playerList.innerHTML = '';
    topPlayers.forEach((p, i) => {
        const div = document.createElement('div');
        div.className = 'timeline-event';
        div.innerHTML = `
            <div style="display:flex; align-items:center; gap: 1rem; width: 100%;">
                <div style="font-weight:800; color:var(--text-muted);">#${i+1}</div>
                <img src="${p.photo}" alt="${p.name}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid var(--accent-brand);">
                <div style="flex:1;">
                    <div style="font-weight: 700;">${p.name}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">${p.team || p.country}</div>
                </div>
                <div style="font-size: 1.25rem; font-weight: 800; color: var(--accent-gold);">${p.rating.toFixed(1)}</div>
            </div>
        `;
        playerList.appendChild(div);
    });
}

function initLiveTrackingSSE() {
    if (!!window.EventSource) {
        var source = new EventSource('/api/live-stream');
        source.onmessage = function(e) {
            console.log("SSE Live Tracker Update:", e.data);
            // In a real app, update DOM elements with live scores here.
            // document.getElementById('live-indicator').classList.add('pulse');
        };
        source.onerror = function(e) {
            console.warn("SSE disconnected, attempting reconnect...");
        };
    } else {
        console.warn("Your browser does not support Server-Sent Events.");
    }
}

// Ensure these run on load
document.addEventListener('DOMContentLoaded', () => {
    loadPlayersData().then(() => {
        populateLeaderboards();
    });
    initLiveTrackingSSE();
});
