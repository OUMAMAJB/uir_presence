"""
Script pour mettre à jour les contraintes de clé étrangère avec CASCADE DELETE
Exécuter directement avec MySQL
"""
import mysql.connector

# Configuration de la base de données
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MYSQL123',
    'database': 'uir_presence'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    print("Connexion à la base de données réussie!")
    
    # Liste des requêtes SQL pour modifier les contraintes
    alter_queries = [
        # enrollments table
        ("ALTER TABLE enrollments DROP FOREIGN KEY enrollments_ibfk_1", True),
        ("ALTER TABLE enrollments DROP FOREIGN KEY enrollments_ibfk_2", True),
        ("ALTER TABLE enrollments ADD CONSTRAINT enrollments_student_fk FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE", False),
        ("ALTER TABLE enrollments ADD CONSTRAINT enrollments_subject_fk FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE", False),
        
        # teaching_assignments table
        ("ALTER TABLE teaching_assignments DROP FOREIGN KEY teaching_assignments_ibfk_1", True),
        ("ALTER TABLE teaching_assignments DROP FOREIGN KEY teaching_assignments_ibfk_2", True),
        ("ALTER TABLE teaching_assignments ADD CONSTRAINT ta_teacher_fk FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE", False),
        ("ALTER TABLE teaching_assignments ADD CONSTRAINT ta_subject_fk FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE", False),
        
        # track_teachers table
        ("ALTER TABLE track_teachers DROP FOREIGN KEY track_teachers_ibfk_1", True),
        ("ALTER TABLE track_teachers DROP FOREIGN KEY track_teachers_ibfk_2", True),
        ("ALTER TABLE track_teachers ADD CONSTRAINT tt_teacher_fk FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE", False),
        ("ALTER TABLE track_teachers ADD CONSTRAINT tt_track_fk FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE", False),
        
        # attendances table
        ("ALTER TABLE attendances DROP FOREIGN KEY attendances_ibfk_1", True),
        ("ALTER TABLE attendances DROP FOREIGN KEY attendances_ibfk_2", True),
        ("ALTER TABLE attendances ADD CONSTRAINT att_session_fk FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE", False),
        ("ALTER TABLE attendances ADD CONSTRAINT att_student_fk FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE", False),
        
        # sessions table
        ("ALTER TABLE sessions DROP FOREIGN KEY sessions_ibfk_1", True),
        ("ALTER TABLE sessions ADD CONSTRAINT sess_subject_fk FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE", False),
        
        # subjects table
        ("ALTER TABLE subjects DROP FOREIGN KEY subjects_ibfk_1", True),
        ("ALTER TABLE subjects DROP FOREIGN KEY subjects_ibfk_2", True),
        ("ALTER TABLE subjects ADD CONSTRAINT subj_track_fk FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE", False),
        ("ALTER TABLE subjects ADD CONSTRAINT subj_semester_fk FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE CASCADE", False),
        
        # semesters table
        ("ALTER TABLE semesters DROP FOREIGN KEY semesters_ibfk_1", True),
        ("ALTER TABLE semesters ADD CONSTRAINT sem_year_fk FOREIGN KEY (academic_year_id) REFERENCES academic_years(id) ON DELETE CASCADE", False),
        
        # tracks table
        ("ALTER TABLE tracks DROP FOREIGN KEY tracks_ibfk_1", True),
        ("ALTER TABLE tracks ADD CONSTRAINT trk_dept_fk FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE", False),
        
        # password_reset_tokens table
        ("ALTER TABLE password_reset_tokens DROP FOREIGN KEY password_reset_tokens_ibfk_1", True),
        ("ALTER TABLE password_reset_tokens ADD CONSTRAINT prt_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE", False),
    ]
    
    success_count = 0
    error_count = 0
    
    for query, can_fail in alter_queries:
        try:
            cursor.execute(query)
            conn.commit()
            print(f"✓ {query[:70]}...")
            success_count += 1
        except mysql.connector.Error as e:
            if can_fail:
                print(f"⚠ Ignoré (normal): {query[:50]}...")
            else:
                print(f"✗ Erreur: {query[:50]}... - {str(e)[:50]}")
            error_count += 1
    
    print(f"\n✅ Terminé: {success_count} requêtes réussies")
    print("Les suppressions en cascade sont maintenant activées!")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as e:
    print(f"Erreur de connexion: {e}")
