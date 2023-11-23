import mysql.connector
import streamlit as st
import subprocess
import random

# Establishing the connection
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='rishab@12',
    database='library'
)

# Creating a cursor
mycursor = mydb.cursor()
print("Connection Established")

# Create a session state to manage the password field
if 'password' not in st.session_state:
    st.session_state.password = ""

# Creating a streamlit app
st.title("Library Management System")

# Creating Options for the Admin
option = st.sidebar.selectbox("Select the type of user:", ("Employee", "User Registration"))

if option == "Employee":
    emp_id = st.text_input("Employee ID:")
    emp_password = st.text_input("Password:", type="password", key="admin_password")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    if col1.button("Login"):
        query = "SELECT * FROM Employee WHERE Employee_ID = %s"
        mycursor.execute(query, (emp_id,))
        employee_data = mycursor.fetchone()

        if employee_data:
            db_password = employee_data[5]

            if db_password == emp_password:
                st.success("Login Successful!")
                subprocess.call(["streamlit", "run", "admin.py"])

            else:
                st.error("Wrong Password!")
        else:
            st.error("Employee not found")

elif option == "User Registration":
    fname = st.text_input("First Name:")
    lname = st.text_input("Last Name:")
    email = st.text_input("Email ID:")
    password = st.text_input("Password:", type="password")
    mobile = st.text_input("Phone Number:")
    address = st.text_area("Address:")

    if st.button("Register"):
        # Call the stored procedure to register a new member
        mycursor.callproc('RegisterMember', (fname, lname, email, password, mobile, address))
        mydb.commit()
        
        st.success("Registration Successful!")

        # Fetch the generated member ID
        mycursor.execute("SELECT Member_ID FROM Members WHERE Email = %s", (email,))
        member_id = mycursor.fetchone()[0]

        st.write("Your Member ID is", member_id)

# Streamlit UI Styling
st.markdown(
    """
    <style>
    body {
        background-color: black;
        color: white;
    }
    #main_content {
        padding: 100px;
        margin: 0 auto;
        text-align: center;
    }
    #side_bar {
        padding: 50px;
        width: 300px;
        height: 450px.
    }
    #main_content h3 {
        margin-bottom: 20px;
    }
    .form-group {
        text-align: left;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

mycursor.close()
mydb.close()
