from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai
import re

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initial prompt for creating SQL query with memory instructions
sql_prompt = [
    """
    You are an expert in converting English questions into SQL queries.
    The SQL database is named STUDENT and has columns: NAME, CLASS, SECTION, and MARKS.
    The marks range from 0 to 20; if it's 10 or more, the student has passed.
    The SECTION column has values: math (for mathematics) and svt (for science).
    For example, if the question is "How many records are present in this table?", 
    the SQL should be: SELECT COUNT(*) FROM STUDENT;
    or if the question is "Tell me all the students in the math section", 
    the SQL should be: SELECT * FROM STUDENT WHERE SECTION="math";
    Provide the SQL code directly, with no additional quotes or symbols.

    If there is recent message history, use it only if relevant to the current question; otherwise, focus on the new question.
    """
]

# Function to generate SQL query with memory
def generate_sql_query(history, question, max_history=5):
    # Use the most recent `max_history` messages for context
    recent_history = history[-max_history:]
    full_prompt = sql_prompt[0] + "\n\nConversation history:\n"
    
    # Construct the prompt with recent conversation history
    for entry in recent_history:
        full_prompt += f"{entry['sender']}: {entry['message']}\n"
    full_prompt += f"User: {question}\nBot:"

    # Generate SQL query
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([full_prompt])
    raw_sql = response.text.strip()
    
    # Use regex to capture only valid SELECT SQL syntax, removing any non-SQL text
    sql_query = re.search(r"(SELECT)[\s\S]*?;", raw_sql, re.IGNORECASE)
    if sql_query:
        return sql_query.group(0)  # Only return the valid SQL part
    else:
        raise ValueError("Invalid SQL syntax generated")

# Function to execute SQL query on the database
def execute_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except sqlite3.OperationalError as e:
        rows = f"Error: {str(e)}"
    conn.close()
    return rows

# Prompt template for human-readable response
human_response_prompt_template = """
    You are an assistant tasked with explaining data results in a human-friendly way.
    Based on the question "{question}", here is the SQL result:
    {data}
    Please provide a summary in natural language, such as "There are X students in the math section."
"""

# Function to generate human-readable response
def generate_human_response(question, data):
    prompt = human_response_prompt_template.format(question=question, data=data)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    return response.text.strip()

# Streamlit UI setup
st.set_page_config(page_title="SQL to Natural Language")
st.title("SQL Query Chatbot")

# Initialize session state for chat history with memory support
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# User input for question
user_question = st.text_input("Type your question here:", key="input")
submit = st.button("Send")

if submit and user_question:
    # Display the user's question in the chat history
    st.session_state["chat_history"].append({"sender": "User", "message": user_question})
    
    # Generate SQL query with memory
    try:
        sql_query = generate_sql_query(st.session_state["chat_history"], user_question)
        st.session_state["chat_history"].append({"sender": "Bot", "message": f"Generated SQL Query: `{sql_query}`"})
        
        # Execute SQL query and fetch data
        data = execute_sql_query(sql_query, "students.db")
        
        # Check if data is available and transform it for human readability
        if data and not isinstance(data, str):
            # Generate a human-readable response
            human_response = generate_human_response(user_question, data)
            st.session_state["chat_history"].append({"sender": "Bot", "message": human_response})
        else:
            error_message = data if isinstance(data, str) else "No results found."
            st.session_state["chat_history"].append({"sender": "Bot", "message": error_message})
    
    except ValueError as e:
        st.session_state["chat_history"].append({"sender": "Bot", "message": str(e)})

# Display chat history with alternating user and bot messages
for chat in st.session_state["chat_history"]:
    if chat["sender"] == "User":
        st.write(f"**{chat['sender']}**: {chat['message']}")
    else:
        with st.container():
            st.markdown(f"<div style='background-color: #f0f0f5; padding: 10px; border-radius: 10px;'>**{chat['sender']}**: {chat['message']}</div>", unsafe_allow_html=True)
