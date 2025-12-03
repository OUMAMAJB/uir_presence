# UIR Presence API Documentation

## Authentication Routes

### POST `/auth/login`
Login to the system.

**Request Body:**
```json
{
  "email": "user@uir.ac.ma",
  "password": "password"
}
```

**Responses:**
- `302`: Redirect to role-appropriate dashboard
- `400`: Invalid credentials

---

### GET `/auth/logout`
Logout from the system.

**Responses:**
- `302`: Redirect to login page

---

## Admin Routes

### GET `/admin/dashboard`
View admin dashboard with department list.

**Authentication:** Required (admin only)

**Response:** HTML page

---

### GET `/admin/department/new`
Show create department form.

**Authentication:** Required (admin only)

**Response:** HTML form

---

### POST` `/admin/department/new`
Create a new department.

**Authentication:** Required (admin only)

**Request Body:**
```json
{
  "name": "Computer Science"
}
```

**Responses:**
- `302`: Redirect to dashboard on success
- `400`: Department already exists

---

### GET `/admin/teacher/add`
Show add teacher form.

**Authentication:** Required (admin only)

**Response:** HTML form

---

### POST `/admin/teacher/add`
Add a new teacher.

**Authentication:** Required (admin only)

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@uir.ac.ma",
  "department_id": 1
}
```

**Responses:**
- `302`: Redirect to dashboard on success
- `400`: User already exists or invalid data

---

## Department Admin Routes

### GET `/department/dashboard`
View department dashboard with track list.

**Authentication:** Required (department admin or teacher)

**Response:** HTML page

---

### GET `/department/track/create`
Show create track form.

**Authentication:** Required (department head only)

**Response:** HTML form

---

### POST `/department/track/create`
Create a new track.

**Authentication:** Required (department head only)

**Request Body:**
```json
{
  "name": "Software Engineering"
}
```

**Responses:**
- `302`: Redirect to dashboard on success
- `400`: Track already exists

---

## Track Admin Routes

### GET `/track/dashboard`
View track dashboard with subject list.

**Authentication:** Required (track admin or teacher)

**Response:** HTML page

---

## Teacher Routes

### GET `/teacher/dashboard`
View teacher dashboard with assigned subjects.

**Authentication:** Required (teacher, dept admin, track admin)

**Response:** HTML page

---

### GET `/teacher/session/create/<int:subject_id>`
Show create session form.

**Authentication:** Required (teacher for that subject)

**Response:** HTML form

---

### POST `/teacher/session/create/<int:subject_id>`
Create a new session.

**Authentication:** Required (teacher for that subject)

**Request Body:**
```json
{
  "type": "CM",
  "date": "2024-12-10",
  "start_time": "09:00",
  "end_time": "11:00"
}
```

**Responses:**
- `302`: Redirect to dashboard on success
- `400`: Invalid data

---

### GET `/teacher/session/<int:session_id>/qr`
View QR code page for a session.

**Authentication:** Required (teacher for that subject)

**Response:** HTML page with QR code interface

---

### POST `/teacher/session/<int:session_id>/start`
Start a session and generate initial QR token.

**Authentication:** Required (teacher for that subject)

**Response:**
```json
{
  "success": true,
  "token": "unique_qr_token_string"
}
```

---

### POST `/teacher/session/<int:session_id>/refresh_token`
Refresh the QR token (called every 15 seconds).

**Authentication:** Required (teacher for that subject)

**Response:**
```json
{
  "success": true,
  "token": "new_unique_qr_token_string"
}
```

---

### POST `/teacher/session/<int:session_id>/stop`
Stop a session and invalidate QR token.

**Authentication:** Required (teacher for that subject)

**Response:**
```json
{
  "success": true
}
```

---

## Student Routes

### GET `/student/dashboard`
View student dashboard with attendance statistics.

**Authentication:** Required (student only)

**Response:** HTML page with attendance data

**Response includes:**
- List of enrolled subjects
- Attendance counts per subject
- Rattrapage status per subject
- Attendance percentage

---

### POST `/student/scan_qr`
Scan QR code and register attendance.

**Authentication:** Required (student only)

**Request Body:**
```json
{
  "token": "scanned_qr_token_string"
}
```

**Responses:**

**Success (200):**
```json
{
  "success": true,
  "message": "Attendance recorded for Computer Science - CM"
}
```

**Error (400):**
```json
{
  "error": "Invalid or expired QR code"
}
```
OR
```json
{
  "error": "You are not enrolled in this subject"
}
```
OR
```json
{
  "error": "You have already registered attendance for this session"
}
```

---

## Main Routes

### GET `/`
Root redirect to appropriate dashboard based on user role.

**Authentication:** Required

**Responses:**
- `/admin/dashboard` for admin
- `/department/dashboard` for department admin
- `/track/dashboard` for track admin
- `/teacher/dashboard` for teachers
- `/student/dashboard` for students

---

## Error Codes

- **200**: Success
- **302**: Redirect
- **400**: Bad Request / Validation Error
- **401**: Unauthorized
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found

---

## Authentication

All routes (except `/auth/login`) require authentication via session cookies. Flask-Login manages sessions automatically.

To access protected routes:
1. Login via `/auth/login`
2. Session cookie is automatically set
3. Subsequent requests include session cookie
4. Logout via `/auth/logout` to clear session

---

## Security Notes

### QR Code Tokens
- Generated using `secrets.token_urlsafe(32)`
- Valid only while session is active (`is_active = True`)
- Automatically refreshed every 15 seconds
- Invalidated when session is stopped

### Password Security
**Note:** Current implementation uses plain text passwords. **This should be changed to hashed passwords using `werkzeug.security.generate_password_hash` and `check_password_hash` before production deployment.**

### Role-Based Access Control
Each route is protected with custom decorators:
- `@admin_required`
- `@department_admin_required`
- `@track_admin_required`
- `@teacher_required`
- `@student_required`

---

## Rate Limiting

**Not yet implemented.** Consider adding rate limiting for:
- Login attempts
- QR scanning
- API endpoints

---

## Future API Endpoints

### Planned Features
- `POST /admin/teacher/import` - Import teachers from Excel
- `POST /track/student/import` - Import students from Excel
- `GET /teacher/attendance/<session_id>` - Get attendance list
- `GET /teacher/statistics/<subject_id>` - Get subject statistics
- `POST /admin/department/<dept_id>/head` - Assign department head
- `POST /department/track/<track_id>/head` - Assign track head
- `GET /export/attendance` - Export attendance reports

---

## Webhook Events (Future)

Planned webhook events for external integrations:
- `student.rattrapage_triggered` - When student reaches rattrapage threshold
- `session.started` - When teacher starts a session
- `session.ended` - When teacher stops a session
- `attendance.recorded` - When student scans QR code

---

## Data Models

### User
```json
{
  "id": 1,
  "email": "user@uir.ac.ma",
  "first_name": "John",
  "last_name": "Doe",
  "role_id": 4,
  "department_id": 1,
  "track_id": null
}
```

### Session
```json
{
  "id": 1,
  "subject_id": 1,
  "type": "CM",
  "date": "2024-12-10",
  "start_time": "09:00:00",
  "end_time": "11:00:00",
  "qr_code_token": "unique_token",
  "is_active": true
}
```

### Attendance
```json
{
  "id": 1,
  "session_id": 1,
  "student_id": 5,
  "status": "present",
  "timestamp": "2024-12-10T09:05:30"
}
```

---

*Last updated: December 2024*
