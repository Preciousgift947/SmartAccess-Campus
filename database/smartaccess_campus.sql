DROP DATABASE IF EXISTS SmartAccessCampus;
CREATE DATABASE SmartAccessCampus;
USE SmartAccessCampus;

-- 1. STUDENT TABLE

CREATE TABLE STUDENT (
    Student_ID INT NOT NULL AUTO_INCREMENT,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Student_Number VARCHAR(20) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Phone_Number VARCHAR(15),
    Photo_URL VARCHAR(255),
    Course VARCHAR(100) NOT NULL,
    Faculty VARCHAR(100) NOT NULL,
    Registration_Date DATE NOT NULL DEFAULT (CURRENT_DATE),
    Password_Hash VARCHAR(255) NOT NULL,
    PRIMARY KEY (Student_ID)
);


-- 2. LECTURER TABLE

CREATE TABLE LECTURER (
    Lecturer_ID INT NOT NULL AUTO_INCREMENT,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Faculty VARCHAR(100) NOT NULL,
    Password_Hash VARCHAR(255) NOT NULL,
    PRIMARY KEY (Lecturer_ID)
);

-- 3. ADMIN TABLE

CREATE TABLE ADMIN (
    Admin_ID INT NOT NULL AUTO_INCREMENT,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Role ENUM('Administrator','Security Personnel') NOT NULL,
    Password_Hash VARCHAR(255) NOT NULL,
    PRIMARY KEY (Admin_ID)
);

-- 4. DIGITAL_ACCESS_CARD TABLE

CREATE TABLE DIGITAL_ACCESS_CARD (
    Card_ID INT NOT NULL AUTO_INCREMENT,
    Student_ID INT NOT NULL,
    QR_Code_Data TEXT NOT NULL,
    Issue_Date DATE NOT NULL DEFAULT (CURRENT_DATE),
    Expiry_Date DATE NOT NULL,
    Card_Status ENUM('Active','Expired','Suspended','Revoked')
        NOT NULL DEFAULT 'Active',

    PRIMARY KEY (Card_ID),

    CONSTRAINT FK_CARD_STUDENT
        FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    UNIQUE (Student_ID)
);

-- 5. MODULE TABLE

