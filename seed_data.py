from app import create_app, db
from app.models import AcademicYear, Semester, Role

app = create_app()

with app.app_context():
    # Create Academic Year
    year_name = "2024-2025"
    academic_year = AcademicYear.query.filter_by(name=year_name).first()
    if not academic_year:
        academic_year = AcademicYear(name=year_name)
        db.session.add(academic_year)
        db.session.commit()
        print(f"Created Academic Year: {year_name}")
    else:
        print(f"Academic Year {year_name} already exists")
        
    # Create Semesters
    semesters = ["S1", "S2", "S3", "S4", "S5", "S6"]
    for sem_name in semesters:
        semester = Semester.query.filter_by(name=sem_name, academic_year_id=academic_year.id).first()
        if not semester:
            semester = Semester(name=sem_name, academic_year_id=academic_year.id)
            db.session.add(semester)
            print(f"Created Semester: {sem_name}")
        else:
            print(f"Semester {sem_name} already exists")
            
    # Ensure Roles exist
    roles = ['admin', 'admin_dept', 'admin_filiere', 'enseignant', 'etudiant']
    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)
            print(f"Created Role: {role_name}")
            
    db.session.commit()
    print("Seeding completed.")
