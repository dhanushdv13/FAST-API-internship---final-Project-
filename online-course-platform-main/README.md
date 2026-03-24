# 📚 Online Course Platform API

A RESTful API built with **FastAPI** for managing online courses, enrollments, and wishlists.

---

## 🚀 Getting Started

### Install dependencies
```bash
pip install fastapi uvicorn
```

### Run the server
```bash
uvicorn main:app --reload
```

### Open Swagger UI
```
http://127.0.0.1:8000/docs
```

---

## 🗂️ Project Structure
```
online-course-platform/
├── screenshots/                  # Test and submissions
├── main.py                       # Main application file
├── README.md                     # Project documentation
└── requirements.txt              # Project dependencies
```

`main.py` is organized into sections:
- **Models** — Pydantic models for request validation
- **Data** — In-memory courses, enrollments and wishlist
- **Helpers** — Reusable logic functions
- **Endpoints** — All API routes

---

## 📦 Models

| Model | Purpose |
|---|---|
| `CourseRequest` | Validate new course creation |
| `CourseUpdateRequest` | Partial update with all optional fields |
| `EnrollmentRequest` | Validate student checkout details |

---

## 🔧 Helper Functions

| Helper | Purpose |
|---|---|
| `find_course(id)` | Lookup course by ID |
| `find_enrollment(id)` | Lookup enrollment by ID |
| `calculate_discount(price, percent)` | Returns final price after discount |
| `is_duplicate_title(title)` | Checks if course title already exists |
| `get_next_id()` | Auto-increments course ID |
| `filter_logic(...)` | Filters courses by category, price, published status |

---

## 🛣️ API Endpoints

### General
| Method | Route | Description |
|---|---|---|
| GET | `/` | Welcome message |

---

### Courses
| Method | Route | Description |
|---|---|---|
| GET | `/courses` | Get all courses |
| GET | `/courses/summary` | Total, published count, average price |
| GET | `/courses/search?keyword=` | Search by title or instructor |
| GET | `/courses/explore` | Sort + paginate courses |
| GET | `/courses_filter` | Filter by category, price, published |
| GET | `/courses-browse` | Combined search + filter + sort + pagination |
| GET | `/courses/{course_id}` | Get single course by ID |
| POST | `/courses` | Add new course (201) |
| PUT | `/courses/{course_id}` | Partial update course |
| DELETE | `/courses/{course_id}` | Delete course (only if unpublished) |

---

### Wishlist
| Method | Route | Description |
|---|---|---|
| GET | `/wishlist` | View wishlist with total price |
| POST | `/wishlist/add?course_id=` | Add course to wishlist |
| DELETE | `/wishlist/remove?course_id=` | Remove course from wishlist |
| DELETE | `/wishlist/clear` | Clear entire wishlist |

---

### Enrollments
| Method | Route | Description |
|---|---|---|
| GET | `/enrollments` | Get all enrollments |
| GET | `/enrollments/search` | Search + sort + paginate enrollments |
| GET | `/enrollments/{enrollment_id}` | Get single enrollment |
| POST | `/enrollment/checkout` | Checkout wishlist → create enrollments (201) |
| DELETE | `/enrollments/{enrollment_id}` | Cancel enrollment |

---

## 🔄 Enrollment Workflow
```
1. POST /wishlist/add?course_id=1       → Add course to wishlist
2. POST /wishlist/add?course_id=2       → Add another course
3. POST /enrollment/checkout            → Checkout with student details
                                          Wishlist is cleared automatically
```

---

## ✅ Validations & Business Rules

- Course title must be **unique** (duplicate check on POST)
- Course **cannot be deleted** if `is_published = True` — unpublish first
- `discount_percent` must be between `0` and `100`
- `final_price` is auto-calculated on create and update
- Partial updates — only provided fields are updated, rest stay unchanged
- `sort_by` only accepts `price` or `title` — invalid values return error
- `order` only accepts `asc` or `desc`

---

## 📋 Query Parameters

### `/courses/explore`
| Param | Default | Options |
|---|---|---|
| `sort_by` | `price` | `price`, `title` |
| `order` | `asc` | `asc`, `desc` |
| `page` | `1` | ≥ 1 |
| `limit` | `2` | 1–10 |

### `/courses-browse`
| Param | Default | Description |
|---|---|---|
| `keyword` | None | Search in title or instructor |
| `category` | None | Filter by category |
| `min_price` | None | Minimum price filter |
| `max_price` | None | Maximum price filter |
| `is_published` | None | Filter by published status |
| `sort_by` | `price` | `price` or `title` |
| `order` | `asc` | `asc` or `desc` |
| `page` | `1` | Page number |
| `limit` | `2` | Results per page |

---

## 🧪 Sample Course Data

| ID | Title | Instructor | Price | Discount | Final Price | Published |
|---|---|---|---|---|---|---|
| 1 | Python for Beginners | Alice | 500 | 0% | 500 | ✅ |
| 2 | Advanced FastAPI | Bob | 750 | 10% | 675 | ✅ |
| 3 | Gen AI | Deepak | 1999 | 20% | 1599 | ✅ |
| 4 | Everything About Data Science | Priya | 2999 | 15% | 2549 | ❌ |

---

## 🛠️ Tech Stack

| Package | Version |
|---|---|
| Python | 3.13 |
| FastAPI | 0.135.1 |
| Pydantic | 2.12.5 |
| Uvicorn | 0.42.0 |
| Starlette | 0.52.1 |
| AnyIO | 4.12.1 |