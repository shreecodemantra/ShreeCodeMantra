
# ProjectHub – Final Year Project Management System

## Overview
**ProjectHub** is a web-based platform designed for final-year students to explore, download, and purchase ready-made projects across multiple domains like AI, Web Development, IoT, and more. It includes two main modules:

1. **Admin Module:** Manage projects, categories, students, and reports.
2. **Student Module:** Browse projects, view details, download free projects, and track purchased projects.

Built with **Python Flask**, **HTML/CSS/JS**, and **MongoDB**, this system is ideal for final-year project management.

---

## Features

### Student Module
- User registration and login
- Browse projects by category or keywords
- View detailed project info (abstract, technologies, demo)
- Download free projects or request paid projects
- View personal project history
- Update profile information

### Admin Module
- Admin login
- Dashboard overview (total projects, students, downloads)
- Add/Edit/Delete projects
- Upload project files (code, documentation, demo)
- Manage categories (AI, IoT, Web, ML, etc.)
- Manage students
- View download/purchase reports

---

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Backend:** Python Flask
- **Database:** MongoDB
- **Authentication:** Flask-Login, bcrypt
- **Charts/Analytics:** Chart.js (optional)
- **File Storage:** Local or Cloud (e.g., Cloudinary / AWS S3)

---

## System Architecture

```
                +------------------------------+
                |         Frontend (UI)        |
                |  HTML / CSS / JS / Bootstrap |
                +---------------+--------------+
                                |
                     HTTP Requests (Flask Routes)
                                |
                +---------------+--------------+
                |         Flask Backend        |
                |  app.py, routes.py, models.py|
                |  Handles API + Authentication|
                +---------------+--------------+
                                |
                            Flask-PyMongo
                                |
                +---------------+--------------+
                |           MongoDB            |
                |  Collections:                |
                |   - users                   |
                |   - projects                |
                |   - categories              |
                |   - downloads/purchases     |
                +------------------------------+
```

---

## Database Collections (MongoDB)

### 1. `users`
```json
{
  "_id": "ObjectId",
  "name": "Roshan",
  "email": "roshan@example.com",
  "password": "hashed_password",
  "role": "student/admin",
  "joined_at": "YYYY-MM-DD"
}
```

### 2. `projects`
```json
{
  "_id": "ObjectId",
  "title": "Smart City Portal",
  "category": "Web Development",
  "description": "Project description...",
  "tech_stack": ["Flask", "MongoDB", "HTML", "CSS"],
  "price": 0,
  "upload_date": "YYYY-MM-DD",
  "files": {
    "report": "url_to_pdf",
    "code": "url_to_zip",
    "demo_video": "url_to_video"
  }
}
```

### 3. `categories`
```json
{
  "_id": "ObjectId",
  "name": "AI/ML",
  "description": "Artificial Intelligence and Machine Learning Projects"
}
```

### 4. `downloads`
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "project_id": "ObjectId",
  "download_date": "YYYY-MM-DD"
}
```

---

## Project Structure

```
projecthub/
│
├── app.py
├── requirements.txt
├── /static/
│   ├── css/
│   ├── js/
│   ├── images/
│
├── /templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── student_dashboard.html
│   ├── browse.html
│   ├── project_detail.html
│   ├── admin_dashboard.html
│   ├── admin_projects.html
│   ├── admin_students.html
│   ├── admin_categories.html
│
└── /models/
    ├── users.py
    ├── projects.py
    ├── categories.py
    ├── downloads.py
```

---

## Setup Instructions

1. **Clone Repository**
```bash
git clone <your_repo_url>
cd projecthub
```

2. **Create Python Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure MongoDB**
- Install MongoDB or use MongoDB Atlas
- Update MongoDB connection URI in `app.py`

5. **Run Flask App**
```bash
python app.py
```
- Open browser at `http://127.0.0.1:5000`

---

## Future Enhancements
- Integrate payment gateway for paid projects
- Email verification and notifications
- AI-based project recommendation system
- Admin analytics with charts and reports
- Deploy on cloud platforms (Heroku / Render / AWS)

---

## License
This project is for **educational purposes** and final-year project demonstration. Commercial use requires permission.

---

## Author
**Roshan Mundekar**  
Email: roshan@example.com  
GitHub: [https://github.com/RoshanMundekar](https://github.com/RoshanMundekar)
