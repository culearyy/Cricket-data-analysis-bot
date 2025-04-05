import streamlit as st
import pandas as pd
import re
import os
import plotly.express as px

# ------------------------------------------------------------------------------
# Streamlit page configuration
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Cricket Analysis Chatbot", layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------------------
# Load CSV
# ------------------------------------------------------------------------------
data_file = r"cricket_statsnew2.csv"
if not os.path.exists(data_file):
    st.error(f"File '{data_file}' not found.")
    st.stop()

df = pd.read_csv(data_file)
df.columns = [col.lower() for col in df.columns]
df['player'] = df['player'].fillna("")
df = df.drop_duplicates(subset=['player'])

# ------------------------------------------------------------------------------
# Helper Functions (Text Responses)
# ------------------------------------------------------------------------------
def get_health_status(player_name):
    player_row = df[df['player'].str.contains(player_name.strip(), case=False)]
    if not player_row.empty:
        return player_row.iloc[0]['health_status']
    return "Unknown"

def get_player_stat(player_name, stat):
    player_row = df[df['player'].str.contains(player_name.strip(), case=False)]
    if not player_row.empty:
        if stat in df.columns:
            return player_row.iloc[0][stat]
        else:
            return f"Stat '{stat}' not found."
    return f"Player '{player_name}' not found."

def get_highest_stat_player(stat, role=None):
    if stat not in df.columns:
        return f"Stat '{stat}' not found."
    if role == 'batsman':
        filtered_df = df[df['runs'] > 100]
    elif role == 'bowler':
        filtered_df = df[df['wickets'] > 0]
    else:
        filtered_df = df
    max_value = filtered_df[stat].max()
    top_player = filtered_df[filtered_df[stat] == max_value].iloc[0]
    health_status = top_player['health_status']
    return f"{top_player['player']} has the highest {stat}: {max_value} (Health: {health_status})"

def get_best_allrounder():
    all_rounders_df = df[(df['runs'] > 100) & (df['wickets'] > 10)]
    if all_rounders_df.empty:
        return "No qualified all-rounders found."
    all_rounders_df['allrounder_rating'] = (
        all_rounders_df['ave'] * all_rounders_df['sr'] / 100
        + all_rounders_df['wickets'] * 10
    )
    best_allrounder = all_rounders_df.sort_values(by='allrounder_rating', ascending=False).iloc[0]
    health_status = best_allrounder['health_status']
    return (f"The best all-rounder is {best_allrounder['player']} "
            f"with {best_allrounder['runs']} runs and {best_allrounder['wickets']} wickets "
            f"(Health: {health_status})")

def compare_players(player1, player2, stat):
    player1_row = df[df['player'].str.contains(player1.strip(), case=False)]
    player2_row = df[df['player'].str.contains(player2.strip(), case=False)]
    if player1_row.empty or player2_row.empty:
        return "One or both players not found."
    if stat not in df.columns:
        return f"Stat '{stat}' not found."
    player1_stat = player1_row.iloc[0][stat]
    player2_stat = player2_row.iloc[0][stat]
    return (f"{player1_row.iloc[0]['player']}'s {stat}: {player1_stat}\n"
            f"{player2_row.iloc[0]['player']}'s {stat}: {player2_stat}")

def best_playing_xi(pitch_type):
    pitch_type = pitch_type.lower()
    if pitch_type == 'spin':
        bowlers = (df[df['economy'] < 4.5]
                   .sort_values(by=['wickets', 'economy'], ascending=[False, True])
                   .head(3)['player'].tolist())
        batsmen = df.sort_values(by='runs', ascending=False).head(6)['player'].tolist()
        allrounders = ['RA Jadeja', 'Washington Sundar']
    elif pitch_type == 'fast':
        bowlers = (df[df['economy'] < 5.5]
                   .sort_values(by=['wickets', 'economy'], ascending=[False, True])
                   .head(3)['player'].tolist())
        batsmen = df.sort_values(by='sr', ascending=False).head(6)['player'].tolist()
        allrounders = ['HH Pandya', 'SN Thakur']
    elif pitch_type == 'dew':
        bowlers = (df[df['economy'] < 5.0]
                   .sort_values(by='economy')
                   .head(3)['player'].tolist())
        batsmen = df.sort_values(by='ave', ascending=False).head(6)['player'].tolist()
        allrounders = ['AR Patel', 'Washington Sundar']
    elif pitch_type == 'slow':
        bowlers = (df[df['economy'] < 6.0]
                   .sort_values(by=['economy', 'wickets'], ascending=[True, False])
                   .head(3)['player'].tolist())
        batsmen = df.sort_values(by='hs', ascending=False).head(6)['player'].tolist()
        allrounders = ['RA Jadeja', 'Kuldeep Yadav']
    else:
        return "Pitch type not recognized. Please specify spin/fast/dew/slow."
    response = f"Best Playing XI for a {pitch_type}-friendly pitch:\n"
    for player in (batsmen + allrounders + bowlers):
        health_status = get_health_status(player)
        response += f"- {player} (Health: {health_status})\n"
    return response.strip()

