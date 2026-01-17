from fastapi import FastAPI, Request
import requests

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

app = FastAPI()

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

SCHOOL_QUERY = """
query NewSearchSchoolsQuery($query: SchoolSearchQuery!) {
  newSearch {
    schools(query: $query) {
      edges {
        node {
          id
          legacyId
          name
          city
          state
          numRatings
          avgRatingRounded
        }
      }
    }
  }
}
"""

TEACHER_QUERY = """
query TeacherSearchResultsPageQuery(
  $query: TeacherSearchQuery!
  $schoolID: ID
  $includeSchoolFilter: Boolean!
) {
  search: newSearch {
    teachers(query: $query, first: 1) {
      edges {
        node {
          firstName
          lastName
          avgRating
          avgDifficulty
          wouldTakeAgainPercent
          numRatings
          department
          legacyId
        }
      }
    }
  }
}
"""

@app.get("/schools/{name}")
@limiter.limit("15/minute")
def search_schools(request: Request, name: str):
    payload = {
        "query": SCHOOL_QUERY,
        "variables": {"query": {"text": name}},
    }

    r = requests.post(RMP_URL, headers=HEADERS, json=payload, timeout=10)
    data = r.json()

    return [
        s["node"]
        for s in data["data"]["newSearch"]["schools"]["edges"]
    ]


@app.get("/professor/{school_id}/{name}")
@limiter.limit("15/minute")
def get_professor(
    request: Request,
    school_id: str,
    name: str
):
    payload = {
        "query": TEACHER_QUERY,
        "variables": {
            "query": {
                "text": name,
                "schoolID": school_id,
                "fallback": True,
                "departmentID": None,
            },
            "schoolID": school_id,
            "includeSchoolFilter": True,
        },
    }

    r = requests.post(RMP_URL, headers=HEADERS, json=payload, timeout=10)
    data = r.json()

    edges = data["data"]["search"]["teachers"]["edges"]
    if not edges:
        return {"found": False}

    t = edges[0]["node"]
    return {
        "found": True,
        "name": f'{t["firstName"]} {t["lastName"]}',
        "avgRating": t["avgRating"],
        "avgDifficulty": t["avgDifficulty"],
        "wouldTakeAgain": t["wouldTakeAgainPercent"],
        "numRatings": t["numRatings"],
        "department": t["department"],
        "link": f'https://www.ratemyprofessors.com/professor/{t["legacyId"]}',
    }