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

TEACHER_RATINGS_QUERY = """
query TeacherRatingsPageQuery(
  $id: ID!
) {
  node(id: $id) {
    __typename
    ... on Teacher {
      id
      legacyId
      firstName
      lastName
      department
      school {
        legacyId
        name
        city
        state
        id
      }
      avgRating
      avgDifficulty
      numRatings
      wouldTakeAgainPercent
      teacherRatingTags {
        tagName
      }
      courseCodes {
        courseCount
        courseName
      }
      ratings(first: 20) {
        edges {
          node {
            comment
            clarityRating
            helpfulRating
            difficultyRating
            date
            class
            grade
            ratingTags
            wouldTakeAgain
            textbookUse
          }
        }
      }
      relatedTeachers {
        legacyId
        firstName
        lastName
        avgRating
      }
    }
  }
}
"""
