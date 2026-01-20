from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import requests
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from queries import SCHOOL_QUERY, TEACHER_QUERY, TEACHER_RATINGS_QUERY
from utils import encode_school_id, encode_teacher_id

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(_, __):
    return JSONResponse(status_code=429, content={"error": "rate limit exceeded"})

RMP_URL = "https://www.ratemyprofessors.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Basic dGVzdDp0ZXN0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.ratemyprofessors.com/",
    "Origin": "https://www.ratemyprofessors.com",
}

@app.get("/schools/{name}")
@limiter.limit("15/minute")
def search_schools(request: Request, name: str):
    payload = {
        "query": SCHOOL_QUERY,
        "variables": {"query": {"text": name}},
    }

    r = requests.post(RMP_URL, headers=HEADERS, json=payload, timeout=10)
    data = r.json()

    # Handle possible empty/error responses safely
    try:
        schools_data = data["data"]["newSearch"]["schools"]["edges"]
        return [s["node"] for s in schools_data]
    except (KeyError, TypeError):
        return []

@app.get("/professor/{school_id}/{name}")
@app.get("/professors/{school_id}/{name}")
@limiter.limit("15/minute")
def get_professor(
    request: Request,
    school_id: str,
    name: str,
    ratings: bool = False,
    related: bool = False
):
    encoded_school_id = encode_school_id(school_id)
    # 1. Search for the professor
    search_payload = {
        "query": TEACHER_QUERY,
        "variables": {
            "query": {
                "text": name,
                "schoolID": encoded_school_id,
                "fallback": True,
                "departmentID": None,
            },
        },
    }

    r = requests.post(RMP_URL, headers=HEADERS, json=search_payload, timeout=10)
    data = r.json()

    edges = data.get("data", {}).get("search", {}).get("teachers", {}).get("edges", [])
    if not edges:
        return {"found": False}

    teacher_summary = edges[0]["node"]
    legacy_id = teacher_summary["legacyId"]
    
    # 2. Fetch detailed professor data
    encoded_teacher_id_str = encode_teacher_id(legacy_id)
    details_payload = {
        "query": TEACHER_RATINGS_QUERY,
        "variables": {"id": encoded_teacher_id_str},
    }
    
    r_details = requests.post(RMP_URL, headers=HEADERS, json=details_payload, timeout=10)
    details_data = r_details.json()
    
    node = details_data.get("data", {}).get("node", {})
    if not node:
        return {"found": False}

    # 3. Minimize and format data
    
    # Courses
    course_codes = node.get("courseCodes", [])
    courses = [{"name": c["courseName"], "count": c["courseCount"]} for c in course_codes]
    courses.sort(key=lambda x: x["count"], reverse=True) # Sort by most common

    # Tags
    tags_data = node.get("teacherRatingTags", [])
    tags = [t["tagName"] for t in tags_data]

    result = {
        "found": True,
        "id": node.get("legacyId"),
        "firstName": node.get("firstName"),
        "lastName": node.get("lastName"),
        "name": f"{node.get('firstName')} {node.get('lastName')}",
        "department": node.get("department"),
        "school": {
            "name": node.get("school", {}).get("name"),
            "id": node.get("school", {}).get("legacyId"),
            "city": node.get("school", {}).get("city"),
            "state": node.get("school", {}).get("state"),
        },
        "avgRating": node.get("avgRating"),
        "avgDifficulty": node.get("avgDifficulty"),
        "numRatings": node.get("numRatings"),
        "wouldTakeAgainPercent": node.get("wouldTakeAgainPercent"),
        "courses": courses,
        "tags": tags,
    }

    # Optional: Ratings
    if ratings:
        raw_ratings = node.get("ratings", {}).get("edges", [])
        ratings_list = []
        for edge in raw_ratings:
            r_node = edge["node"]
            ratings_list.append({
                "comment": r_node.get("comment"),
                "clarity": r_node.get("clarityRating"),
                "helpful": r_node.get("helpfulRating"),
                "difficulty": r_node.get("difficultyRating"),
                "date": r_node.get("date"),
                "class": r_node.get("class"),
                "grade": r_node.get("grade"),
                "tags": r_node.get("ratingTags", "").split("--") if r_node.get("ratingTags") else [],
                "takeAgain": r_node.get("wouldTakeAgain"),
                "textbook": r_node.get("textbookUse")
            })
        result["ratings"] = ratings_list

    # Optional: Related Professors
    if related:
        result["relatedProfessors"] = [
             {
                 "id": rt.get("legacyId"), 
                 "d": f"{rt.get('firstName')} {rt.get('lastName')}",
                 "rating": rt.get("avgRating")
             } 
             for rt in node.get("relatedTeachers", [])
        ]

    return result