# RMP API

A simple API to fetch professor ratings from RateMyProfessors. Code taken from https://github.com/snow4060/rmp-api and translated to Python.

Publicly running version is available at https://rmp.akramb.com/

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
  "id": 14890,
  "firstName": "Steve",
  "lastName": "Desjardins",
  "name": "Steve Desjardins",
  "department": "Mathematics",
  "school": {
    "name": "University of Ottawa",
    "id": 1452,
    "city": "Ottawa",
    "state": "ON"
  },
  "avgRating": 4.5,
  "avgDifficulty": 2.1,
  "numRatings": 307,
  "wouldTakeAgainPercent": 92.3077,
  "courses": [
    { "name": "MAT1320", "count": 98 },
    { "name": "MAT2384", "count": 52 },
    { "name": "MAT1322", "count": 46 }
  ],
  "tags": [
    "Tough grader",
    "Amazing lectures",
    "Respected"
  ],
  "ratings": [
    {
      "comment": "Great prof, explains things well...",
      "clarity": 5,
      "helpful": 5,
      "difficulty": 3,
      "date": "2026-01-13 23:23:51 +0000 UTC",
      "class": "MAT1320",
      "grade": "D+",
      "tags": ["Amazing lectures", "Respected"],
      "takeAgain": 1,
      "textbook": -1
    }
  ],
  "relatedProfessors": [
    {
      "id": 2225832,
      "d": "Jason Bramburger",
      "rating": 5.0
    }
  ]
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
