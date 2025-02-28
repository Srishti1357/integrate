
import os
import django
from datetime import datetime
from random import choice

# ✅ Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Integrate.settings")  # Change 'Integrate' to your actual project name
django.setup()

# ✅ Import models
from collegeApp.models import Student
from adminApp.models import College
from gate.models import Attendance

# ✅ Sample student data
students_data = [
    {"name": "Sophia Reed", "event": "AI Hackathon", "type_of_visitor": "Student", "college_name": "Tech Institute", "datetime": datetime(2025, 2, 17, 11, 45), "approval": 2},
    {"name": "Michael Carter", "event": "Blockchain Summit", "type_of_visitor": "Entrepreneur", "college_name": "Business School", "datetime": datetime(2025, 2, 18, 16, 20), "approval": 1},
    {"name": "Ava Patel", "event": "Art Expo", "type_of_visitor": "Artist", "college_name": "Fine Arts Academy", "datetime": datetime(2025, 2, 15, 9, 30), "approval": 0},
    {"name": "Ethan Parker", "event": "Robotics Championship", "type_of_visitor": "Engineer", "college_name": "Tech University", "datetime": datetime(2025, 2, 20, 14, 10), "approval": 1},
    {"name": "Liam Nguyen", "event": "Entrepreneur Meetup", "type_of_visitor": "Investor", "college_name": "Global Business Hub", "datetime": datetime(2025, 2, 19, 18, 50), "approval": 2},
    {"name": "Zara Malik", "event": "Startup Pitch Fest", "type_of_visitor": "Founder", "college_name": "XYZ Incubator", "datetime": datetime(2025, 2, 22, 10, 15), "approval": 1},
    {"name": "Oscar Bennett", "event": "Tech Workshop", "type_of_visitor": "Developer", "college_name": "Software Academy", "datetime": datetime(2025, 2, 13, 13, 40), "approval": 0},
    {"name": "Isabella Ross", "event": "Medical Innovation Forum", "type_of_visitor": "Doctor", "college_name": "Health Research Institute", "datetime": datetime(2025, 2, 25, 12, 30), "approval": 2},
    {"name": "Noah Adams", "event": "Cybersecurity Conference", "type_of_visitor": "Ethical Hacker", "college_name": "Security Academy", "datetime": datetime(2025, 2, 21, 9, 0), "approval": 1},
    {"name": "Emily Foster", "event": "Film Festival", "type_of_visitor": "Filmmaker", "college_name": "Cinema School", "datetime": datetime(2025, 2, 16, 11, 55), "approval": 0},
]

def generate_roll_number(index):
    """Generate a unique roll number for each student."""
    return f"STU{1000 + index}"

def populate_db():
    try:
        new_entries = []
        existing_entries = []

        # ✅ Process each student entry
        for index, student_data in enumerate(students_data):
            roll_no = generate_roll_number(index)

            # 🔹 Get or create the college
            college, _ = College.objects.get_or_create(college_name=student_data['college_name'])

            # 🔹 Create or update the student
            student, created = Student.objects.update_or_create(
                roll_no=roll_no,  # ✅ Unique Roll Number
                defaults={
                    "name": student_data['name'],
                    "event": student_data['event'],
                    "type_of_visitor": student_data['type_of_visitor'],
                    "college": college,  # ✅ Correct ForeignKey reference
                    "datetime": student_data['datetime'],
                    "approval": student_data['approval'],
                }
            )

            # 🔹 Get or create an attendance record (Prevent duplication)
            attendance_status = choice(["Present", "Absent", "Pending"])
            attendance, _ = Attendance.objects.get_or_create(user=student, defaults={"status": attendance_status})

            # 🔹 Update student with attendance
            student.attendence = attendance
            student.save()

            if created:
                new_entries.append(student)
                print(f"✅ New Student '{student.name}' ({student.roll_no}) added with {attendance.status} attendance.")
            else:
                existing_entries.append(student)
                print(f"🔄 Existing Student '{student.name}' ({student.roll_no}) updated.")

        # ✅ Sorting: New entries first, then old ones
        all_students = sorted(new_entries + existing_entries, key=lambda v: v.datetime, reverse=True)

        # ✅ Display sorted results
        print("\n🔹 Final Sorted List (Newest at Top):")
        for student in all_students:
            print(f"📌 {student.name} ({student.roll_no}) - {student.event} - {student.datetime} - {student.attendence.status}")

    except Exception as e:
        print(f"❌ Error while adding students: {e}")

# ✅ Run the function
if __name__ == "__main__":
    populate_db()