def top_n_players(role='batsman', n=5):
    role = role.lower()
    if role in ['batsman', 'batsmen', 'batter', 'batters']:
        sorted_df = df.sort_values(by='runs', ascending=False).head(n)
        role_type = 'Batsman'
    elif role in ['bowler', 'bowlers']:
        sorted_df = (df.sort_values(by=['wickets', 'economy'], ascending=[False, True])
                     .head(n))
        role_type = 'Bowler'
    else:
        return f"Role '{role}' not recognized. Please specify either batsman or bowlers."
    response = f"Top {n} {role_type}:\n"
    for _, row in sorted_df.iterrows():
        if role_type.lower() == 'batsman':
            stat = f"{row['runs']} runs"
        else:
            stat = f"{row['wickets']} wickets at Economy {row['economy']}"
        response += f"- {row['player']} ({stat}, Health: {row['health_status']})\n"
    return response.strip()

def most_fit_player():
    fit_players = df[df['health_status'] == 'Fully Fit']
    if fit_players.empty:
        return "No fully fit players found."
    top_fit_player = fit_players.sort_values(by='mat', ascending=False).iloc[0]
    return (f"The most fit player currently is {top_fit_player['player']} "
            f"(Matches Played: {top_fit_player['mat']}).")

def answer_question(question):
    question_lower = question.lower()
    # Health Status Query
    health_match = re.match(r".*health[_ ]?status.*of\s+([\w\s\.]+)\??", question_lower)
    if health_match:
        player_name = health_match.group(1).strip()
        status = get_health_status(player_name)
        if status == "Unknown":
            return f"Player '{player_name}' not found or health status unavailable."
        return f"{player_name}'s current Health Status: {status}"
    # Specific Player Stat Query
    stat_match = re.match(r".*what is the (\w+) of ([\w\s\.]+)\??", question_lower)
    if stat_match:
        stat = stat_match.group(1).strip().lower()
        player_name = stat_match.group(2).strip()
        result = get_player_stat(player_name, stat)
        return f"{player_name}'s {stat}: {result}"
    # Highest Stat Query for Batsmen
    highest_batsman_match = re.search(r"which\s+batsman\s+has\s+(?:the\s+)?highest\s+(\w+)", question_lower)
    if highest_batsman_match:
        stat = highest_batsman_match.group(1).lower()
        return get_highest_stat_player(stat, role='batsman')
    # Highest Stat Query for Bowlers
    highest_bowler_match = re.search(r"which\s+bowler\s+has\s+(?:the\s+)?highest\s+(\w+)", question_lower)
    if highest_bowler_match:
        stat = highest_bowler_match.group(1).lower().rstrip('s')
        return get_highest_stat_player(stat, role='bowler')
    # Best All-rounder Query
    allrounder_match = re.search(r"(?:which|who)\s+is\s+(?:the\s+)?best\s+all[\s-]rounder", question_lower)
    if allrounder_match:
        return get_best_allrounder()
    # Player Comparison Query
    compare_match = re.search(r"compare\s+([\w\s\.]+)\s+and\s+([\w\s\.]+)(?:'s)?\s+(\w+)", question_lower)
    if compare_match:
        player1 = compare_match.group(1).strip()
        player2 = compare_match.group(2).strip()
        stat = compare_match.group(3).strip()
        return compare_players(player1, player2, stat)
    # Best Playing XI Query
    xi_match = re.match(r".*best playing xi.*(spin|fast|dew|slow).*pitch.*", question_lower)
    if xi_match:
        pitch_type = xi_match.group(1)
        return best_playing_xi(pitch_type)
    # Top N Players Query
    top_n_match = re.search(r"top\s+(\d+)\s+(batsmen|batsman|bowlers|bowler)", question_lower)
    if top_n_match:
        n = int(top_n_match.group(1))
        role = top_n_match.group(2)
        return top_n_players(role=role, n=n)
    # Most Fit Player Query
    fit_match = re.match(r".*most fit player.*", question_lower)
    if fit_match:
        return most_fit_player()
    return "Sorry! I couldn't understand your query."

