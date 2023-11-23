-- Active: 1699331073415@@127.0.0.1@3306@Library

-- DROP DATABASE Library;
CREATE DATABASE Library;
USE Library;

-- Create Employee table
CREATE TABLE Employee (
    First_Name VARCHAR(255),
    Last_Name VARCHAR(255),
    Email VARCHAR(255),
    Phone_No VARCHAR(20),
    Employee_ID INT PRIMARY KEY,
    Password VARCHAR(255)
);

-- Create Members table
CREATE TABLE Members (
    First_Name VARCHAR(255),
    Last_Name VARCHAR(255),
    Email VARCHAR(255),
    Phone_No VARCHAR(20),
    Full_Name VARCHAR(255),
    Address VARCHAR(255),
    Member_ID INT AUTO_INCREMENT PRIMARY KEY,
    Password VARCHAR(255),
    Registration_Fee INT DEFAULT 200
);

-- Create Book table
CREATE TABLE Book(
    ISBN VARCHAR(13) PRIMARY KEY,
    Title VARCHAR(255), 
    Author_Name VARCHAR(255),
    Publisher_Name VARCHAR(255),
    Genre VARCHAR(255),
    Price DECIMAL(10, 2),
    Total_No_Of_Copies INT,
    No_of_Copies_Left INT
   
);

-- Create Borrow Table 
CREATE TABLE Borrow(
    Borrow_ID INT AUTO_INCREMENT PRIMARY KEY,
    Member_ID INT,
    ISBN VARCHAR(13),
    Issue_Date DATE,
    Return_Date DATE,
    Late_Fees DECIMAL(10, 2)
);


-- Define the "Borrows" relationship
ALTER TABLE Borrow
ADD CONSTRAINT FK_Book_Members
FOREIGN KEY (Member_ID)
REFERENCES Members(Member_ID);

ALTER TABLE Borrow
ADD CONSTRAINT FK_Book
FOREIGN KEY (ISBN)
REFERENCES Book(ISBN);

SET SQL_SAFE_UPDATES = 0;



-- Concatenate the first name and last name and update the Full_Name column
DELIMITER //

CREATE TRIGGER after_member_insert_concat_name
BEFORE INSERT
ON Members FOR EACH ROW
BEGIN

    SET NEW.Full_Name = CONCAT(NEW.First_Name, ' ', NEW.Last_Name);
END;

// DELIMITER ;


-- Procedure to handle the registration of a new member

DELIMITER //

CREATE PROCEDURE RegisterMember(
    IN p_First_Name VARCHAR(255),
    IN p_Last_Name VARCHAR(255),
    IN p_Email VARCHAR(255),
    IN p_Password VARCHAR(255),
    IN p_Phone_No VARCHAR(20),
    IN p_Address VARCHAR(255)
)
BEGIN
    -- Insert the new member without specifying Member_ID (auto-increment)
    INSERT INTO Members (Phone_No, Address, First_Name, Last_Name, Email, Password)
    VALUES (p_Phone_No, p_Address, p_First_Name, p_Last_Name, p_Email, p_Password);
END 

// DELIMITER ;

-- Create a trigger to update No_of_Copies_Left when a book is issued
DELIMITER //
CREATE TRIGGER after_borrow_insert
AFTER INSERT ON Borrow FOR EACH ROW
BEGIN
    -- Decrease the number of copies left for the issued book
    UPDATE Book
    SET No_of_Copies_Left = No_of_Copies_Left - 1
    WHERE ISBN = NEW.ISBN;
END;
//
DELIMITER ;








































