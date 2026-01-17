# RMP API

A simple API to fetch professor ratings from RateMyProfessors. Code taken from https://github.com/snow4060/rmp-api and translated to Python

## Running

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs on http://localhost:8000

## Endpoints

### GET /schools/{name}

Search for schools by name.

**Example:**
```
GET /schools/ottawa
```

**Response:**
```json
[
  {
    "id": "U2Nob29sLTE0NTI=",
    "legacyId": 1452,
    "name": "University of Ottawa",
    "city": "Ottawa",
    "state": "ON",
    "numRatings": 12345,
    "avgRatingRounded": 3.5
  }
]
```

---

### GET /professor/{school_id}/{name}

Get professor rating info.

**Example:**
```
GET /professor/U2Nob29sLTE0NTI=/John%20Smith
```

**Response (found):**
```json
{
  "found": true,
  "name": "John Smith",
  "avgRating": 4.2,
  "avgDifficulty": 3.1,
  "wouldTakeAgain": 85,
  "numRatings": 42,
  "department": "Computer Science",
  "link": "https://www.ratemyprofessors.com/professor/12345"
}
```

**Response (not found):**
```json
{
  "found": false
}
```

## Rate Limiting

Both endpoints are rate limited to 15 requests per minute per IP.
