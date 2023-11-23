import streamlit as st
import mysql.connector
from datetime import date, datetime
import pandas as pd

# Database connection
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='rishab@12',
    database='library'
)

cursor = db.cursor()
option = st.sidebar.selectbox("Select one of the following:", ("Issue a book","Add a book","Return a book","View Books","View Members","View Borrow Records","Delete a Book","Change Password"))

def delete_book_backend(isbn):
    # Check if the book with the given ISBN exists
    cursor.execute("SELECT No_of_Copies_Left FROM Book WHERE ISBN = %s", (isbn,))
    total = cursor.fetchone()[0]
    cursor.execute("SELECT Total_No_of_Copies FROM Book WHERE ISBN = %s", (isbn,))
    left = cursor.fetchone()[0]


    if total == left:
        # Book exists, delete it
        cursor.execute("DELETE FROM Borrow WHERE ISBN = %s", (isbn,))
        cursor.execute("DELETE FROM Book WHERE ISBN = %s", (isbn,))
        db.commit()
        st.success("Book deleted successfully!")

    elif total > left:
        st.warning("Book with the provided ISBN has not been returned yet.")

    else:
        st.warning("Book with the provided ISBN does not exist.")

# Streamlit UI
if option == "Add a book":
    st.title("Add a New Book")

    isbn = st.text_input("ISBN")
    title = st.text_input("Title")
    genre = st.text_input("Genre")
    price = st.number_input("Price (in rupees)", min_value=0.0)
    author_name = st.text_input("Author's Name")
    publisher_name = st.text_input("Publisher's Name")
    total_copies = st.number_input("Total Number of Copies", min_value=1)

    if st.button("Add Book"):
        # Check if the book with the given ISBN already exists
        cursor.execute("SELECT COUNT(*) FROM Book WHERE ISBN = %s", (isbn,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Book already exists, update the number of copies in the Borrow table
            cursor.execute("UPDATE Book SET No_of_Copies_Left = No_of_Copies_Left + %s WHERE ISBN = %s", (total_copies, isbn))
            cursor.execute("UPDATE Book SET Total_No_of_Copies = Total_No_of_Copies + %s WHERE ISBN = %s", (total_copies, isbn))
        else:
            # Book does not exist, insert the new book
            cursor.execute("INSERT INTO Book (ISBN, Title, Author_Name, Publisher_Name, Genre, Price, Total_No_Of_Copies,No_of_Copies_Left) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (isbn, title, author_name, publisher_name, genre, price, total_copies,total_copies))
        db.commit()
        st.success("Book added successfully!")


elif option == "Issue a book":
    st.title("Issue a Book")

    member_id = st.text_input("Member ID")
    isbn_to_issue = st.text_input("ISBN")

    if st.button("Issue Book"):
        # Check if the user has already issued three books without returning
        cursor.execute("SELECT COUNT(*) FROM Borrow WHERE Member_ID = %s AND Return_Date IS NULL", (member_id,))
        issued_books_count = cursor.fetchone()[0]

        if issued_books_count < 3:
            # Check if the book is available for borrowing
            cursor.execute("SELECT No_of_Copies_Left FROM Book WHERE ISBN = %s", (isbn_to_issue,))
            copies_left = cursor.fetchone()

            if copies_left and copies_left[0] > 0:
                # Book is available, decrease the number of copies and record issue date and member ID
                cursor.execute("INSERT INTO Borrow (Issue_Date, Member_ID, ISBN) VALUES (%s,%s,%s)",
                               (date.today(), member_id, isbn_to_issue))
                db.commit()
                st.success("Book issued successfully!")
            else:
                st.warning("The book is not available for borrowing.")
        else:
            st.warning("You have already issued three books without returning. Cannot issue another book.")



elif option == "Return a book":
    st.title("Return a Book")

    member_id_return = st.text_input("Member ID")
    isbn_to_return = st.text_input("ISBN")
    return_date_str = st.text_input("Return Date (YYYY-MM-DD)")

    if st.button("Return Book"):
        # Check if the book was issued to the member
        cursor.execute("SELECT Issue_Date FROM Borrow WHERE ISBN = %s AND Member_ID = %s", (isbn_to_return, member_id_return))
        issue_date_result = cursor.fetchone()

        if issue_date_result:
            issue_date = issue_date_result[0]
            return_date = datetime.strptime(return_date_str, "%Y-%m-%d").date()

            # Calculate the number of days between issue date and return date
            days_difference = (return_date - issue_date).days

            # Calculate late fees if the book is returned after 20 days
            late_fees = max(0, days_difference - 20) * 30

            # Update the Borrow table with return date and late fees
            cursor.execute("UPDATE Borrow SET Return_Date = %s, Late_Fees = %s WHERE ISBN = %s AND Member_ID = %s",
                           (return_date, late_fees, isbn_to_return, member_id_return))
            cursor.execute("UPDATE Book SET No_of_Copies_Left = No_of_Copies_Left + 1 WHERE ISBN = %s", (isbn_to_return,))
            db.commit()

            st.success("Book returned successfully!")
            st.info(f"Late Fees: {late_fees} rupees")
        else:
            st.warning("The book was not issued to the member.")

elif option == "Delete a Book":
    st.title("Delete a Book")

    # Collect user input for ISBN to delete
    isbn_to_delete = st.text_input("ISBN to Delete")

    # Button to trigger book deletion
    if st.button("Delete Book"):
        delete_book_backend(isbn_to_delete)

# Streamlit UI
# Streamlit UI
if option == "View Members":
    # Add the new piece of code to display the number of borrowed books by each member
    cursor.execute("""
        SELECT Members.Member_ID, Full_Name, COUNT(Borrow.ISBN) AS Borrowed_Books
        FROM Members
        LEFT JOIN Borrow ON Members.Member_ID = Borrow.Member_ID
        WHERE Borrow.Return_Date IS NULL
        GROUP BY Members.Member_ID
    """)
    borrowed_books_by_member = cursor.fetchall()

    if borrowed_books_by_member:
        st.title("View number of books borrowed by each member:")
        st.table(pd.DataFrame(borrowed_books_by_member, columns=["Member_ID", "Full_Name", "Borrowed_Books"]))
    else:
        st.info("No data available.")

    # Add the code to display members who have not borrowed any books
    cursor.execute("""
        SELECT Member_ID, Full_Name
        FROM Members
        WHERE Member_ID NOT IN (
            SELECT DISTINCT Member_ID
            FROM Borrow
        )
    """)
    non_borrowing_members = cursor.fetchall()

    if non_borrowing_members:
        st.title("Members who have not borrowed any books:")
        st.table(pd.DataFrame(non_borrowing_members, columns=["Member_ID", "Full_Name"]))
    else:
        st.info("All members have borrowed books.")


elif option == "View Books":
    # Existing code for viewing books
    st.title("View Books")

    # Fetch only necessary columns from the Book table
    cursor.execute("SELECT ISBN, Title, Total_No_Of_Copies FROM Book")
    books_data = cursor.fetchall()

    # Get column names
    column_names = ["ISBN", "Title", "Total_No_Of_Copies"]

    # Display the books data with pandas
    if books_data:
        books_df = pd.DataFrame(books_data, columns=column_names)
        st.table(books_df)
    else:
        st.info("No books data available.")

elif option == "View Books":
    st.title("View Books")

    # Fetch only necessary columns from the Book table
    cursor.execute("SELECT ISBN, Title, Total_No_Of_Copies FROM Book")
    books_data = cursor.fetchall()

    # Get column names
    column_names = ["ISBN", "Title", "Total_No_Of_Copies"]

    # Display the books data with pandas
    if books_data:
        books_df = pd.DataFrame(books_data, columns=column_names)
        st.table(books_df)
    else:
        st.info("No books data available.")

elif option == "View Borrow Records":
    st.title("View Borrow Records")

    # Fetch all borrow records from the Borrow table
    cursor.execute("SELECT * FROM Borrow")
    borrow_data = cursor.fetchall()

    # Get column names
    column_names = [i[0] for i in cursor.description]

    # Display the borrow records data with pandas
    if borrow_data:
        # Handle NaN values in the data before creating the DataFrame
        borrow_data_cleaned = [[int(value) if isinstance(value, float) else value for value in row] for row in borrow_data]

        borrow_df = pd.DataFrame(borrow_data_cleaned, columns=column_names)
        st.table(borrow_df)
    else:
        st.info("No borrow records data available.")



elif option == "Change Password":
    st.title("Change Password")

    user_id = st.text_input("Employee ID")

    old_password = st.text_input("Old Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

    if st.button("Change Password"):
        # Check if the old password matches the current password in the database
        cursor.execute("SELECT Password FROM Employee WHERE Employee_ID = %s", (user_id,))
        result = cursor.fetchone()

        if result and result[0] == old_password:
            # Update the password with the new password
            if new_password == confirm_password:
                cursor.execute("UPDATE Employee SET Password = %s WHERE Employee_ID = %s", (new_password, user_id))
                db.commit()
                st.success("Password changed successfully!")
            else:
                st.warning("New password and confirm password do not match.")
        else:
            st.warning("Incorrect old password.")



# Close the database connection
cursor.close()
db.close()
