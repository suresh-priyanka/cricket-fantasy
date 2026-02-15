#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import sys
import os
from datetime import date
from thefuzz import process
import matplotlib.pyplot as plt

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================
pd.set_option('display.max_colwidth', 200)

if len(sys.argv) > 1:
    group = sys.argv[1]
else:
    group = 'group_1' 

# Date Logic
ipl_day_0 = date(2026, 2, 6)
ipl_day_cur = date.today()
day_num = abs((ipl_day_cur - ipl_day_0).days)
day = 'day_' + str(day_num)
prev_day = 'day_' + str(day_num - 1)

# --- SMART FALLBACK ---
if not os.path.exists(f'./data/mvp_{day}.csv'):
    day = prev_day 
    prev_day_num = int(day.split('_')[1]) - 1
    prev_day = f'day_{prev_day_num}'
    if not os.path.exists(f'./data/mvp_{day}.csv'):
         day = 'day_1'
         prev_day = 'day_0'

tournament = 't20_wc_2026'
leaderboard_graph_file = f'./{group}/{tournament}_leaderboard.png'
leaderboard_file = f'./{group}/{tournament}_leaderboard.txt'
ipl_mock_auction_summary = f'./{group}/AuctionSummary.csv'

# ==========================================
# 2. LOAD & CALCULATE
# ==========================================
mvp_df = pd.read_csv(f'./data/mvp_{day}.csv')
mvp_df['Player'] = mvp_df['Player'].astype(str).str.lower().str.strip()

fantasy_teams_auction_df = pd.read_csv(ipl_mock_auction_summary)
fantasy_mgrs = fantasy_teams_auction_df.columns.to_list()
fantasy_teams_df = fantasy_teams_auction_df.apply(lambda x: x.astype(str).str.lower().str.strip())

scores = { mgr:0 for mgr in fantasy_mgrs }
ownership_list = []

for mgr in fantasy_mgrs:
    mvp_players_list = mvp_df['Player'].to_list()
    for i in range(len(fantasy_teams_df[mgr])):
        player_name = str(fantasy_teams_df[mgr].iloc[i])
        pts = 0.0
        if player_name in mvp_players_list:
            pts = float(mvp_df.loc[mvp_df['Player'] == player_name, 'Pts'].iloc[0])
            scores[mgr] += pts
        if player_name != 'nan':
            ownership_list.append({'Player': player_name.title(), 'Manager': mgr, 'Points': pts})

# ==========================================
# 3. GENERATE THE CONSOLIDATED WEB REPORT
# ==========================================
print(f"🚀 Generating Master Report for {day}...")

# Sort Data
scores_sorted = pd.DataFrame(sorted(scores.items(), key=lambda x: x[1], reverse=True), columns=['Manager', 'Total Points'])
ownership_sorted = pd.DataFrame(ownership_list).sort_values(by='Points', ascending=False)

# Build the Markdown String
report_content = f"# 🏏 T20 World Cup 2026 Fantasy Dashboard\n"
report_content += f"**Report Generated on:** {day.replace('_', ' ').upper()}\n\n"

report_content += "## 🏆 Manager Leaderboard\n"
report_content += "The current standings of all managers based on their player performance.\n\n"
report_content += scores_sorted.to_markdown(index=False) + "\n\n"

report_content += "---\n\n"