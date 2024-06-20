import json
from django.contrib.auth.models import User
from webapp_viewer.models import UserProfile, Organization, Opportunity, Interest, Skill, Review, Disability
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from pathlib import Path

ROOT_DIR = Path('webapp_viewer') / 'management' / 'commands'

class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        with open(ROOT_DIR / 'sample_data.json') as f:
            data = json.load(f)
            
        Review.objects.all().delete()
        Opportunity.objects.all().delete()
        Organization.objects.all().delete()
        UserProfile.objects.all().delete()
        Interest.objects.all().delete()
        Skill.objects.all().delete()
        Disability.objects.all().delete()
        User.objects.all().delete()

        # Create interests
        interests = []
        for interest_data in data['Interest']:
            interest, created = Interest.objects.get_or_create(name=interest_data['name'])
            interests.append(interest)

        # Create skills
        skills = []
        for skill_data in data['Skill']:
            skill, created = Skill.objects.get_or_create(name=skill_data['name'])
            skills.append(skill)

        # Create disabilities
        disabilities = []
        for disability_data in data['Disability']:
            disability, created = Disability.objects.get_or_create(name=disability_data['name'])
            disabilities.append(disability)

        # Create users and user profiles
        for user_data in data['UserProfile']:
            # Create user
            user = User.objects.create(username=f"user{user_data['user']}")
            user.set_password('password')
            user.save()

            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                bio=user_data['bio'],
                location=user_data['location'],
                date_of_birth=user_data['date_of_birth'],
                phone_number=user_data['phone_number'],
                hours=user_data['hours']
            )

            # Add profile image
            profile_image_path = user_data['image']
            with open(profile_image_path, 'rb') as image_file:
                profile.image.save(slugify(user.username) + '.jpg', File(image_file))

            # Add interests, skills, and disabilities
            interest_ids = user_data['interests']
            profile.interests.set([interests[interest_id - 1] for interest_id in interest_ids])

            skill_ids = user_data['skills']
            profile.skills.set([skills[skill_id - 1] for skill_id in skill_ids])

            disability_ids = user_data['disabilities']
            profile.disabilities.set([disabilities[disability_id - 1] for disability_id in disability_ids])

        # Create organizations
        for org_data in data['Organization']:
            user = User.objects.create(username=f"org{org_data['user']}")
            user.set_password('password')
            user.save()

            org = Organization.objects.create(
                user=user,
                name=org_data['name'],
                description=org_data['description'],    
                location=org_data['location'],
                causes=org_data['causes'],
                awards=org_data.get('awards', ''),
                website=org_data.get('website', ''),
                email=org_data.get('email', '')
            )

            # Add organization image
            org_image_path = org_data['image']
            with open(org_image_path, 'rb') as image_file:
                org.image.save(slugify(org.name) + '.jpg', File(image_file))

        # Create opportunities
        for opp_data in data['Opportunity']:
            org = Organization.objects.get(user__username=f"org{opp_data['organization']}")
            opportunity = Opportunity.objects.create(
                organization=org,
                title=opp_data['title'],
                description=opp_data['description'],
                category=opp_data['category'],
                impact_score=opp_data['impact_score'],
                start_date=opp_data['start_date'],
                end_date=opp_data['end_date'],
                total_hours=opp_data['total_hours'],
                location=opp_data['location'],
                images=opp_data['images']
            )

            # Add required skills
            for skill_id in opp_data['required_skills']:
                opportunity.required_skills.add(skills[skill_id - 1]) 

            # Add disability accessibility
            for disability_id in opp_data['disability_accessibility']:
                opportunity.disability_inclusive.add(disabilities[disability_id - 1])

        # Create reviews
        for review_data in data['Review']:
            org = Organization.objects.get(user__username=f"org{review_data['organization']}")
            user = UserProfile.objects.get(user__username=f"user{review_data['user']}")
            Review.objects.create(
                organization=org,
                user=user,
                rating=review_data['rating'],
                comment=review_data['comment']
            )

        self.stdout.write(self.style.SUCCESS('Sample data successfully seeded!'))