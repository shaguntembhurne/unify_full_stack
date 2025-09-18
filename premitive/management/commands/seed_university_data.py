from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from premitive.models import UserProfile
from news.models import NewsPost
from projects.models import Project


USERS = [
    ("Aarav Sharma", "aarav@unify.test"),
    ("Ishita Patel", "ishita@unify.test"),
    ("Rohan Gupta", "rohan@unify.test"),
    ("Neha Verma", "neha@unify.test"),
    ("Vikram Singh", "vikram@unify.test"),
]

NEWS_DATA = [
    ("Research", "AI Lab Publishes Breakthrough Paper", "The Computer Science AI Lab has published a breakthrough on efficient transformer training reducing compute by 40%."),
    ("Events", "Tech Symposium Announced for October", "The annual Tech Symposium will feature alumni founders and industry leaders. Registrations open next week."),
    ("Academics", "Spring Enrollment Window Opens", "Students can now enroll for Spring semester courses via the portal until Oct 5."),
    ("Sports", "Football Team Advances to Finals", "Our university football team has advanced to the state finals after a stunning semi-final win."),
    ("Research", "Robotics Club Wins National Challenge", "Team Vimana from the Robotics Club won the National Autonomous Drone Challenge."),
    ("Events", "Cultural Fest ‘Sanskriti’ Line-up Revealed", "Music, dance, and theatre clubs will perform at the central amphitheater on 28-29 Sept."),
    ("Academics", "Library Adds 5,000 New E-Resources", "The central library now offers 5,000 new ebooks and journals with off-campus access."),
    ("Sports", "Inter-College Athletics Meet Hosted", "The campus hosted an inter-college meet with 300+ athletes participating across 12 events."),
    ("Research", "BioTech Lab Receives DST Grant", "Biotechnology department secures a DST grant for cancer biomarker research over 3 years."),
    ("Events", "Career Fair with 60+ Companies", "Placement Cell announces a career fair bringing 60+ companies across tech, consulting, and core sectors."),
]

PROJECTS_DATA = [
    ("Smart Campus Energy Monitor", "Build IoT-based energy monitoring across hostels and labs to reduce wastage.", "IoT, Python, MQTT"),
    ("Open-Source Notes Platform", "A collaborative markdown-based notes platform for courses with tagging and search.", "Django, PostgreSQL, Tailwind"),
    ("Sports Analytics Dashboard", "Analyze team performance with match stats and predictive modeling.", "Pandas, scikit-learn, D3.js"),
    ("Mental Health Support Bot", "Anonymous chatbot that shares campus resources and coping strategies.", "NLP, Rasa, UX"),
    ("Clean Water Quality Sensor", "Low-cost turbidity and pH sensor suite for nearby villages.", "Embedded C, Sensors, PCB"),
    ("Campus Navigation App", "Indoor navigation for new students across academic blocks using BLE beacons.", "Flutter, BLE, Maps"),
    ("Accessibility Audit Toolkit", "Audit departmental sites and provide accessibility remediation guides.", "WCAG, Lighthouse, React"),
    ("Green Lab Certification", "Framework to certify labs for sustainable practices and resource usage.", "Policy, Data, Reporting"),
    ("Course Planner Optimizer", "Helps students build conflict-free timetables from course offerings.", "Python, OR-Tools, UI"),
    ("Virtual Lab Simulations", "Simulate basic physics labs for remote learning scenarios.", "Unity, Physics, Education"),
]


class Command(BaseCommand):
    help = "Delete all news and projects; create 5 users and seed 10 news + 10 projects"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Deleting existing News and Projects..."))
        NewsPost.objects.all().delete()
        Project.objects.all().delete()

        self.stdout.write(self.style.WARNING("Creating users..."))
        created_users = []
        for name, email in USERS:
            first = name.split()[0]
            user, _ = User.objects.get_or_create(username=email, defaults={
                'email': email,
                'first_name': first,
            })
            if not user.has_usable_password():
                user.set_password('pass1234')
                user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'student'})
            created_users.append(user)

        self.stdout.write(self.style.WARNING("Seeding News posts..."))
        for i, (cat, title, content) in enumerate(NEWS_DATA):
            author = created_users[i % len(created_users)]
            NewsPost.objects.create(
                title=title,
                category=cat.lower(),
                content=content,
                image_url='',
                author=author,
            )

        self.stdout.write(self.style.WARNING("Seeding Projects..."))
        for i, (title, desc, skills) in enumerate(PROJECTS_DATA):
            author = created_users[(i + 2) % len(created_users)]
            Project.objects.create(
                title=title,
                description=desc,
                skills=skills,
                status='recruiting',
                author=author,
            )

        self.stdout.write(self.style.SUCCESS("Seeded 5 users, 10 news posts, and 10 projects."))