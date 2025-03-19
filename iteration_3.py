import streamlit as st
import pandas as pd
import re
import os

# File path for the cricket stats CSV file.
data_file = r'C:\Users\KIIT\Desktop\Advanced Programming\AP Project - Cricket analysis\cricket_statsnew.csv'

# Check if file exists.
if not os.path.exists(data_file):
    st.error(f"File '{data_file}' not found. Please check the file path.")
    st.stop()

# Load the DataFrame.
df = pd.read_csv(data_file)

# Chatbot function to process the user query.
def answer_question(question):
    """
    Answer a user's question by interpreting the query and performing
    operations on the loaded DataFrame.
    """
    # --- Pattern 1: Operation on a column (highest, lowest, average, top n) ---
    op_pattern = re.compile(r"(highest|lowest|average|mean|top\s*\d+)\s+(?:of|in)\s+(\w+)", re.IGNORECASE)
    op_match = op_pattern.search(question)
    
    if op_match:
        op = op_match.group(1).lower()
        column = op_match.group(2)
        if column not in df.columns:
            return f"Column '{column}' not found in the data."
        
        if op in ['average', 'mean']:
            value = df[column].mean()
            return f"The average of '{column}' is {value:.2f}."
        elif op == 'highest':
            value = df[column].max()
            return f"The highest value of '{column}' is {value}."
        elif op == 'lowest':
            value = df[column].min()
            return f"The lowest value of '{column}' is {value}."
        elif op.startswith("top"):
            num_match = re.search(r'\d+', op)
            if num_match:
                num = int(num_match.group())
                try:
                    top_values = df[column].nlargest(num)
                    return f"The top {num} values of '{column}' are:\n{top_values.to_string()}"
                except Exception as e:
                    return f"Error processing top values for '{column}': {e}"
            else:
                return "Could not determine the number for the top operation."

    # --- Pattern 2: Direct player query (e.g., "What is V Kohli's SR?") ---
    player_pattern = re.compile(r"what\s+is\s+([\w\s\.]+)'s\s+(\w+)", re.IGNORECASE)
    player_match = player_pattern.search(question)
    
    if player_match:
        player_name = player_match.group(1).strip()
        stat_column = player_match.group(2).strip()
        
        if 'Player' not in df.columns:
            return "The data does not contain a 'Player' column."
        
        player_rows = df[df['Player'].str.contains(player_name, case=False, na=False)]
        if player_rows.empty:
            return f"Player '{player_name}' not found."
        elif stat_column not in df.columns:
            return f"Column '{stat_column}' not found in the data."
        else:
            value = player_rows[stat_column].iloc[0]
            return f"{player_name}'s {stat_column} is {value}."

    # --- Pattern 3: Contextual query for top players ---
    # Example: "Which players have top 5 SR?"
    context_pattern = re.compile(r"\|?\s*which\s+players\s+have\s+top\s*(\d+)\s+(\w+)", re.IGNORECASE)
    context_match = context_pattern.search(question)
    
    if context_match:
        top_n = int(context_match.group(1))
        stat_column = context_match.group(2)
        if 'Player' not in df.columns:
            return "The data does not contain a 'Player' column."
        if stat_column not in df.columns:
            return f"Column '{stat_column}' not found in the data."
        
        try:
            sorted_df = df.sort_values(by=stat_column, ascending=False)
        except Exception as e:
            return f"Error sorting by column '{stat_column}': {e}"
        
        top_players = sorted_df.head(top_n)['Player']
        players_list = top_players.tolist()
        return f"Top {top_n} players by {stat_column} are:\n" + "\n".join(players_list)
    
    return "Sorry, I couldn't understand your question. Please try a different query."

# Streamlit UI
st.title("Cricket Data Chatbot")
st.write("Ask questions about cricket stats! For example: 'What is V Kohli's SR?', 'highest of runs', or 'top 5 economy'.")

# Maintain chat history using session_state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# User input form.
with st.form(key="chat_form", clear_on_submit=True):
    user_question = st.text_input("Your question:")
    submit_button = st.form_submit_button("Send")

if submit_button and user_question:
    # Process the query and get answer.
    answer = answer_question(user_question)
    # Append both question and answer to the chat history.
    st.session_state.chat_history.append(("You", user_question))
    st.session_state.chat_history.append(("Bot", answer))

# Display chat history.
for speaker, message in st.session_state.chat_history:
    if speaker == "You":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**Bot:** {message}")
