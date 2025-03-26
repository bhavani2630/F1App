from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from firebase_admin import credentials, firestore, auth, initialize_app
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

# Initialize FastAPI
app = FastAPI()

# Middleware for session management
app.add_middleware(SessionMiddleware, secret_key="AIzaSyDOEhmnPgk5clxHn8dWR_oXx-Jv1aS_6BU")

# Load Firebase credentials
cred = credentials.Certificate("f1-app-61258-firebase-adminsdk-fbsvc-a77194ad01.json") 
firebase_app = initialize_app(cred)
db = firestore.client()

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Template rendering (HTML files)
templates = Jinja2Templates(directory="templates")

# ------------------------------ Data Models ------------------------------

class User(BaseModel):
    email: str
    password: str

class Driver(BaseModel):
    name: str
    age: int
    team: str
    pole_positions: int
    race_wins: int
    points_scored: int
    world_titles: int
    fastest_laps: int

class Team(BaseModel):
    name: str
    year_founded: int
    pole_positions: int
    race_wins: int
    constructor_titles: int
    last_season_finish: int

# ------------------------------ Routes ------------------------------

# ✅ Home Page (Pass session data)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

# ✅ Login Page (GET)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("login.html", {"request": request, "user": user})

# ✅ User Login (POST)
@app.post("/login")
async def login(user: User, request: Request):
    try:
        firebase_user = auth.get_user_by_email(user.email)
        request.session["user"] = firebase_user.email  # Store email in session
        return JSONResponse(content={"message": "Login successful!"}, status_code=200)
    except:
        raise HTTPException(status_code=401, detail="Invalid credentials!")

# ✅ User Registration (POST)
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("register.html", {"request": request, "user": user})

# ✅ User Logout
@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")

# ✅ Add a Driver (GET and POST)
@app.get("/add_driver", response_class=HTMLResponse)
async def add_driver_page(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Please log in first!")
    return templates.TemplateResponse("add_driver.html", {"request": request, "user": user})

@app.post("/add_driver")
async def add_driver(driver: Driver, request: Request):
    if "user" not in request.session:
        raise HTTPException(status_code=401, detail="Please log in first!")
    db.collection("drivers").document(driver.name).set(driver.dict())
    return JSONResponse(content={"message": "Driver added successfully!"}, status_code=201)

# ✅ Add a Team (GET and POST)
@app.get("/add_team", response_class=HTMLResponse)
async def add_team_page(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Please log in first!")
    return templates.TemplateResponse("add_team.html", {"request": request, "user": user})

@app.post("/add_team")
async def add_team(team: Team, request: Request):
    if "user" not in request.session:
        raise HTTPException(status_code=401, detail="Please log in first!")
    db.collection("teams").document(team.name).set(team.dict())
    return JSONResponse(content={"message": "Team added successfully!"}, status_code=201)


# ✅ Edit Driver (GET - Display form with current data)
@app.get("/edit_driver/{driver_name}", response_class=HTMLResponse)
async def edit_driver_page(request: Request, driver_name: str):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Please log in first!")
    driver_doc = db.collection("drivers").document(driver_name).get()
    if not driver_doc.exists:
        raise HTTPException(status_code=404, detail="Driver not found!")
    driver = driver_doc.to_dict()
    return templates.TemplateResponse("edit_driver.html", {"request": request, "user": user, "driver": driver})

# ✅ Edit Driver (POST - Update driver data)
@app.post("/edit_driver/{driver_name}")
async def edit_driver(driver_name: str, driver: Driver, request: Request):
    if "user" not in request.session:
        raise HTTPException(status_code=401, detail="Please log in first!")
    driver_doc = db.collection("drivers").document(driver_name)
    if not driver_doc.get().exists:
        raise HTTPException(status_code=404, detail="Driver not found!")
    driver_doc.set(driver.dict())
    return JSONResponse(content={"message": "Driver updated successfully!"}, status_code=200)

# ✅ Delete Driver (POST - Remove driver)
@app.post("/delete_driver/{driver_name}")
async def delete_driver(driver_name: str, request: Request):
    if "user" not in request.session:
        raise HTTPException(status_code=401, detail="Please log in first!")
    driver_doc = db.collection("drivers").document(driver_name)
    if not driver_doc.get().exists:
        raise HTTPException(status_code=404, detail="Driver not found!")
    driver_doc.delete()
    return JSONResponse(content={"message": "Driver deleted successfully!"}, status_code=200)

# ✅ Query Drivers (GET)
@app.get("/query_drivers", response_class=HTMLResponse)
async def query_drivers_page(request: Request):
    user = request.session.get("user")
    drivers_docs = db.collection("drivers").stream()
    drivers = [doc.to_dict() for doc in drivers_docs]
    return templates.TemplateResponse("query_drivers.html", {"request": request, "user": user, "drivers": drivers})

# ✅ Compare Drivers (GET)
@app.get("/compare_drivers", response_class=HTMLResponse)
async def compare_drivers_page(request: Request):
    user = request.session.get("user")
    drivers_docs = db.collection("drivers").stream()
    drivers = [doc.to_dict() for doc in drivers_docs]
    return templates.TemplateResponse("compare_drivers.html", {"request": request, "user": user, "drivers": drivers})

# ------------------------------ Run Application ------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)