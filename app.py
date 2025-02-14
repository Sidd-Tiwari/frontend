from flask import Flask, request, jsonify, redirect
from enum import Enum
from flask_cors import CORS

app = Flask(__name__) 
CORS(app)

# Define RecruiterProfile Class
class RecruiterProfile:
    def __init__(self, name, email, phone, password, company, adhar):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password
        self.company = company
        self.adhar = adhar

# Define Recruiters Class
class Recruiters:
    def __init__(self):
        self.recruiters = {}

    def addUser(self, recruiter: RecruiterProfile):
        if recruiter.adhar in self.recruiters:
            return "User with this Aadhar already exists."
        self.recruiters[recruiter.adhar] = recruiter
        return f"User {recruiter.name} added successfully!"

    def getRecruiterByEmail(self, email):
        for recruiter in self.recruiters.values():
            if recruiter.email == email:
                return recruiter
        return None

# Initialize Recruiters Database
recruiters_db = Recruiters()

# Define JobStatus Enum
class JobStatus(Enum):
    WORKING = "Working"
    FREELANCE = "Freelance"
    UNEMPLOYED = "Unemployed"

# Define UserProfile Class
class UserProfile:
    def __init__(self, name, email, password, adhar, phone, expectedSalary, portfolio, jobLocation, projects, currentJob, skills):
        self.name = name
        self.email = email
        self.password = password
        self.adhar = adhar
        self.phone = phone
        self.expectedSalary = expectedSalary
        self.portfolio = portfolio
        self.jobLocation = jobLocation
        self.projects = projects
        self.skills = skills

        if isinstance(currentJob, JobStatus):
            self.currentJob = currentJob
        else:
            raise ValueError("Invalid job status. Must be an instance of JobStatus Enum.")

# Define Users Class for User Management
class Users:
    def __init__(self):
        self.users = {}

    def addUser(self, user: UserProfile):
        if user.adhar in self.users:
            return "User with this Aadhar already exists."
        self.users[user.adhar] = user
        return f"User {user.name} added successfully!"

    def filterUsers(self, expectedSalary=None, jobLocation=None, currentJobStatus=None, skills=None):
        filtered_users = []
        
        for user in self.users.values():
            if expectedSalary and user.expectedSalary > expectedSalary:
                continue
            if jobLocation and user.jobLocation.lower() != jobLocation.lower():
                continue
            if currentJobStatus and user.currentJob.value.lower() != currentJobStatus.lower():
                continue
            if skills:
                user_skills = set(map(str.lower, user.skills))
                required_skills = set(map(str.lower, skills))
                if not required_skills.issubset(user_skills):
                    continue
            
            filtered_users.append({
                "name": user.name,
                "email": user.email,
                "jobLocation": user.jobLocation,
                "expectedSalary": user.expectedSalary,
                "currentJobStatus": user.currentJob.value,
                "skills": user.skills
            })
        
        return filtered_users
# Initialize User Database
users_db = Users()

# Sample Users
# users_db.addUser(UserProfile("Alice", "alice@example.com", "password123", "123456789012", "9876543210", 50000, "alice_portfolio", "New York", ["Project1", "Project2"], JobStatus.WORKING, ["Python", "Flask"]))
# users_db.addUser(UserProfile("Bob", "bob@example.com", "password456", "987654321098", "8765432109", 60000, "bob_portfolio", "San Francisco", ["ProjectA"], JobStatus.FREELANCE, ["JavaScript", "React"]))
# users_db.addUser(UserProfile("Charlie", "charlie@example.com", "password789", "567890123456", "7654321098", 45000, "charlie_portfolio", "New York", ["ProjectX"], JobStatus.UNEMPLOYED, ["Python", "Django"]))

# Flask Routes
FRONTEND_URL = "https://sidd-tiwari.github.io/frontend"  # Replace with your actual frontend URL

@app.route('/')
def index():
    return redirect(f"{FRONTEND_URL}/")  # Redirecting to frontend login page

@app.route('/recruiterLogin', methods=['POST'])
def recLogin():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    recruiter = recruiters_db.getRecruiterByEmail(email)
    
    if recruiter and recruiter.password == password:
        return jsonify({"message": "Login successful", "name": recruiter.name, "company": recruiter.company})
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route('/recruiterRegister')
def recRegister():
    return redirect(f"{FRONTEND_URL}/recruiterRegister")

@app.route('/devLogin', methods=['POST'])
def devLogin():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = next((user for user in users_db.users.values() if user.email == email), None)
    
    if user and user.password == password:
        return jsonify({"message": "Login successful", "name": user.name, "jobLocation": user.jobLocation})
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route('/devRegister', methods=['POST'])
def devRegister():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    adhar = data.get("adhar")
    phone = data.get("phone")
    expectedSalary = data.get("expectedSalary")
    portfolio = data.get("portfolio")
    jobLocation = data.get("jobLocation")
    projects = data.get("projects", [])
    currentJobStatus = data.get("currentJobStatus")
    skills = data.get("skills", [])

    if not all([name, email, password, adhar, phone, expectedSalary, portfolio, jobLocation, currentJobStatus]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        currentJob = JobStatus[currentJobStatus.upper()]
    except KeyError:
        return jsonify({"error": "Invalid job status"}), 400

    new_user = UserProfile(name, email, password, adhar, phone, expectedSalary, portfolio, jobLocation, projects, currentJob, skills)
    response = users_db.addUser(new_user)

    return jsonify({"message": response})

@app.route('/userRegister', methods=['POST'])
def userRegister():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if any(user.email == email for user in users_db.users.values()):
        return jsonify({"error": "User with this email already exists"}), 409

    return jsonify({"message": "User registered successfully!"})

@app.route('/filter', methods=['GET'])
def filter_candidates():
    expectedSalary = request.args.get('expectedSalary', type=int)
    jobLocation = request.args.get('jobLocation')
    currentJobStatus = request.args.get('currentJobStatus')
    skills = request.args.getlist('skills')

    filtered_users = users_db.filterUsers(expectedSalary, jobLocation, currentJobStatus, skills)

    return jsonify(filtered_users)

if __name__ == '__main__':
    app.run(debug=True)