from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# ══ MODELS ════════════════════════════════════════════════════════

class CourseRequest(BaseModel):
    title:       str = Field(..., min_length=3, max_length=100)
    instructor:  str = Field(..., min_length=2)
    price:       int = Field(..., ge=0)
    category:    str = Field(..., min_length=2)
    discount_percent: int = Field(0, ge=0, le=100)
    is_published: bool = True

class EnrollmentRequest(BaseModel):
    student_name: str = Field(..., min_length=2)
    email:        str = Field(..., min_length=5)

class CourseUpdateRequest(BaseModel):
    title:            Optional[str] = None
    instructor:       Optional[str] = None
    price:            Optional[int] = None
    category:         Optional[str] = None
    discount_percent: Optional[int] = None
    is_published:     Optional[bool] = None

# ══ DATA ══════════════════════════════════════════════════════════

courses = [
    {"id": 1, "title": "Python for Beginners", "instructor": "Alice", "price": 500, "Category": "Programming", "is_published": True, "discount_percent": 0, "final_price": 500},
    {"id": 2, "title": "Advanced FastAPI", "instructor": "Bob", "price": 750, "Category": "Programming", "is_published": True, "discount_percent": 0, "final_price": 675},
    {"id": 3, "title": "Gen AI", "instructor": "Deepak", "price": 1999, "Category": "Ai", "is_published": True, "discount_percent": 20, "final_price": 1599},
    {"id": 4, "title": "Everything About Data Science", "instructor": "Priya", "price": 2999, "Category": "Data Science", "is_published": False, "discount_percent": 15, "final_price": 2549},
]

enrollments     = []
enroll_counter  = 101
wishlist        = []

# ══ HELPERS ═══════════════════════════════════════════════════════

def find_course(course_id: int):
    for c in courses:
        if c['id'] == course_id:
            return c
    return None

def calculate_discount(price: int, discount_percent: int) -> int:
    return int(price * (1 - discount_percent / 100))

def is_duplicate_title(title: str) -> bool:
    return any(c['title'].lower() == title.lower() for c in courses)

def get_next_id() -> int:
    return max(c['id'] for c in courses) + 1

def find_enrollment(enrollment_id: int):
    for e in enrollments:
        if e['enrollment_id'] == enrollment_id:
            return e
    return None

def filter_logic(category: str = None, min_price: int = None, max_price: int = None, is_published: bool = None):
    result = courses
    if category is not None:
        result = [c for c in result if c['Category'].lower() == category.lower()]
    if min_price is not None:
        result = [c for c in result if c['price'] >= min_price]
    if max_price is not None:
        result = [c for c in result if c['price'] <= max_price]
    if is_published is not None:
        result = [c for c in result if c['is_published'] == is_published]
    return result

# ══ ENDPOINTS ═════════════════════════════════════════════════════

# ── Day 1 — Home & List ───────────────────────────────────────────

@app.get('/')
def home():
    return {'message': 'Welcome to the Online Course Platform API'}

@app.get('/courses')
def get_all_courses():
    return {'courses': courses, 'total': len(courses)}

# ── Day 2 — Summary ───────────────────────────────────────────────

@app.get('/courses/summary')
def get_summary():
    total_price = sum(c['price'] for c in courses)
    return {
        'total_courses': len(courses),
        'published': len([c for c in courses if c['is_published']]),
        'average_price': total_price / len(courses) if courses else 0
    }

# ── Day 6 — Search by Keyword ─────────────────────────────────────

@app.get('/courses/search')
def search_courses(
    keyword: str = Query(..., description='Search in titles or instructors'),
):
    results = [
        c for c in courses
        if keyword.lower() in c['title'].lower() or keyword.lower() in c['instructor'].lower()
    ]
    return {
    'keyword': keyword,
    'total_found': len(results),
    'message': 'No courses found matching your search.' if not results else f'{len(results)} course(s) found.',
    'results': results,
}

# ── Day 6 — Sort & Pagination ─────────────────────────────────────

