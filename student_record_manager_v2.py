import json
import os
from typing import List, Dict, Optional, Tuple

STUDENT_FILE = "students.json"
SUBJECTS = ["English", "Tamil", "Maths", "Science", "Social"]
CLASS_OPTIONS = {f"CLASS {grade}" for grade in range(6, 13)}


class StudentRecordManager:
    """Student Record Management with MANUAL ID creation and SUBJECT-WISE MARKS"""

    def __init__(self):
        self.students: List[Dict] = []
        self.load_students()

    # ==================== DATA LOADING & SAVING ====================
    
    def load_students(self) -> None:
        """Load students from JSON file"""
        if os.path.exists(STUDENT_FILE):
            try:
                with open(STUDENT_FILE, 'r') as file:
                    self.students = json.load(file)
                print(f"✓ Loaded {len(self.students)} student records")
            except (json.JSONDecodeError, IOError) as e:
                print(f"✗ Error loading file: {e}")
                self.students = []
        else:
            print(f"✓ Starting with fresh records")
            self.students = []

    def save_students(self) -> None:
        """Save students to JSON file"""
        try:
            with open(STUDENT_FILE, 'w') as file:
                json.dump(self.students, file, indent=4)
            print("✓ Records saved successfully!")
            return True
        except IOError as e:
            print(f"✗ Error saving file: {e}")
            return False

    # ==================== UTILITY METHODS ====================

    def is_id_exists(self, student_id: int) -> bool:
        """Check if ID already exists"""
        return any(student['id'] == student_id for student in self.students)

    def _find_student_by_id(self, student_id: int) -> Optional[Dict]:
        """Find student by ID"""
        for student in self.students:
            if student['id'] == student_id:
                return student
        return None

    def _calculate_average_marks(self, marks_dict: Dict) -> float:
        """Calculate average marks from subject marks"""
        if not marks_dict:
            return 0
        return sum(marks_dict.values()) / len(marks_dict)

    def _get_grade(self, average: float) -> str:
        """Get grade based on average marks"""
        if average >= 90:
            return "O"
        elif average >= 80:
            return "A"
        elif average >= 70:
            return "B"
        elif average >= 60:
            return "C"
        elif average >= 50:
            return "D"
        else:
            return "F"

    def _normalize_class(self, class_name: str) -> str:
        """Normalize class values while allowing a custom Other value."""
        value = class_name.strip()
        if not value:
            return ""

        normalized = value.upper()
        if normalized.startswith("CLASS "):
            suffix = normalized[6:].strip()
            if suffix.isdigit() and 6 <= int(suffix) <= 12:
                return f"CLASS {int(suffix)}"
        return value

    # ==================== APPLICATION METHODS (Non-CLI) ====================

    def add_student_app(self, student_id: int, name: str, age: int, 
                        department: str, marks_dict: Dict[str, float]) -> Tuple[bool, str]:
        """
        Add student via application method (not CLI)
        Returns: (success: bool, message: str)
        """
        # Validate ID
        if student_id <= 0:
            return False, "ID must be a positive number!"
        
        if self.is_id_exists(student_id):
            return False, f"ID {student_id} already exists!"

        # Validate name
        if not name or not name.strip():
            return False, "Name cannot be empty!"

        # Validate age
        if age < 5 or age > 100:
            return False, "Age must be between 5 and 100!"

        # Validate department
        if not department or not department.strip():
            return False, "Department cannot be empty!"

        # Validate marks
        for subject, mark in marks_dict.items():
            if not (0 <= mark <= 100):
                return False, f"Marks for {subject} must be between 0 and 100!"

        # Create student record
        new_student = {
            "id": student_id,
            "name": name.strip(),
            "age": age,
            "department": self._normalize_class(department),
            "marks": marks_dict,
            "average": self._calculate_average_marks(marks_dict),
            "grade": self._get_grade(self._calculate_average_marks(marks_dict))
        }

        self.students.append(new_student)
        self.save_students()
        return True, f"Student {name} added successfully!"

    def get_student_details(self, student_id: int) -> Optional[Dict]:
        """
        Get student details as dictionary (application method)
        """
        student = self._find_student_by_id(student_id)
        if student:
            return student.copy()
        return None

    def get_all_students(self) -> List[Dict]:
        """
        Get all students as list of dictionaries (application method)
        """
        return [student.copy() for student in self.students]

    def update_student_app(self, student_id: int, **kwargs) -> Tuple[bool, str]:
        """
        Update student via application method
        Accepted kwargs: name, age, department, marks (dict)
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return False, f"No student found with ID {student_id}"

        # Update fields
        if 'name' in kwargs and kwargs['name']:
            student['name'] = kwargs['name'].strip()

        if 'age' in kwargs:
            if 5 <= kwargs['age'] <= 100:
                student['age'] = kwargs['age']
            else:
                return False, "Age must be between 5 and 100!"

        if 'department' in kwargs and kwargs['department']:
            student['department'] = self._normalize_class(kwargs['department'])

        if 'marks' in kwargs:
            marks = kwargs['marks']
            for subject, mark in marks.items():
                if not (0 <= mark <= 100):
                    return False, f"Marks for {subject} must be between 0 and 100!"
            student['marks'] = marks
            student['average'] = self._calculate_average_marks(marks)
            student['grade'] = self._get_grade(student['average'])

        self.save_students()
        return True, "Student updated successfully!"

    def delete_student_app(self, student_id: int) -> Tuple[bool, str]:
        """
        Delete student via application method
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return False, f"No student found with ID {student_id}"

        self.students.remove(student)
        self.save_students()
        return True, f"Student {student['name']} deleted successfully!"

    def get_students_by_department(self, department: str) -> List[Dict]:
        """Get all students from a specific class or custom class value"""
        class_name = department.strip().casefold()
        return [
            s.copy() for s in self.students
            if s['department'].strip().casefold() == class_name
        ]

    def get_top_performers(self, limit: int = 5) -> List[Dict]:
        """Get top performing students"""
        return sorted(self.students, key=lambda x: x['average'], reverse=True)[:limit]

    # ==================== CLI METHODS ====================

    def add_student(self) -> None:
        """Add new student via CLI"""
        print("\n" + "=" * 70)
        print("ADD NEW STUDENT (MANUAL ID)")
        print("=" * 70)

        try:
            # Get ID from user
            while True:
                student_id = int(input("Enter student ID: "))
                
                if student_id <= 0:
                    print("✗ ID must be a positive number!")
                    continue
                
                if self.is_id_exists(student_id):
                    print(f"✗ ID {student_id} already exists!")
                    continue
                
                break

            # Get other details
            name = input("Enter student name: ").strip()
            if not name:
                print("✗ Name cannot be empty!")
                return

            age = int(input("Enter student age: "))
            if age < 5 or age > 100:
                print("✗ Age must be between 5 and 100!")
                return

            department = input("Enter class (6-12 or Other): ").strip()
            if not department:
                print("✗ Class cannot be empty!")
                return

            # Get marks for each subject
            print(f"\nEnter marks for each subject (0-100):")
            marks_dict = {}
            for subject in SUBJECTS:
                while True:
                    try:
                        mark = float(input(f"  {subject}: "))
                        if 0 <= mark <= 100:
                            marks_dict[subject] = mark
                            break
                        else:
                            print(f"  ✗ {subject} marks must be between 0 and 100!")
                    except ValueError:
                        print(f"  ✗ Invalid input for {subject}!")

            # Add student
            success, message = self.add_student_app(student_id, name, age, department, marks_dict)
            
            if success:
                print(f"\n✓ {message}")
                print(f"  Student ID: {student_id}")
                print(f"  Name: {name}")
                avg = self._calculate_average_marks(marks_dict)
                print(f"  Average Marks: {avg:.2f}")
            else:
                print(f"\n✗ {message}")

        except ValueError as e:
            print(f"✗ Invalid input: {e}")

    def view_all_students(self) -> None:
        """Display all students"""
        print("\n" + "=" * 110)
        print("ALL STUDENT RECORDS")
        print("=" * 110)

        if not self.students:
            print("✗ No students found in the records.")
            return

        print(f"{'ID':<8} {'Name':<20} {'Age':<5} {'Dept':<8} {'Eng':<6} {'Tam':<6} {'Mat':<6} {'Sci':<6} {'Soc':<6} {'Avg':<7} {'Grade':<7}")
        print("-" * 110)

        for student in self.students:
            marks = student['marks']
            print(
                f"{student['id']:<8} "
                f"{student['name']:<20} "
                f"{student['age']:<5} "
                f"{student['department']:<8} "
                f"{marks.get('English', 0):<6.1f} "
                f"{marks.get('Tamil', 0):<6.1f} "
                f"{marks.get('Maths', 0):<6.1f} "
                f"{marks.get('Science', 0):<6.1f} "
                f"{marks.get('Social', 0):<6.1f} "
                f"{student['average']:<7.2f} "
                f"{student['grade']:<7}"
            )

        print("-" * 110)
        print(f"Total students: {len(self.students)}\n")

    def search_student_by_id(self) -> None:
        """Search student by ID"""
        print("\n" + "=" * 70)
        print("SEARCH STUDENT BY ID")
        print("=" * 70)

        try:
            student_id = int(input("Enter student ID to search: "))
            student = self.get_student_details(student_id)

            if student:
                print("\n✓ Student found!")
                print(f"  ID: {student['id']}")
                print(f"  Name: {student['name']}")
                print(f"  Age: {student['age']}")
                print(f"  Department: {student['department']}")
                print(f"\n  Marks by Subject:")
                for subject, mark in student['marks'].items():
                    print(f"    {subject}: {mark:.1f}")
                print(f"\n  Average Marks: {student['average']:.2f}")
                print(f"  Grade: {student['grade']}")
            else:
                print(f"✗ No student found with ID {student_id}")

        except ValueError:
            print("✗ Invalid input: ID must be a number!")

    def update_student_details(self) -> None:
        """Update student details"""
        print("\n" + "=" * 70)
        print("UPDATE STUDENT DETAILS")
        print("=" * 70)

        try:
            student_id = int(input("Enter student ID to update: "))
            student = self.get_student_details(student_id)

            if not student:
                print(f"✗ No student found with ID {student_id}")
                return

            print(f"\n✓ Found student: {student['name']}")
            print("\nWhat would you like to update?")
            print("1. Name")
            print("2. Age")
            print("3. Department")
            print("4. Marks for a specific subject")
            print("5. Update all marks")
            print("6. Update Multiple Fields")

            choice = input("Enter choice (1-6): ").strip()

            if choice == "1":
                new_name = input("Enter new name: ").strip()
                if new_name:
                    success, msg = self.update_student_app(student_id, name=new_name)
                    print(f"✓ {msg}" if success else f"✗ {msg}")
                else:
                    print("✗ Name cannot be empty!")

            elif choice == "2":
                try:
                    new_age = int(input("Enter new age: "))
                    success, msg = self.update_student_app(student_id, age=new_age)
                    print(f"✓ {msg}" if success else f"✗ {msg}")
                except ValueError:
                    print("✗ Invalid age!")

            elif choice == "3":
                new_dept = input("Enter new department: ").strip()
                if new_dept:
                    success, msg = self.update_student_app(student_id, department=new_dept)
                    print(f"✓ {msg}" if success else f"✗ {msg}")
                else:
                    print("✗ Department cannot be empty!")

            elif choice == "4":
                print("\nSelect subject to update:")
                for i, subject in enumerate(SUBJECTS, 1):
                    current = student['marks'].get(subject, 0)
                    print(f"  {i}. {subject} (current: {current:.1f})")
                
                try:
                    sub_choice = int(input("Enter choice (1-5): ")) - 1
                    if 0 <= sub_choice < len(SUBJECTS):
                        subject = SUBJECTS[sub_choice]
                        new_mark = float(input(f"Enter new marks for {subject}: "))
                        updated_marks = student['marks'].copy()
                        updated_marks[subject] = new_mark
                        success, msg = self.update_student_app(student_id, marks=updated_marks)
                        print(f"✓ {msg}" if success else f"✗ {msg}")
                    else:
                        print("✗ Invalid choice!")
                except ValueError:
                    print("✗ Invalid input!")

            elif choice == "5":
                print(f"\nUpdate marks for all subjects (0-100):")
                updated_marks = student['marks'].copy()
                for subject in SUBJECTS:
                    try:
                        new_mark = float(input(f"  {subject} (current: {student['marks'].get(subject, 0):.1f}): "))
                        if 0 <= new_mark <= 100:
                            updated_marks[subject] = new_mark
                        else:
                            print(f"  ✗ {subject} marks must be between 0 and 100!")
                            return
                    except ValueError:
                        print(f"  ✗ Invalid input for {subject}!")
                        return
                
                success, msg = self.update_student_app(student_id, marks=updated_marks)
                print(f"✓ {msg}" if success else f"✗ {msg}")

            elif choice == "6":
                print("\nUpdate the fields you want to change (or press Enter to skip):")
                
                new_name = input(f"Name (current: {student['name']}): ").strip()
                new_age_input = input(f"Age (current: {student['age']}): ").strip()
                new_dept = input(f"Department (current: {student['department']}): ").strip()

                kwargs = {}
                if new_name:
                    kwargs['name'] = new_name
                if new_age_input:
                    try:
                        kwargs['age'] = int(new_age_input)
                    except ValueError:
                        print("✗ Invalid age!")
                        return
                if new_dept:
                    kwargs['department'] = new_dept

                if kwargs:
                    success, msg = self.update_student_app(student_id, **kwargs)
                    print(f"✓ {msg}" if success else f"✗ {msg}")
                else:
                    print("✗ No changes made!")

            else:
                print("✗ Invalid choice!")

        except ValueError:
            print("✗ Invalid input: ID must be a number!")

    def delete_student(self) -> None:
        """Delete student"""
        print("\n" + "=" * 70)
        print("DELETE STUDENT")
        print("=" * 70)

        try:
            student_id = int(input("Enter student ID to delete: "))
            student = self.get_student_details(student_id)

            if not student:
                print(f"✗ No student found with ID {student_id}")
                return

            print(f"\n⚠ You are about to delete:")
            print(f"  ID: {student['id']}")
            print(f"  Name: {student['name']}")
            confirm = input("\nAre you sure? (yes/no): ").strip().lower()

            if confirm == "yes":
                success, msg = self.delete_student_app(student_id)
                print(f"✓ {msg}" if success else f"✗ {msg}")
            else:
                print("✗ Deletion cancelled.")

        except ValueError:
            print("✗ Invalid input: ID must be a number!")

    def view_department_stats(self) -> None:
        """View statistics by department"""
        print("\n" + "=" * 70)
        print("DEPARTMENT STATISTICS")
        print("=" * 70)

        if not self.students:
            print("✗ No students found!")
            return

        departments = set(s['department'] for s in self.students)
        
        for dept in sorted(departments):
            students = self.get_students_by_department(dept)
            avg_marks = sum(s['average'] for s in students) / len(students)
            print(f"\n{dept}:")
            print(f"  Total Students: {len(students)}")
            print(f"  Average Marks: {avg_marks:.2f}")

    def view_top_performers(self) -> None:
        """View top performing students"""
        print("\n" + "=" * 70)
        print("TOP PERFORMERS")
        print("=" * 70)

        top_students = self.get_top_performers(5)
        
        if not top_students:
            print("✗ No students found!")
            return

        for i, student in enumerate(top_students, 1):
            print(f"\n{i}. {student['name']}")
            print(f"   ID: {student['id']}")
            print(f"   Average: {student['average']:.2f}")
            print(f"   Grade: {student['grade']}")

    def display_menu(self) -> None:
        """Display main menu"""
        print("\n" + "=" * 70)
        print("STUDENT RECORD MANAGEMENT SYSTEM")
        print("(MANUAL ID + SUBJECT-WISE MARKS)")
        print("=" * 70)
        print("1. Add a student")
        print("2. View all students")
        print("3. Search for a student by ID")
        print("4. Update student details")
        print("5. Delete a student")
        print("6. View top performers")
        print("7. View department statistics")
        print("8. Exit")
        print("=" * 70)

    def run(self) -> None:
        """Run the CLI application"""
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-8): ").strip()

            if choice == "1":
                self.add_student()
            elif choice == "2":
                self.view_all_students()
            elif choice == "3":
                self.search_student_by_id()
            elif choice == "4":
                self.update_student_details()
            elif choice == "5":
                self.delete_student()
            elif choice == "6":
                self.view_top_performers()
            elif choice == "7":
                self.view_department_stats()
            elif choice == "8":
                print("\n✓ Thank you for using Student Record Manager!")
                print("Exiting...")
                break
            else:
                print("✗ Invalid choice! Please enter a number between 1 and 8.")


if __name__ == "__main__":
    manager = StudentRecordManager()
    manager.run()
