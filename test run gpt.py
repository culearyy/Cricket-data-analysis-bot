import pandas as pd
import re

# Load your data from CSV or Excel file.
# Uncomment the appropriate line below.
data_file = r'C:\Users\KIIT\Desktop\Advanced Programming\AP Project - Cricket analysis\cricket_statsnew.csv'
df = pd.read_csv(data_file)
# For Excel file, use:
# df = pd.read_excel('data.xlsx')

def answer_question(question):
    """
    Answer a user question by parsing the text and performing
    operations on the loaded DataFrame.
    """
    # Example: Answer questions asking for the average of a column.
    # Expected format: "What is the average of [column_name]?"
    average_pattern = re.compile(r'average of (\w+)', re.IGNORECASE)
    match = average_pattern.search(question)
    
    if match:
        column = match.group(1)
        if column in df.columns:
            avg = df[column].mean()
            return f"The average of '{column}' is {avg:.2f}."
        else:
            return f"Column '{column}' not found in the data."
    
    # Add more patterns and operations as needed.
    return "Sorry, I couldn't understand your question. Please try a different query."

def chat_bot():
    print("Welcome to the Data Chatbot! Type your question (or 'exit' to quit).")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        response = answer_question(user_input)
        print("Bot:", response)

if __name__ == '__main__':
    chat_bot()
