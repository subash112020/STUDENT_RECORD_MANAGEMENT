"""
FLASK WEB SERVER - Student Record Manager
REST API + Web Interface
Run: python app_flask_server.py
Access: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from student_record_manager_v2 import StudentRecordManager
import json

app = Flask(__name__, template_folder=".")
manager = StudentRecordManager()

# ==================== HELPER FUNCTIONS ====================

def success_response(message, data=None, status_code=200):
    """Return standardized success response"""
    response = {"success": True, "message": message}
    if data:
        response["data"] = data
    return jsonify(response), status_code

def error_response(message, status_code=400):
    """Return standardized error response"""
    return jsonify({"success": False, "message": message}), status_code

# ==================== PAGE ROUTES ====================

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')

@app.route('/students-page')
def students_page():
    """View all students page"""
    return render_template('students.html')

@app.route('/add-page')
def add_page():
    """Add student page"""
    return render_template('add.html')

@app.route('/search-page')
def search_page():
    """Search student page"""
    return render_template('search.html')

@app.route('/update-page')
def update_page():
    """Update student page"""
    return render_template('update.html')

@app.route('/analytics-page')
def analytics_page():
    """Analytics page"""
    return render_template('analytics.html')

# ==================== API ROUTES - GET ====================

@app.route('/api/students', methods=['GET'])
def get_all_students():
    """Get all students"""
    try:
        students = manager.get_all_students()
        return success_response("Students retrieved successfully", students)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get single student by ID"""
    try:
        student = manager.get_student_details(student_id)
        if student:
            return success_response("Student found", student)
        else:
            return error_response(f"Student with ID {student_id} not found", 404)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/department/<dept>', methods=['GET'])
def get_by_department(dept):
    """Get students by department"""
    try:
        students = manager.get_students_by_department(dept)
        if students:
            return success_response(f"Students from {dept} department", students)
        else:
            return error_response(f"No students found in {dept} department", 404)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/top-performers', methods=['GET'])
def get_top_performers():
    """Get top performing students"""
    try:
        limit = request.args.get('limit', 5, type=int)
        students = manager.get_top_performers(limit)
        return success_response(f"Top {limit} performers retrieved", students)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get class statistics"""
    try:
        students = manager.get_all_students()
        
        if not students:
            return error_response("No students found", 404)
        
        # Calculate statistics
        total_students = len(students)
        overall_avg = sum(s['average'] for s in students) / total_students
        
        # Subject-wise average
        subjects = ["English", "Tamil", "Maths", "Science", "Social"]
        subject_avgs = {}
        for subject in subjects:
            avg = sum(s['marks'].get(subject, 0) for s in students) / total_students
            subject_avgs[subject] = round(avg, 2)
        
        # Grade distribution
        grades = {}
        for student in students:
            grade = student['grade']
            grades[grade] = grades.get(grade, 0) + 1
        
        # Department distribution
        departments = {}
        for student in students:
            dept = student['department']
            if dept not in departments:
                departments[dept] = {"count": 0, "average": 0}
            departments[dept]["count"] += 1
        
        # Calculate department averages
        for student in students:
            dept = student['department']
            departments[dept]["average"] += student['average']
        
        for dept in departments:
            departments[dept]["average"] = round(
                departments[dept]["average"] / departments[dept]["count"], 2
            )
        
        stats = {
            "total_students": total_students,
            "overall_average": round(overall_avg, 2),
            "subject_averages": subject_avgs,
            "grade_distribution": grades,
            "department_distribution": departments,
            "class_averages": {
                class_name: class_data["average"]
                for class_name, class_data in departments.items()
            }
        }
        
        return success_response("Statistics retrieved", stats)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==================== API ROUTES - POST ====================

@app.route('/api/students', methods=['POST'])
def add_student():
    """Add new student"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['id', 'name', 'age', 'department', 'marks']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        # Validate marks is a dictionary with all subjects
        if not isinstance(data['marks'], dict):
            return error_response("Marks must be a dictionary", 400)
        
        required_subjects = ["English", "Tamil", "Maths", "Science", "Social"]
        for subject in required_subjects:
            if subject not in data['marks']:
                return error_response(f"Missing marks for {subject}", 400)
        
        # Add student
        success, message = manager.add_student_app(
            student_id=data['id'],
            name=data['name'],
            age=data['age'],
            department=data['department'],
            marks_dict=data['marks']
        )
        
        if success:
            return success_response(message, None, 201)
        else:
            return error_response(message, 400)
            
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==================== API ROUTES - PUT ====================

@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update student details"""
    try:
        data = request.get_json()
        
        # Get current student
        student = manager.get_student_details(student_id)
        if not student:
            return error_response(f"Student with ID {student_id} not found", 404)
        
        # Update student
        kwargs = {}
        
        if 'name' in data:
            kwargs['name'] = data['name']
        
        if 'age' in data:
            kwargs['age'] = data['age']
        
        if 'department' in data:
            kwargs['department'] = data['department']
        
        if 'marks' in data:
            if not isinstance(data['marks'], dict):
                return error_response("Marks must be a dictionary", 400)
            kwargs['marks'] = data['marks']
        
        success, message = manager.update_student_app(student_id, **kwargs)
        
        if success:
            updated_student = manager.get_student_details(student_id)
            return success_response(message, updated_student)
        else:
            return error_response(message, 400)
            
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==================== API ROUTES - DELETE ====================

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete student"""
    try:
        success, message = manager.delete_student_app(student_id)
        
        if success:
            return success_response(message)
        else:
            return error_response(message, 404)
            
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return error_response("Page not found", 404)

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return error_response("Internal server error", 500)

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("STUDENT RECORD MANAGER - FLASK SERVER")
    print("="*70)
    print("\n✓ Server starting...")
    print("\n🌐 Web Interface: http://localhost:5000")
    print("📡 API Base URL: http://localhost:5000/api")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
