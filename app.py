from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import sqlite3
import datetime

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE = 'database.db'

# Models
class User(BaseModel):
    user_id: int
    username: str
    email: str

class CodeSubmission(BaseModel):
    submission_id: int
    user_id: int
    code: str
    submitted_at: datetime.datetime

class ReviewSuggestion(BaseModel):
    suggestion_id: int
    submission_id: int
    suggestion: str
    created_at: datetime.datetime

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS code_submissions (
        submission_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        code TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS review_suggestions (
        suggestion_id INTEGER PRIMARY KEY,
        submission_id INTEGER,
        suggestion TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(submission_id) REFERENCES code_submissions(submission_id)
    )
    ''')
    conn.commit()
    conn.close()

# Seed data
def seed_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, email) VALUES (1, 'johndoe', 'john@example.com')")
    cursor.execute("INSERT OR IGNORE INTO code_submissions (submission_id, user_id, code) VALUES (1, 1, 'print(\"Hello, World!\")')")
    cursor.execute("INSERT OR IGNORE INTO review_suggestions (suggestion_id, submission_id, suggestion) VALUES (1, 1, 'Consider using a function to encapsulate this logic.')")
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_db()
    seed_data()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/submit", response_class=HTMLResponse)
async def submit_code(request: Request):
    return templates.TemplateResponse("submit.html", {"request": request})

@app.get("/reviews", response_class=HTMLResponse)
async def review_dashboard(request: Request):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code_submissions")
    submissions = cursor.fetchall()
    cursor.execute("SELECT * FROM review_suggestions")
    suggestions = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("reviews.html", {"request": request, "submissions": submissions, "suggestions": suggestions})

@app.get("/profile", response_class=HTMLResponse)
async def user_profile(request: Request):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM code_submissions WHERE user_id = ?", (user[0],))
    submissions = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "submissions": submissions})

@app.get("/stats", response_class=HTMLResponse)
async def review_stats(request: Request):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM code_submissions")
    total_submissions = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM review_suggestions")
    total_suggestions = cursor.fetchone()[0]
    conn.close()
    return templates.TemplateResponse("stats.html", {"request": request, "total_submissions": total_submissions, "total_suggestions": total_suggestions})

@app.post("/api/code/submit")
async def api_code_submit(submission: CodeSubmission):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO code_submissions (user_id, code) VALUES (?, ?)", (submission.user_id, submission.code))
    conn.commit()
    conn.close()
    return {"message": "Code submitted successfully"}

@app.get("/api/reviews")
async def api_get_reviews():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code_submissions")
    submissions = cursor.fetchall()
    cursor.execute("SELECT * FROM review_suggestions")
    suggestions = cursor.fetchall()
    conn.close()
    return {"submissions": submissions, "suggestions": suggestions}

@app.get("/api/user/{user_id}/profile")
async def api_user_profile(user_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM code_submissions WHERE user_id = ?", (user_id,))
    submissions = cursor.fetchall()
    conn.close()
    return {"user": user, "submissions": submissions}

@app.get("/api/stats")
async def api_get_stats():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM code_submissions")
    total_submissions = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM review_suggestions")
    total_suggestions = cursor.fetchone()[0]
    conn.close()
    return {"total_submissions": total_submissions, "total_suggestions": total_suggestions}
