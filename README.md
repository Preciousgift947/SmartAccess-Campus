SmartAccess-Campus
Digital Student Access Card System with QR Verification - Richfield College IT Project Management Group 3

About the Project


Team Members
- Lebogang — Project Manager
- Katleho Hlabahlaba — System Analyst
- Obakeng - Documentation Leader and Testing Leader
- Amukelani - UI/UX Designer
- Olebogeng - Front-end Developer
- Happiness - Front-end Developer
- Gift  - Back-end Developer
- Alfred - Back-end Developer
- Kgothatso - Database Administartor
- Relebogile - Database Administrator
- Thami - Tester and Intergration Developer
- Eneas - Tester and Intergration Developer
- Koketso - Security Specialist
- Sibonelo - Deployment and Infastructure Sprcialist
  

 Tech Stack
- Front-End: HTML, CSS, JavaScript
- Back-End: Python (Flask)
- Database: MySQL
- QR Code: QRCode.js

## How to Run the Project
### Requirements
- Python 3.10 or newer
- MySQL Server 8.x and MySQL Workbench

### Setup
1. Clone the repo and open a terminal in the project folder.
2. Install the packages: pip install -r requirements.txt
3. Create a file called .env in the project folder with these lines (use your own MySQL password):

        DB_HOST=localhost
        DB_USER=root
        DB_PASSWORD=your_mysql_password
        DB_NAME=SmartAccessCampus
        SECRET_KEY=any_long_random_text

   Never upload .env to GitHub.
4. In MySQL Workbench, open database/smartaccess_campus.sql and run it. This creates the database and the sample data.
5. Run: python hash_passwords.py
   Do this every time you reload the SQL file. It secures the sample passwords, and logins fail without it.
6. Start the app: python app.py
   Then open the address it prints, usually http://127.0.0.1:5000

### Sample logins

| Role | Login | Password |
| --- | --- | --- |
| Student | ST2025001 | Stud1@2026 |
| Administrator | sarah@richfield.ac.za | Sarah@2026 |
