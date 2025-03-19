import pandas as pd
import re
import os


data_file = r'C:\Users\KIIT\Desktop\Advanced Programming\AP Project - Cricket analysis\cricket_statsnew.csv'


if not os.path.exists(data_file):
    print(f"File '{data_file}' not found. Please check the file path.")
    exit()


df = pd.read_csv(data_file)


def answer_question(question):
    """
    Answer a user's question by interpreting the query and performing
    operations on the loaded DataFrame.
    """
    # --- Pattern 1: Operation on a column (highest, lowest, average, top n) ---
    # This regex looks for phrases like "highest of runs", "average in wickets", "top 5 of matches"
    op_pattern = re.compile(r"(highest|lowest|average|mean|top\s*\d+)\s+(?:of|in)\s+(\w+)", re.IGNORECASE)
    op_match = op_pattern.search(question)
    
    if op_match:
        op = op_match.group(1).lower()
        column = op_match.group(2)
        if column not in df.columns:
            return f"Column '{column}' not found in the data."
        
        # Compute based on the operation detected
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
            # Extract the number (e.g., '5' from 'top 5')
            num_match = re.search(r'\d+', op)
            if num_match:
                num = int(num_match.group())
                # Use nlargest for numeric columns; if non-numeric, this might need adjustment.
                try:
                    top_values = df[column].nlargest(num)
                    return f"The top {num} values of '{column}' are:\n{top_values.to_string()}"
                except Exception as e:
                    return f"Error processing top values for '{column}': {e}"
            else:
                return "Could not determine the number for the top operation."

    # --- Pattern 2: Direct player query (e.g., "What is V Kohli's SR?") ---
    # This regex looks for queries like "What is [player]'s [stat]?"
    player_pattern = re.compile(r"what\s+is\s+([\w\s\.]+)'s\s+(\w+)", re.IGNORECASE)
    player_match = player_pattern.search(question)
    
    if player_match:
        player_name = player_match.group(1).strip()
        stat_column = player_match.group(2).strip()
        
        # Check if the dataframe has a "Player" column
        if 'Player' not in df.columns:
            return "The data does not contain a 'Player' column."
        
        # Try to find the row corresponding to the player
        # Using case-insensitive matching. Adjust if player names have extra formatting.
        player_rows = df[df['Player'].str.contains(player_name, case=False, na=False)]
        if player_rows.empty:
            return f"Player '{player_name}' not found."
        elif stat_column not in df.columns:
            return f"Column '{stat_column}' not found in the data."
        else:
            # In case of multiple rows, return the first match.
            value = player_rows[stat_column].iloc[0]
            return f"{player_name}'s {stat_column} is {value}."
    
    return "Sorry, I couldn't understand your question. Please try a different query."

def chat_bot():
    print("Welcome to the Cricket Data Chatbot! Type your question (or 'exit' to quit).")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        response = answer_question(user_input)
        print("Bot:", response)

if __name__ == '__main__':
    chat_bot()
