import streamlit as st
import pandas as pd
import re
import os
import matplotlib.pyplot as plt
import seaborn as sns

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
# Helper Functions
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
        all_rounders_df['ave'] * all_rounders_df['sr'] / 100 + all_rounders_df['wickets'] * 10
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
# Visualization Functions
# ------------------------------------------------------------------------------
def plot_batting_stats(players=None, stat='runs'):
    if players is None:
        # Get top 10 players by the selected stat
        players_df = df.sort_values(by=stat, ascending=False).head(10)
    else:
        players_df = df[df['player'].isin(players)]
    
    if players_df.empty:
        st.error("No players found with the selected criteria.")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='player', y=stat, data=players_df, ax=ax)
    ax.set_title(f'Comparison of {stat.title()} for Selected Players')
    ax.set_xlabel('Player')
    ax.set_ylabel(stat.title())
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

def plot_bowling_stats(players=None, stat='wickets'):
    if players is None:
        # Get top 10 players by the selected stat
        players_df = df.sort_values(by=stat, ascending=False).head(10)
    else:
        players_df = df[df['player'].isin(players)]
    
    if players_df.empty:
        st.error("No players found with the selected criteria.")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='player', y=stat, data=players_df, ax=ax)
    ax.set_title(f'Comparison of {stat.title()} for Selected Players')
    ax.set_xlabel('Player')
    ax.set_ylabel(stat.title())
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

def plot_player_comparison(player1, player2):
    player1_data = df[df['player'].str.contains(player1, case=False)]
    player2_data = df[df['player'].str.contains(player2, case=False)]
    
    if player1_data.empty or player2_data.empty:
        st.error("One or both players not found.")
        return
    
    # Select relevant stats for comparison
    batting_stats = ['runs', 'ave', 'sr', 'hs']
    bowling_stats = ['wickets', 'economy', 'bowling_ave']
    
    # Create comparison dataframe
    comparison_data = []
    
    for stat in batting_stats + bowling_stats:
        if stat in df.columns:
            try:
                p1_value = float(player1_data.iloc[0][stat])
                p2_value = float(player2_data.iloc[0][stat])
                comparison_data.append({
                    'Stat': stat,
                    player1_data.iloc[0]['player']: p1_value,
                    player2_data.iloc[0]['player']: p2_value
                })
            except (ValueError, TypeError):
                pass
    
    comparison_df = pd.DataFrame(comparison_data)
    
    if comparison_df.empty:
        st.error("No comparable stats found for these players.")
        return
    
    # Plot batting stats
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Filter for batting stats
    batting_df = comparison_df[comparison_df['Stat'].isin(batting_stats)]
    if not batting_df.empty:
        batting_df = batting_df.melt(id_vars=['Stat'], var_name='Player', value_name='Value')
        sns.barplot(x='Stat', y='Value', hue='Player', data=batting_df, ax=axes[0])
        axes[0].set_title('Batting Stats Comparison')
        axes[0].set_xlabel('Stat')
        axes[0].set_ylabel('Value')
        axes[0].tick_params(axis='x', rotation=45)
    
    # Filter for bowling stats
    bowling_df = comparison_df[comparison_df['Stat'].isin(bowling_stats)]
    if not bowling_df.empty:
        bowling_df = bowling_df.melt(id_vars=['Stat'], var_name='Player', value_name='Value')
        sns.barplot(x='Stat', y='Value', hue='Player', data=bowling_df, ax=axes[1])
        axes[1].set_title('Bowling Stats Comparison')
        axes[1].set_xlabel('Stat')
        axes[1].set_ylabel('Value')
        axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)

def plot_health_distribution():
    health_counts = df['health_status'].value_counts()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=health_counts.index, y=health_counts.values, ax=ax)
    ax.set_title('Distribution of Player Health Status')
    ax.set_xlabel('Health Status')
    ax.set_ylabel('Number of Players')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# ------------------------------------------------------------------------------
# Main UI Layout using Tabs and Containers
# ------------------------------------------------------------------------------
# Sidebar: App header and instructions
st.sidebar.title("Cricket Analysis Chatbot")
st.sidebar.markdown(
    """
    **Welcome!** Use the **Chatbot** tab to ask cricket stat questions.
    Alternatively, explore quick stats in the **Stats Explorer** tab.
    """
)

# Create two tabs: one for the Chatbot, another for exploring stats
tabs = st.tabs(["Chatbot", "Stats Explorer"])

with tabs[0]:
    st.header("Cricket Stats Chatbot")
    
    # Conversation history container
    if "history" not in st.session_state:
        st.session_state.history = []
    
    # Chat form: users can press Enter or click Send
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
    
    # Display conversation history with improved styling
    for speaker, message in st.session_state.history:
        if speaker == "You":
            st.markdown(f"**You**: {message}")
        else:
            st.markdown(f"**Bot**: {message}")

with tabs[1]:
    st.header("Cricket Stats Explorer")
    
    # Create sub-tabs for different visualization options
    viz_tabs = st.tabs(["Batting Stats", "Bowling Stats", "Player Comparison", "Health Status"])
    
    with viz_tabs[0]:
        st.subheader("Batting Statistics Visualization")
        
        # Select batting stat to visualize
        batting_stat = st.selectbox(
            "Select batting statistic to visualize:",
            ["runs", "ave", "sr", "hs", "4s", "6s"],
            format_func=lambda x: {
                "runs": "Total Runs", 
                "ave": "Batting Average",
                "sr": "Strike Rate",
                "hs": "Highest Score",
                "4s": "Number of Fours",
                "6s": "Number of Sixes"
            }.get(x, x)
        )
        
        # Option to select specific players or view top players
        player_selection = st.radio(
            "Select players to visualize:",
            ["Top 10 Players", "Select Specific Players"],
            key="batting_player_selection"
        )
        
        if player_selection == "Select Specific Players":
            selected_players = st.multiselect(
                "Select players:",
                df['player'].unique(),
                key="batting_selected_players"
            )
            if selected_players:
                plot_batting_stats(players=selected_players, stat=batting_stat)
        else:
            plot_batting_stats(stat=batting_stat)
    
    with viz_tabs[1]:
        st.subheader("Bowling Statistics Visualization")
        
        # Select bowling stat to visualize
        bowling_stat = st.selectbox(
            "Select bowling statistic to visualize:",
            ["wickets", "economy", "bowling_ave"],
            format_func=lambda x: {
                "wickets": "Total Wickets", 
                "economy": "Economy Rate",
                "bowling_ave": "Bowling Average"
            }.get(x, x)
        )
        
        # Option to select specific players or view top players
        player_selection = st.radio(
            "Select players to visualize:",
            ["Top 10 Players", "Select Specific Players"],
            key="bowling_player_selection"
        )
        
        if player_selection == "Select Specific Players":
            selected_players = st.multiselect(
                "Select players:",
                df['player'].unique(),
                key="bowling_selected_players"
            )
            if selected_players:
                plot_bowling_stats(players=selected_players, stat=bowling_stat)
        else:
            plot_bowling_stats(stat=bowling_stat)
    
    with viz_tabs[2]:
        st.subheader("Player Comparison")
        
        # Select players to compare
        player1 = st.selectbox("Select first player:", df['player'].unique(), key="player1")
        player2 = st.selectbox("Select second player:", df['player'].unique(), key="player2")
        
        if player1 and player2:
            plot_player_comparison(player1, player2)
    
    with viz_tabs[3]:
        st.subheader("Health Status Distribution")
        plot_health_distribution()
