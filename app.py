from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Gemini
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to read and execute SQL query
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows

# Prompt for converting questions to SQL
prompt = [
    """
    you are an expert in converting english question to sql query.
    the sql database has the name STUDENT and has the following columns , NAME, CLASS ,SECTION and MARKS
    the marks conatains a grade from 0 to 20 , if its 10 or more then student passed the test
    in the section there is two section math (for mathematics) and svt (for science)
    for example , when the question is (how many entries of records present in this table ?) the sql command will look like this
    SELECT COUNT(*) FROM STUDENT;
    or for example if the question is (tell me all the students studying in math ( mathematics)) the sql response will be
    SELECT * FROM STUDENT WHERE CLASS="math";
    also the sql code should not have any ''' in beggining or end of the ouput you will just send the code directly with no extra
    """
]

# Streamlit UI setup
st.set_page_config(page_title="het teext naatik sql séééhbiii")
st.header("Gemini aamlaa 7aala")

# User input for question
question = st.text_input("INPUT:", key="input")
submit = st.button("ASK the question bratha")

if submit:
    # Get the generated SQL query
    sql_query = get_gemini_response(question, prompt)
    
    # Display the generated SQL query
    st.subheader("Generated SQL Query")
    st.write(sql_query)
    
    # Execute the SQL query and display the results
    data = read_sql_query(sql_query, "students.db")
    st.subheader("Query Result")
    
    # Display data in a table format if rows are returned
    if data:
        st.table(data)  # Shows data in a table format
    else:
        st.write("No results found.")