# ------------------------------------------------------------------------------
# Plotting Functions
# ------------------------------------------------------------------------------
def plot_multiple_players_stats(players_list, stat, title=""):
    """
    Creates a bar chart comparing the given stat for multiple players.
    Non-numeric values will be shown as None.
    """
    data = []
    for player in players_list:
        val = get_player_stat(player, stat)
        # Attempt to convert to float
        try:
            val = float(val)
        except (ValueError, TypeError):
            val = None
        data.append({"Player": player, stat: val})
    
    chart_df = pd.DataFrame(data)
    fig = px.bar(
        chart_df,
        x="Player",
        y=stat,
        text=stat,
        title=title if title else f"{stat.capitalize()} Comparison",
        color="Player",
        height=500
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(yaxis_title=stat.capitalize(), xaxis_title="Player")
    return fig

# ------------------------------------------------------------------------------
# Main UI Layout using Tabs and Containers
# ------------------------------------------------------------------------------
st.sidebar.title("Cricket Analysis Chatbot")
st.sidebar.markdown(
    """
**Welcome!**  
Use the **Chatbot** tab to ask cricket stat questions.  
Or explore quick stats and visualizations in the **Stats Explorer** tab.
"""
)

tabs = st.tabs(["Chatbot", "Stats Explorer"])

# ------------------ CHATBOT TAB ------------------
with tabs[0]:
    st.header("Cricket Stats Chatbot")
    if "history" not in st.session_state:
        st.session_state.history = []
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your question:")
        submitted = st.form_submit_button("Send")
    
    if submitted:
        if user_input.lower() in ["exit", "quit"]:
            st.info("Goodbye!")
        else:
            response = answer_question(user_input)
            st.session_state.history.append(("You", user_input))
            st.session_state.history.append(("Bot", response))
            # If the question is a compare query, we might show a chart
            if "compare" in user_input.lower():
                cmp_match = re.search(r"compare\s+([\w\s\.]+)\s+and\s+([\w\s\.]+)(?:'s)?\s+(\w+)", user_input.lower())
                if cmp_match:
                    p1 = cmp_match.group(1).strip()
                    p2 = cmp_match.group(2).strip()
                    stat = cmp_match.group(3).strip()
                    fig = plot_multiple_players_stats([p1, p2], stat,
                          title=f"Comparison of {stat.capitalize()} for {p1} and {p2}")
                    # Only show chart if stat is numeric
                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True)
    
    # Display conversation
    for speaker, message in st.session_state.history:
        if speaker == "You":
            st.markdown(
                f"<div style='background-color:#e8f5e9; padding:10px; border-radius:5px; margin-bottom:5px'>"
                f"<strong>You:</strong> {message}</div>", unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='background-color:#e3f2fd; padding:10px; border-radius:5px; margin-bottom:5px'>"
                f"<strong>Bot:</strong> {message}</div>", unsafe_allow_html=True
            )

# ------------------ STATS EXPLORER TAB ------------------
with tabs[1]:
    st.header("Quick Stats Explorer")
    st.markdown("Explore cricket stats and view visualizations with the interactive widgets below.")
    
    # ---- Existing Quick Stats (Top players, best playing XI, etc.) ----
    col1, col2 = st.columns([1, 2])
    with col1:
        role_option = st.selectbox("Select role:", ["-- select --", "Top Batsmen", "Top Bowlers"])
        num_option = st.slider("Number of players:", 1, 10, 5)
        action = st.radio("Action:", ("Show Top Players", "Show Most Fit Player"))
    with col2:
        if action == "Show Top Players":
            if role_option == "Top Batsmen":
                st.write(top_n_players("batsman", num_option))
            elif role_option == "Top Bowlers":
                st.write(top_n_players("bowler", num_option))
            else:
                st.warning("Please select a valid role.")
        else:
            st.write(most_fit_player())
    
    st.markdown("---")
    st.subheader("Best Playing XI by Pitch Type")
    pitch_type = st.selectbox("Select Pitch Type:", ["-- select --", "Spin", "Fast", "Dew", "Slow"])
    if pitch_type != "-- select --":
        st.write(best_playing_xi(pitch_type.lower()))
    
    # ---- New: Batters Visualization ----
    st.markdown("---")
    st.subheader("Batters Visualization")
    # Filter to players with some batting data (e.g., runs > 0). You can tweak as needed.
    batters_list = df[df['runs'] > 0]['player'].unique().tolist()
    selected_batters = st.multiselect("Select Batters to Compare:", options=sorted(batters_list), default=None)
    # Common batting stats: runs, ave, sr, hs
    batting_stats = ["runs", "ave", "sr", "hs"]
    selected_batting_stat = st.selectbox("Select Batting Stat:", batting_stats)
    
    if st.button("Show Batters Chart"):
        if selected_batters:
            fig_bat = plot_multiple_players_stats(selected_batters, selected_batting_stat,
                        title=f"Batters: {selected_batting_stat.capitalize()} Comparison")
            st.plotly_chart(fig_bat, use_container_width=True)
        else:
            st.warning("Please select at least one batter.")

    # ---- New: Bowlers Visualization ----
    st.markdown("---")
    st.subheader("Bowlers Visualization")
    # Filter to players with some bowling data (e.g., wickets > 0). Adjust as needed.
    bowlers_list = df[df['wickets'] > 0]['player'].unique().tolist()
    selected_bowlers = st.multiselect("Select Bowlers to Compare:", options=sorted(bowlers_list), default=None)
    # Common bowling stats: wickets, economy, ave, sr
    bowling_stats = ["wickets", "economy", "ave", "sr"]
    selected_bowling_stat = st.selectbox("Select Bowling Stat:", bowling_stats)
    
    if st.button("Show Bowlers Chart"):
        if selected_bowlers:
            fig_bowl = plot_multiple_players_stats(selected_bowlers, selected_bowling_stat,
                        title=f"Bowlers: {selected_bowling_stat.capitalize()} Comparison")
            st.plotly_chart(fig_bowl, use_container_width=True)
        else:
            st.warning("Please select at least one bowler.")