@app.get('/courses/explore')
def explore_courses(
    sort_by: str = Query('price', description='price or title'),
    order:   str = Query('asc', description='asc or desc'),
    page:    int = Query(1, ge=1),
    limit:   int = Query(2, ge=1, le=10),
):
    if sort_by not in ('price', 'title'):
        return {'error': 'sort_by must be price or title'}
    if order not in ('asc', 'desc'):
        return {'error': 'order must be asc or desc'}

    sorted_data = sorted(courses, key=lambda c: c[sort_by], reverse=(order == 'desc'))
    
    start = (page - 1) * limit
    end   = start + limit
    paged = sorted_data[start:end]
    
    return {
        'page': page,
        'limit': limit,
        'order': order,
        'sort_by': sort_by,
        'total_pages': -(-len(courses) // limit),
        'results': paged
    }

# ── Day 4 — CRUD (Variable routes placed AFTER fixed) ─────────────

@app.get('/courses/{course_id}')
def get_course(course_id: int, response: Response):
    course = find_course(course_id)
    if not course:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Course not found'}
    return {'course': course}

@app.post('/courses', status_code=201)
def add_course(new_course: CourseRequest, response: Response):
    if is_duplicate_title(new_course.title):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Course title already exists'}
        
    course_entry = {
        'id': get_next_id(),
        **new_course.dict(),
        'final_price': calculate_discount(new_course.price, new_course.discount_percent)
    }
    courses.append(course_entry)
    return {'message': 'Course added', 'course': course_entry}

@app.put('/courses/{course_id}')
def update_course(course_id: int, updated_data: CourseUpdateRequest, response: Response):
    course = find_course(course_id)
    if not course:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Course not found'}
    
    for key, value in updated_data.dict().items():
        if value is not None:
            course[key] = value

    course['final_price'] = calculate_discount(course['price'], course['discount_percent'])
    
    return {'message': 'Course updated', 'course': course}

@app.delete('/courses/{course_id}')
def delete_course(course_id: int, response: Response):
    course = find_course(course_id)
    if not course:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Course not found'}

    if course['is_published']:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Cannot delete an active course. Unpublish it first.'}
        
    courses.remove(course)
    return {'message': f"Course '{course['title']}' deleted"}

#────── Q10───────────────────────────────────────────────────────
 
@app.get('/courses_filter')
def filter_courses(
    category:     str  = Query(None),
    min_price:    int  = Query(None, ge=0),
    max_price:    int  = Query(None, ge=0),
    is_published: bool = Query(None)
):
    result = filter_logic(category, min_price, max_price, is_published)
    return {'total': len(result), 'results': result}

# ── Day 5: Wishlist ───────────────────────────────────────────────────────
 
@app.get('/wishlist')
def get_wishlist():
    wishlist_courses = [find_course(cid) for cid in wishlist]
    total_price = sum(c['price'] for c in wishlist_courses if c)
    return {
        'total_items': len(wishlist),
        'total_price': total_price,
        'items': wishlist_courses
    }
 
@app.post('/wishlist/add')
def add_to_wishlist(course_id: int = Query(...)):
    course = find_course(course_id)
    if not course:
        return {'error': 'Course not found'}
    if course_id in wishlist:
        return {'message': 'Already in wishlist'}
    
    wishlist.append(course_id)
    return {'message': 'Added to wishlist', 'total_items': len(wishlist)}
 
@app.delete('/wishlist/remove')
def remove_from_wishlist(course_id: int = Query(...), response: Response = None):
    if course_id not in wishlist:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Course not in wishlist'}
    
    wishlist.remove(course_id)
    return {'message': 'Removed from wishlist', 'total_items': len(wishlist)}
 
@app.delete('/wishlist/clear')
def clear_wishlist():
    wishlist.clear()
    return {'message': 'Wishlist cleared'}
 
# ── Day 6 Enrollments ───────────────────────────────────────────────────
 
@app.get('/enrollments')
def get_all_enrollments():
    return {'total': len(enrollments), 'enrollments': enrollments}

@app.get('/enrollments/search')
def search_enrollments(
    keyword:  str = Query(None, description='Search by student name, email or course'),
    sort_by:  str = Query('enrollment_id', description='enrollment_id, student or course'),
    order:    str = Query('asc', description='asc or desc'),
    page:     int = Query(1, ge=1),
    limit:    int = Query(2, ge=1, le=10),
):
    if sort_by not in ('enrollment_id', 'student', 'course'):
        return {'error': 'sort_by must be enrollment_id, student or course'}
    if order not in ('asc', 'desc'):
        return {'error': 'order must be asc or desc'}

    result = enrollments

    # Search
    if keyword is not None:
        result = [
            e for e in result
            if keyword.lower() in e['student'].lower()
            or keyword.lower() in e['email'].lower()
            or keyword.lower() in e['course'].lower()
        ]

    # Sort
    result = sorted(result, key=lambda e: e[sort_by], reverse=(order == 'desc'))

    # Pagination
    start = (page - 1) * limit
    end   = start + limit
    paged = result[start:end]

    return {
        'total_found': len(result),
        'page': page,
        'limit': limit,
        'total_pages': -(-len(result) // limit) if result else 1,
        'results': paged,
        'message': 'No enrollments found.' if not result else f'{len(result)} enrollment(s) found.'
    }
 
@app.get('/enrollments/{enrollment_id}')
def get_enrollment(enrollment_id: int, response: Response):
    enrollment = find_enrollment(enrollment_id)
    if not enrollment:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Enrollment not found'}
    return {'enrollment': enrollment}
 
@app.post('/enrollment/checkout')
def checkout_enrollment(data: EnrollmentRequest, response: Response):
    global enroll_counter
    if not wishlist:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Wishlist is empty'}
    
    new_enrollments = []
    total_price = 0

    for cid in wishlist:
        course = find_course(cid)
        record = {
            'enrollment_id': enroll_counter,
            'course_id': cid,
            'student': data.student_name,
            'email': data.email,
            'course': course['title'],
            'price': course['final_price'],
            'status': 'active'
        }
        enrollments.append(record)
        new_enrollments.append(record)
        total_price += course['final_price']
        enroll_counter += 1
        
    wishlist.clear()
    response.status_code = status.HTTP_201_CREATED
    return {
        'message': 'Enrollment successful',
        'total_courses_enrolled': len(new_enrollments),
        'total_price': total_price,
        'enrolled_courses': new_enrollments
    }

@app.delete('/enrollments/{enrollment_id}')
def cancel_enrollment(enrollment_id: int, response: Response):
    enrollment = find_enrollment(enrollment_id)
    if not enrollment:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Enrollment not found'}
    
    enrollment['status'] = 'cancelled'
    return {'message': f"Enrollment {enrollment_id} cancelled", 'enrollment': enrollment}


@app.get('/courses-browse')
def browse_courses(
    keyword:      str  = Query(None, description='Search in title or instructor'),
    category:     str  = Query(None),
    min_price:    int  = Query(None, ge=0),
    max_price:    int  = Query(None, ge=0),
    is_published: bool = Query(None),
    sort_by:      str  = Query('price', description='price or title'),
    order:        str  = Query('asc', description='asc or desc'),
    page:         int  = Query(1, ge=1),
    limit:        int  = Query(2, ge=1, le=10),
):
    if sort_by not in ('price', 'title'):
        return {'error': 'sort_by must be price or title'}
    if order not in ('asc', 'desc'):
        return {'error': 'order must be asc or desc'}

    # Step 1 — Filter
    result = filter_logic(category, min_price, max_price, is_published)

    # Step 2 — Search
    if keyword is not None:
        result = [
            c for c in result
            if keyword.lower() in c['title'].lower()
            or keyword.lower() in c['instructor'].lower()
        ]

    # Step 3 — Sort
    result = sorted(result, key=lambda c: c[sort_by], reverse=(order == 'desc'))

    # Step 4 — Paginate
    start = (page - 1) * limit
    end   = start + limit
    paged = result[start:end]

    return {
        'total_found': len(result),
        'page': page,
        'limit': limit,
        'total_pages': -(-len(result) // limit) if result else 1,
        'results': paged,
        'message': 'No courses found.' if not result else f'{len(result)} course(s) found.'
    }