import os
import django
from datetime import datetime

# ✅ Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Integrate.settings")  # Change 'Integrate' to your actual project name
django.setup()

# ✅ Import models
from collegeApp.models import Visitor
from adminApp.models import College

# ✅ Sample visitor data
visitors_data = [
    {"name": "Sophia Reed", "event": "AI Hackathon", "visitor_type": "Student", "college_name": "Tech Institute", "datetime": datetime(2025, 2, 17, 11, 45), "approval": 2},
    {"name": "Michael Carter", "event": "Blockchain Summit", "visitor_type": "Entrepreneur", "college_name": "Business School", "datetime": datetime(2025, 2, 18, 16, 20), "approval": 1},
    {"name": "Ava Patel", "event": "Art Expo", "visitor_type": "Artist", "college_name": "Fine Arts Academy", "datetime": datetime(2025, 2, 15, 9, 30), "approval": 0},
    {"name": "Ethan Parker", "event": "Robotics Championship", "visitor_type": "Engineer", "college_name": "Tech University", "datetime": datetime(2025, 2, 20, 14, 10), "approval": 1},
    {"name": "Liam Nguyen", "event": "Entrepreneur Meetup", "visitor_type": "Investor", "college_name": "Global Business Hub", "datetime": datetime(2025, 2, 19, 18, 50), "approval": 2},
    {"name": "Zara Malik", "event": "Startup Pitch Fest", "visitor_type": "Founder", "college_name": "XYZ Incubator", "datetime": datetime(2025, 2, 22, 10, 15), "approval": 1},
    {"name": "Oscar Bennett", "event": "Tech Workshop", "visitor_type": "Developer", "college_name": "Software Academy", "datetime": datetime(2025, 2, 13, 13, 40), "approval": 0},
    {"name": "Isabella Ross", "event": "Medical Innovation Forum", "visitor_type": "Doctor", "college_name": "Health Research Institute", "datetime": datetime(2025, 2, 25, 12, 30), "approval": 2},
    {"name": "Noah Adams", "event": "Cybersecurity Conference", "visitor_type": "Ethical Hacker", "college_name": "Security Academy", "datetime": datetime(2025, 2, 21, 9, 0), "approval": 1},
    {"name": "Emily Foster", "event": "Film Festival", "visitor_type": "Filmmaker", "college_name": "Cinema School", "datetime": datetime(2025, 2, 16, 11, 55), "approval": 0},
]

def populate_db():
    try:
        new_entries = []
        existing_entries = []

        # ✅ Process each visitor entry
        for visitor_data in visitors_data:
            # 🔹 Get or create the college
            college, _ = College.objects.get_or_create(college_name=visitor_data['college_name'])

            # 🔹 Create or update the visitor
            visitor, created = Visitor.objects.update_or_create(
                name=visitor_data['name'],
                event=visitor_data['event'],
                visitor_type=visitor_data['visitor_type'],
                college_name=college,  # ✅ Correct ForeignKey reference
                defaults={"datetime": visitor_data['datetime'], "approval": visitor_data['approval']}
            )

            if created:
                new_entries.append(visitor)
                print(f"✅ New Visitor '{visitor.name}' added.")
            else:
                existing_entries.append(visitor)
                print(f"🔄 Existing Visitor '{visitor.name}' updated.")

        # ✅ Sorting: New entries first, then old ones
        all_visitors = sorted(new_entries + existing_entries, key=lambda v: v.datetime, reverse=True)

        # ✅ Display sorted results
        print("\n🔹 Final Sorted List (Newest at Top):")
        for visitor in all_visitors:
            print(f"📌 {visitor.name} - {visitor.event} - {visitor.datetime}")

    except Exception as e:
        print(f"❌ Error while adding visitor: {e}")

# ✅ Run the function
if __name__ == "__main__":
    populate_db()
