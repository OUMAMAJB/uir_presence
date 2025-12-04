from app import db
from flask_login import UserMixin
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # admin, admin_dept, admin_filiere, enseignant, etudiant
    users = db.relationship('User', backref='role', lazy=True, cascade='all, delete-orphan')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    # Foreign keys for hierarchy
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=True)
    
    # Année académique pour les étudiants (1ère année, 2ème année, etc.)
    academic_year = db.Column(db.Integer, nullable=True)  # 1, 2, 3, 4, 5...

    # Relationships
    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    tracks_taught = db.relationship('Track', secondary='track_teachers', backref=db.backref('teachers', lazy=True))
    department = db.relationship('Department', backref='users', foreign_keys=[department_id])
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    # ========== ROLE HELPER PROPERTIES (Dynamic Role System) ==========
    
    @property
    def is_super_admin(self):
        """Check if user is Super Admin"""
        return self.role.name in ['admin', 'super_admin']
    
    @property
    def is_teacher(self):
        """Check if user has teacher capabilities (includes all staff roles)"""
        return self.role.name in ['admin', 'super_admin', 'admin_dept', 'admin_filiere', 'enseignant']
    
    @property
    def is_student(self):
        """Check if user is a student"""
        return self.role.name == 'etudiant'
    
    @property
    def is_dept_head(self):
        """Check if user is head of any department (additive role)"""
        from app.models import Department
        return Department.query.filter_by(head_id=self.id).first() is not None
    
    @property
    def is_track_head(self):
        """Check if user is head of any track/filière (additive role)"""
        from app.models import Track
        return Track.query.filter_by(head_id=self.id).first() is not None
    
    @property
    def managed_departments(self):
        """Get list of departments this user manages"""
        from app.models import Department
        return Department.query.filter_by(head_id=self.id).all()
    
    @property
    def managed_tracks(self):
        """Get list of tracks/filières this user manages"""
        from app.models import Track
        return Track.query.filter_by(head_id=self.id).all()
    
    @property
    def dashboard_tabs(self):
        """Get list of dashboard tabs available to this user"""
        tabs = []
        
        if self.is_teacher:
            tabs.append({'id': 'courses', 'name': 'Mes Cours', 'icon': 'book'})
        
        if self.is_dept_head or self.is_super_admin:
            tabs.append({'id': 'department', 'name': 'Gestion Département', 'icon': 'building'})
        
        if self.is_track_head:
            tabs.append({'id': 'track', 'name': 'Gestion Filière', 'icon': 'users'})
        
        return tabs

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    head_id = db.Column(db.Integer, db.ForeignKey('users.id', use_alter=True, name='fk_dept_head'), nullable=True)
    
    tracks = db.relationship('Track', backref='department', lazy=True, cascade='all, delete-orphan')
    # Teachers are assigned to departments via User.department_id

class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    head_id = db.Column(db.Integer, db.ForeignKey('users.id', use_alter=True, name='fk_track_head'), nullable=True)
    
    subjects = db.relationship('Subject', backref='track', lazy=True, cascade='all, delete-orphan')
    students = db.relationship('User', backref='enrolled_track', lazy=True, foreign_keys=[User.track_id])

class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) # e.g., "1ère Année", "2023-2024"
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=True)
    
    track = db.relationship('Track', backref='academic_years')
    semesters = db.relationship('Semester', backref='academic_year', lazy=True, cascade='all, delete-orphan')

class Semester(db.Model):
    __tablename__ = 'semesters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False) # S1, S2, etc.
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=True)
    
    subjects = db.relationship('Subject', backref='semester', lazy=True, cascade='all, delete-orphan')
    track = db.relationship('Track', backref='semesters')

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    # teacher_id removed in favor of Many-to-Many relationship
    
    total_sessions_cm = db.Column(db.Integer, default=0)
    total_sessions_td = db.Column(db.Integer, default=0)
    total_sessions_tp = db.Column(db.Integer, default=0)
    
    # Relationships
    sessions = db.relationship('Session', backref='subject', lazy=True, cascade='all, delete-orphan')
    
    # Many-to-Many for students enrolled in this subject
    students = db.relationship('User', secondary='enrollments', backref=db.backref('enrolled_subjects', lazy=True))
    
    # Many-to-Many for teachers assigned to this subject
    teachers = db.relationship('User', secondary='teaching_assignments', backref=db.backref('teaching_subjects', lazy=True))

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Enseignant qui a créé la séance
    type = db.Column(db.String(10), nullable=False) # CM, TD, TP
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    qr_code_token = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, nullable=True)  # Quand la séance a été démarrée
    stopped_at = db.Column(db.DateTime, nullable=True)  # Quand la séance a été arrêtée
    
    attendances = db.relationship('Attendance', backref='session', lazy=True, cascade='all, delete-orphan')
    teacher = db.relationship('User', backref='sessions_created', foreign_keys=[teacher_id])

class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='absent') # present, absent
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Association Tables
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True)
)

teaching_assignments = db.Table('teaching_assignments',
    db.Column('teacher_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True)
)

track_teachers = db.Table('track_teachers',
    db.Column('teacher_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('track_id', db.Integer, db.ForeignKey('tracks.id', ondelete='CASCADE'), primary_key=True)
)

import secrets
from datetime import timedelta

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reset_tokens')
    
    @staticmethod
    def create_token(user_id, expires_in_hours=24):
        """Crée un nouveau token pour un utilisateur"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(reset_token)
        db.session.commit()
        
        return token
    
    @staticmethod
    def verify_token(token):
        """Vérifie si un token est valide"""
        reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()
        
        if not reset_token:
            return None
        
        if reset_token.expires_at < datetime.utcnow():
            return None
        
        return reset_token