CREATE TABLE MODULE (
    Module_ID INT NOT NULL AUTO_INCREMENT,
    Module_Name VARCHAR(100) NOT NULL,
    Module_Code VARCHAR(20) NOT NULL UNIQUE,
    Lecturer_ID INT NOT NULL,
    Venue VARCHAR(100) NOT NULL,
    Day ENUM(
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday'
    ) NOT NULL,
    Time TIME NOT NULL,

    PRIMARY KEY (Module_ID),

    CONSTRAINT FK_MODULE_LECTURER
        FOREIGN KEY (Lecturer_ID)
        REFERENCES LECTURER(Lecturer_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- 6. STUDENT_MODULE TABLE

CREATE TABLE STUDENT_MODULE (
    Student_ID INT NOT NULL,
    Module_ID INT NOT NULL,

    PRIMARY KEY (Student_ID, Module_ID),

    CONSTRAINT FK_SM_STUDENT
        FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT FK_SM_MODULE
        FOREIGN KEY (Module_ID)
        REFERENCES MODULE(Module_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- 7. ACADEMIC_EVENT TABLE

CREATE TABLE ACADEMIC_EVENT (
    Event_ID INT NOT NULL AUTO_INCREMENT,
    Module_ID INT NOT NULL,
    Event_Type ENUM(
        'Assignment',
        'Test',
        'Examination',
        'Other'
    ) NOT NULL,
    Event_Date DATE NOT NULL,
    Event_Description TEXT NOT NULL,
    Reminder_Date DATE NOT NULL,

    PRIMARY KEY (Event_ID),

    CONSTRAINT FK_EVENT_MODULE
        FOREIGN KEY (Module_ID)
        REFERENCES MODULE(Module_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- 8. ATTENDANCE TABLE

CREATE TABLE ATTENDANCE (
    Attendance_ID INT NOT NULL AUTO_INCREMENT,
    Student_ID INT NOT NULL,
    Module_ID INT NOT NULL,
    Attendance_Date DATE NOT NULL,
    Status ENUM('Present','Absent','Late')
        NOT NULL DEFAULT 'Present',
    Scan_Time TIME NOT NULL,
    Gate_Location VARCHAR(100) NOT NULL,

    PRIMARY KEY (Attendance_ID),

    CONSTRAINT FK_ATTENDANCE_STUDENT
        FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT FK_ATTENDANCE_MODULE
        FOREIGN KEY (Module_ID)
        REFERENCES MODULE(Module_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- 9. NOTIFICATION TABLE

CREATE TABLE NOTIFICATION (
    Notification_ID INT NOT NULL AUTO_INCREMENT,
    Student_ID INT NOT NULL,
    Event_ID INT,
    Message TEXT NOT NULL,
    Sent_Date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Status ENUM('Sent','Pending')
        NOT NULL DEFAULT 'Pending',
    Is_Read BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (Notification_ID),

    CONSTRAINT FK_NOTIFICATION_STUDENT
        FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT FK_NOTIFICATION_EVENT
        FOREIGN KEY (Event_ID)
        REFERENCES ACADEMIC_EVENT(Event_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- INSERT LECTURERS

INSERT INTO LECTURER (First_Name,Last_Name,Email,Faculty,Password_Hash) VALUES
('Lerato','Nkosi','lerato.nkosi@richfield.ac.za','Information Technology','Lect1@2026'),
('Sipho','Ndlovu','sipho.ndlovu@richfield.ac.za','Information Technology','Lect2@2026'),
('Ayanda','Zulu','ayanda.zulu@richfield.ac.za','Information Technology','Lect3@2026'),
('Thabo','Molefe','thabo.molefe@richfield.ac.za','Information Technology','Lect4@2026'),
('Nomsa','Naidoo','nomsa.naidoo@richfield.ac.za','Information Technology','Lect5@2026'),
('John','Smith','john.smith@richfield.ac.za','Business and Management','Lect6@2026'),
('Mary','Johnson','mary.johnson@richfield.ac.za','Business and Management','Lect7@2026'),
('Peter','Brown','peter.brown@richfield.ac.za','Business and Management','Lect8@2026'),
('David','Mthembu','david.mthembu@richfield.ac.za','Business and Management','Lect9@2026'),
('Grace','Khumalo','grace.khumalo@richfield.ac.za','Business and Management','Lect10@2026');

-- INSERT ADMINS

INSERT INTO ADMIN (First_Name,Last_Name,Email,Role,Password_Hash) VALUES
('Sarah','Williams','sarah@richfield.ac.za','Administrator','Sarah@2026'),
('James','Mokoena','james@richfield.ac.za','Administrator','James@2026'),
('Lebo','Ncube','lebo@richfield.ac.za','Administrator','Lebo@2026'),
('Grace','Naidoo','grace@richfield.ac.za','Administrator','Grace@2026'),
('David','Mthembu','david@richfield.ac.za','Administrator','David@2026');

-- INSERT STUDENTS

INSERT INTO STUDENT (First_Name,Last_Name,Student_Number,Email,Phone_Number,Photo_URL,Course,Faculty,Password_Hash) VALUES
('Lerato','Molefe','ST2025001','lerato.molefe@richfield.ac.za','07012345678','photos/lerato.jpg','Bachelor of Science in Information Technology','Information Technology','Stud1@2026'),
('Sipho','Naidoo','ST2025002','sipho.naidoo@richfield.ac.za','07112345679','photos/sipho.jpg','Diploma in Information Technology','Information Technology','Stud2@2026'),
('Ayanda','Smith','ST2025003','ayanda.smith@richfield.ac.za','07212345680','photos/ayanda.jpg','Bachelor of Business Administration','Business and Management','Stud3@2026'),
('Thabo','Johnson','ST2025004','thabo.johnson@richfield.ac.za','07312345681','photos/thabo.jpg','Diploma in Business Management','Business and Management','Stud4@2026'),
('Nomsa','Brown','ST2025005','nomsa.brown@richfield.ac.za','07412345682','photos/nomsa.jpg','Certificate in Project Management','Business and Management','Stud5@2026'),
('John','Mthembu','ST2025006','john.mthembu@richfield.ac.za','07512345683','photos/john.jpg','Certificate in Human Resource Management','Business and Management','Stud6@2026'),
('Mary','Khumalo','ST2025007','mary.khumalo@richfield.ac.za','07612345684','photos/mary.jpg','Bachelor of Science in Information Technology','Information Technology','Stud7@2026'),
('Peter','Dlamini','ST2025008','peter.dlamini@richfield.ac.za','07712345685','photos/peter.jpg','Diploma in Information Technology','Information Technology','Stud8@2026'),
('David','Mokoena','ST2025009','david.mokoena@richfield.ac.za','07812345686','photos/david.jpg','Bachelor of Business Administration','Business and Management','Stud9@2026'),
('Grace','Mahloko','ST2025010','grace.mahloko@richfield.ac.za','07912345687','photos/grace.jpg','Diploma in Business Management','Business and Management','Stud10@2026'),
('Bennedict','Mabena','ST2025011','bennedict.mabena@richfield.ac.za','07012345688','photos/bennedict.jpg','Certificate in Project Management','Business and Management','Stud11@2026'),
('Lindo','Pillay','ST2025012','lindo.pillay@richfield.ac.za','07112345689','photos/lindo.jpg','Certificate in Human Resource Management','Business and Management','Stud12@2026'),
('Aphiwe','Botha','ST2025013','aphiwe.botha@richfield.ac.za','07212345690','photos/aphiwe.jpg','Bachelor of Science in Information Technology','Information Technology','Stud13@2026'),
('Neo','Jacobs','ST2025014','neo.jacobs@richfield.ac.za','07312345691','photos/neo.jpg','Diploma in Information Technology','Information Technology','Stud14@2026'),
('Kabelo','Mahlobo','ST2025015','kabelo.mahlobo@richfield.ac.za','07412345692','photos/kabelo.jpg','Bachelor of Business Administration','Business and Management','Stud15@2026'),
('Zanele','Mabaso','ST2025016','zanele.mabaso@richfield.ac.za','07512345693','photos/zanele.jpg','Diploma in Business Management','Business and Management','Stud16@2026'),
('Brian','Sithole','ST2025017','brian.sithole@richfield.ac.za','07612345694','photos/brian.jpg','Certificate in Project Management','Business and Management','Stud17@2026'),
('Kevin','Nkosi','ST2025018','kevin.nkosi@richfield.ac.za','07712345695','photos/kevin.jpg','Certificate in Human Resource Management','Business and Management','Stud18@2026'),
('Faith','Ndlovu','ST2025019','faith.ndlovu@richfield.ac.za','07812345696','photos/faith.jpg','Bachelor of Science in Information Technology','Information Technology','Stud19@2026'),
('Musa','Zulu','ST2025020','musa.zulu@richfield.ac.za','07912345697','photos/musa.jpg','Diploma in Information Technology','Information Technology','Stud20@2026');

-- INSERT MODULES

INSERT INTO MODULE (Module_Name, Module_Code, Lecturer_ID, Venue, Day, Time) VALUES
('Cloud Computing','CC101',1,'Lab 1','Monday','09:00:00'),
('Internet of Things','IOT102',2,'Lab 2','Tuesday','10:00:00'),
('Cybersecurity','CYB103',3,'Lab 3','Wednesday','11:00:00'),
('Software Development','SD104',4,'Lab 4','Thursday','09:00:00'),
('Algorithms','ALG105',5,'Lecture 1','Friday','10:00:00'),
('Database Programming','DBP106',6,'Lab 5','Monday','11:00:00'),
('Web Development','WEB107',7,'Lab 1','Tuesday','09:00:00'),
('Cloud Computing II','CC201',8,'Lab 2','Wednesday','10:00:00'),
('Internet of Things II','IOT202',9,'Lab 3','Thursday','11:00:00'),
('Cybersecurity II','CYB203',10,'Lab 4','Friday','09:00:00'),
('Financial Accounting','FAC204',1,'Lecture 2','Monday','13:00:00'),
('Management Accounting','MAC205',2,'Lecture 3','Tuesday','13:00:00'),
('Auditing','AUD206',3,'Lecture 4','Wednesday','13:00:00'),
('Marketing','MKT207',4,'Lecture 5','Thursday','13:00:00'),
('Human Resources Management','HRM208',5,'Lecture 6','Friday','13:00:00'),
('Advanced Software Development','SD301',6,'Lab 5','Monday','15:00:00'),
('Advanced Database Programming','DBP302',7,'Lab 2','Tuesday','15:00:00'),
('Advanced Web Development','WEB303',8,'Lab 1','Wednesday','15:00:00'),
('Business Information Systems','BIS304',9,'Lecture 7','Thursday','15:00:00'),
('Project Management','PM305',10,'Auditorium','Friday','15:00:00');

-- INSERT STUDENT MODULES

INSERT INTO STUDENT_MODULE (Student_ID,Module_ID) VALUES
(1,1),
(1,2),
(2,2),
(2,3),
(3,3),
(3,4),
(4,4),
(4,5),
(5,5),
(5,6),
(6,6),
(6,7),
(7,7),
(7,8),
(8,8),
(8,9),
(9,9),
(9,10),
(10,10),
(10,11),
(11,11),
(11,12),
(12,12),
(12,13),
(13,13),
(13,14),
(14,14),
(14,15),
(15,15),
(15,16),
(16,16),
(16,17),
(17,17),
(17,18),
(18,18),
(18,19),
(19,19),
(19,20),
(20,20),
(20,1);

-- INSERT DIGITAL ACCESS CARDS

INSERT INTO DIGITAL_ACCESS_CARD (Student_ID,QR_Code_Data,Expiry_Date,Card_Status) VALUES
(1,'QR0001','2027-12-31','Active'),
(2,'QR0002','2027-12-31','Active'),
(3,'QR0003','2027-12-31','Active'),
(4,'QR0004','2027-12-31','Active'),
(5,'QR0005','2027-12-31','Active'),
(6,'QR0006','2027-12-31','Active'),
(7,'QR0007','2027-12-31','Active'),
(8,'QR0008','2027-12-31','Active'),
(9,'QR0009','2027-12-31','Active'),
(10,'QR0010','2027-12-31','Active'),
(11,'QR0011','2027-12-31','Active'),
(12,'QR0012','2027-12-31','Active'),
(13,'QR0013','2027-12-31','Active'),
(14,'QR0014','2027-12-31','Active'),
(15,'QR0015','2027-12-31','Active'),
(16,'QR0016','2027-12-31','Active'),
(17,'QR0017','2027-12-31','Active'),
(18,'QR0018','2027-12-31','Active'),
(19,'QR0019','2027-12-31','Active'),
(20,'QR0020','2027-12-31','Active');

-- INSERT ACADEMIC EVENTS

INSERT INTO ACADEMIC_EVENT (Module_ID, Event_Type, Event_Date, Event_Description, Reminder_Date) VALUES
(1,'Assignment','2026-09-01','Cloud Computing Assignment 1','2026-08-28'),
(2,'Test','2026-09-02','Internet of Things Class Test','2026-08-30'),
(3,'Assignment','2026-09-03','Cybersecurity Risk Assessment Assignment','2026-08-31'),
(4,'Examination','2026-09-04','Software Development Midterm Examination','2026-09-01'),
(5,'Assignment','2026-09-05','Algorithms Programming Assignment','2026-09-02'),
(6,'Test','2026-09-06','Database Programming Practical Test','2026-09-03'),
(7,'Assignment','2026-09-07','Web Development Portfolio Submission','2026-09-04'),
(8,'Examination','2026-09-08','Cloud Computing II Final Examination','2026-09-05'),
(9,'Assignment','2026-09-09','Internet of Things II Research Assignment','2026-09-06'),
(10,'Test','2026-09-10','Cybersecurity II Theory Test','2026-09-07'),
(11,'Assignment','2026-09-11','Financial Accounting Assignment 1','2026-09-08'),
(12,'Examination','2026-09-12','Management Accounting Semester Examination','2026-09-09'),
(13,'Assignment','2026-09-13','Auditing Case Study Submission','2026-09-10'),
(14,'Test','2026-09-14','Marketing Principles Class Test','2026-09-11'),
(15,'Assignment','2026-09-15','Human Resources Management Group Assignment','2026-09-12'),
(16,'Examination','2026-09-16','Advanced Software Development Practical Examination','2026-09-13'),
(17,'Assignment','2026-09-17','Advanced Database Programming Project Submission','2026-09-14'),
(18,'Test','2026-09-18','Advanced Web Development Practical Test','2026-09-15'),
(19,'Assignment','2026-09-19','Business Information Systems Research Project','2026-09-16'),
(20,'Examination','2026-09-20','Project Management Final Examination','2026-09-17');

-- INSERT ATTENDANCE

INSERT INTO ATTENDANCE (Student_ID, Module_ID, Attendance_Date, Status, Scan_Time, Gate_Location) VALUES
(1,1,'2026-08-01','Present','08:50:00','Main Entrance'),
(2,2,'2026-08-02','Late','10:08:00','North Gate'),
(3,3,'2026-08-03','Absent','00:00:00','No Scan'),
(4,4,'2026-08-04','Present','08:55:00','South Gate'),
(5,5,'2026-08-05','Late','10:12:00','Parking Entrance'),
(6,6,'2026-08-06','Absent','00:00:00','No Scan'),
(7,7,'2026-08-07','Present','08:47:00','Library Entrance'),
(8,8,'2026-08-08','Late','10:06:00','Student Centre Entrance'),
(9,9,'2026-08-09','Absent','00:00:00','No Scan'),
(10,10,'2026-08-10','Present','08:53:00','Administration Block'),
(11,11,'2026-08-11','Late','13:05:00','Main Entrance'),
(12,12,'2026-08-12','Absent','00:00:00','No Scan'),
(13,13,'2026-08-13','Present','08:58:00','North Gate'),
(14,14,'2026-08-14','Late','13:09:00','South Gate'),
(15,15,'2026-08-15','Absent','00:00:00','No Scan'),
(16,16,'2026-08-16','Present','14:52:00','Parking Entrance'),
(17,17,'2026-08-17','Late','15:07:00','Library Entrance'),
(18,18,'2026-08-18','Absent','00:00:00','No Scan'),
(19,19,'2026-08-19','Present','14:48:00','Student Centre Entrance'),
(20,20,'2026-08-20','Late','15:11:00','Administration Block');

-- INSERT NOTIFICATIONS

INSERT INTO NOTIFICATION (Student_ID, Event_ID, Message, Status, Is_Read) VALUES
(1,1,'Reminder: Your Cloud Computing assignment is due on 1 September 2026.','Sent',FALSE),
(2,2,'Reminder: Internet of Things test is scheduled for 2 September 2026. Please arrive 15 minutes early.','Sent',TRUE),
(3,3,'Reminder: Cybersecurity assignment is due on 3 September 2026.','Sent',FALSE),
(4,4,'Reminder: Software Development examination will take place on 4 September 2026.','Sent',TRUE),
(5,5,'Reminder: Algorithms assignment submission closes on 5 September 2026.','Sent',FALSE),
(6,6,'Reminder: Database Programming test will be written on 6 September 2026.','Sent',TRUE),
(7,7,'Reminder: Web Development assignment is due on 7 September 2026.','Sent',FALSE),
(8,8,'Reminder: Cloud Computing II examination is scheduled for 8 September 2026.','Sent',TRUE),
(9,9,'Reminder: Internet of Things II assignment must be submitted by 9 September 2026.','Sent',FALSE),
(10,10,'Reminder: Cybersecurity II test will be held on 10 September 2026.','Sent',TRUE),
(11,11,'Reminder: Financial Accounting assignment is due on 11 September 2026.','Sent',FALSE),
(12,12,'Reminder: Management Accounting examination will take place on 12 September 2026.','Sent',TRUE),
(13,13,'Reminder: Auditing assignment submission deadline is 13 September 2026.','Sent',FALSE),
(14,14,'Reminder: Marketing test is scheduled for 14 September 2026.','Sent',TRUE),
(15,15,'Reminder: Human Resources Management assignment is due on 15 September 2026.','Sent',FALSE),
(16,16,'Reminder: Advanced Software Development examination is on 16 September 2026.','Sent',TRUE),
(17,17,'Reminder: Advanced Database Programming assignment must be submitted by 17 September 2026.','Sent',FALSE),
(18,18,'Reminder: Advanced Web Development test is scheduled for 18 September 2026.','Sent',TRUE),
(19,19,'Reminder: Business Information Systems assignment is due on 19 September 2026.','Sent',FALSE),
(20,20,'Reminder: Project Management examination is scheduled for 20 September 2026. Best of luck!','Sent',TRUE);

-- DISPLAY DATA
SELECT * FROM STUDENT;
SELECT * FROM LECTURER;
SELECT * FROM ADMIN;
SELECT * FROM MODULE;
SELECT * FROM STUDENT_MODULE;
SELECT * FROM DIGITAL_ACCESS_CARD;
SELECT * FROM ACADEMIC_EVENT;
SELECT * FROM ATTENDANCE;
SELECT * FROM NOTIFICATION;