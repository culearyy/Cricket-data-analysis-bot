import streamlit as st
import pandas as pd
import re
import os

# ------------------------------------------------------------------------------
# Streamlit page config
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Cricket Analysis Chatbot", layout="wide")

# ------------------------------------------------------------------------------
# Load CSV
# ------------------------------------------------------------------------------
data_file = r"C:\Users\KIIT\Desktop\Advanced Programming\AP Project - Cricket analysis\cricket_statsnew2.csv"

if not os.path.exists(data_file):
    st.error(f"File '{data_file}' not found.")
    st.stop()

df = pd.read_csv(data_file)

# Normalize column names
df.columns = [col.lower() for col in df.columns]

# Fill NaN in 'player' column
df['player'] = df['player'].fillna("")

# Drop duplicates
df = df.drop_duplicates(subset=['player'])

# ------------------------------------------------------------------------------
# Helper functions
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
    # Simple rating
    all_rounders_df['allrounder_rating'] = (
        all_rounders_df['ave'] * all_rounders_df['sr'] / 100
        + all_rounders_df['wickets'] * 10
    )
    best_allrounder = all_rounders_df.sort_values(by='allrounder_rating', ascending=False).iloc[0]
    health_status = best_allrounder['health_status']
    return (
        f"The best all-rounder is {best_allrounder['player']} "
        f"with {best_allrounder['runs']} runs and {best_allrounder['wickets']} wickets "
        f"(Health: {health_status})"
    )

def compare_players(player1, player2, stat):
    player1_row = df[df['player'].str.contains(player1.strip(), case=False)]
    player2_row = df[df['player'].str.contains(player2.strip(), case=False)]
    if player1_row.empty or player2_row.empty:
        return "One or both players not found."
    if stat not in df.columns:
        return f"Stat '{stat}' not found."
    player1_stat = player1_row.iloc[0][stat]
    player2_stat = player2_row.iloc[0][stat]
    return (
        f"{player1_row.iloc[0]['player']}'s {stat}: {player1_stat}\n"
        f"{player2_row.iloc[0]['player']}'s {stat}: {player2_stat}"
    )

def best_playing_xi(pitch_type):
    pitch_type = pitch_type.lower()
    if pitch_type == 'spin':
        bowlers = (df[df['economy'] < 4.5]
                   .sort_values(by=['wickets','economy'], ascending=[False,True])
                   .head(3)['player'].tolist())
        batsmen = df.sort_values(by='runs', ascending=False).head(6)['player'].tolist()
        allrounders = ['RA Jadeja', 'Washington Sundar']
    elif pitch_type == 'fast':
        bowlers = (df[df['economy'] < 5.5]
                   .sort_values(by=['wickets','economy'], ascending=[False,True])
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
                   .sort_values(by=['economy','wickets'], ascending=[True,False])
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
        role_type = 'batsman'
    elif role in ['bowler', 'bowlers']:
        sorted_df = (
            df.sort_values(by=['wickets','economy'], ascending=[False,True])
            .head(n)
        )
        role_type = 'bowlers'
    else:
        return f"Role '{role}' not recognized. Please specify either batsman or bowlers."
    response = f"Top {n} {role_type.capitalize()}:\n"
    for _, row in sorted_df.iterrows():
        if role_type == 'batsman':
            stat = f"{row['runs']} runs"
        else:
            stat = f"{row['wickets']} wickets at Economy {row['economy']}"
        response += (
            f"- {row['player']} ({stat}, Health: {row['health_status']})\n"
        )
    return response.strip()

def most_fit_player():
    fit_players = df[df['health_status'] == 'Fully Fit']
    if fit_players.empty:
        return "No fully fit players found."
    top_fit_player = fit_players.sort_values(by='mat', ascending=False).iloc[0]
    return (
        f"The most fit player currently is {top_fit_player['player']} "
        f"(Matches Played: {top_fit_player['mat']})."
    )

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

    # Fallback
    return "Sorry! I couldn't understand your query."

# ------------------------------------------------------------------------------
# Streamlit layout
# ------------------------------------------------------------------------------

st.sidebar.title("Cricket Analysis Chatbot")
st.sidebar.markdown(
    """
**Instructions:**
- Ask your cricket stats question in the text box below.
- Press **Enter** or click **Send** to submit.
- Examples:
  - "What is the economy of Bumrah?"
  - "Which batsman has the highest SR?"
  - "Best playing XI for spin pitch"
  - "Compare Kohli and Gill's runs"
- Type 'exit' or 'quit' to end the chat session.
"""
)

# A few interactive stats exploration options in the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats Explorer")
role_option = st.sidebar.selectbox(
    "Select role to view top players:",
    ["-- select --", "Top Batsmen", "Top Bowlers"]
)
num_option = st.sidebar.slider("Number of players to display:", 1, 10, 5)

if st.sidebar.button("Show Top Players"):
    if role_option == "Top Batsmen":
        st.sidebar.write(top_n_players("batsman", num_option))
    elif role_option == "Top Bowlers":
        st.sidebar.write(top_n_players("bowler", num_option))
    else:
        st.sidebar.warning("Please select a valid role.")

if st.sidebar.button("Show Most Fit Player"):
    st.sidebar.write(most_fit_player())

# Main title
st.title("Cricket Stats Chatbot with Enhanced NLP")

# Keep a conversation history
if "history" not in st.session_state:
    st.session_state.history = []

# Create a form so Enter triggers submission
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:")
    submitted = st.form_submit_button("Send")

if submitted:
    # Handle user input
    if user_input.lower() in ["exit", "quit"]:
        st.write("Goodbye!")
    else:
        response = answer_question(user_input)
        st.session_state.history.append(("You", user_input))
        st.session_state.history.append(("Bot", response))
    # Force a rerun so the conversation updates

# Display the conversation
for speaker, message in st.session_state.history:
    if speaker == "You":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**Bot:** {message}")
