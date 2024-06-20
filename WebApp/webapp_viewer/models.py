from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.shortcuts import redirect, reverse
from django.db.models import Sum


class UserProfile(models.Model):
    def __str__(self):
        return self.user.username

    # Each user profile is linked to a user (OneToOne relationship)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(upload_to='profile_pics', default='default.jpg')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    interests = models.ManyToManyField('Interest', blank=True)  # Interests of the user (Many-to-many relationship with Interest model)
    skills = models.ManyToManyField('Skill', blank=True)  # Skills of the user (Many-to-many relationship with Skill model)
    disabilities = models.ManyToManyField('Disability', blank=True)  # Many-to-Many relationship with Disability model
    hours = models.IntegerField(default=0)

    def submit_volunteer_hours(self, opportunity, hours):
        organization = opportunity.organization
        volunteer_hour = VolunteerHour.objects.create(
            user=self,
            organization=organization,
            opportunity=opportunity,
            hours=hours
        )
        return redirect(reverse('timesheet_detail', args=[volunteer_hour.id]))


class Organization(models.Model):
    def __str__(self):
        if isinstance(self.user, User):
            return self.user.username
        else:
            return f"Organization {self.pk}"  # Return a default string if user is not a User instance

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    causes = models.CharField(max_length=100)
    image = models.ImageField(upload_to='organization_images/')
    awards = models.TextField(blank=True)
    website = models.URLField(max_length=200, blank=True)
    email = models.EmailField(max_length=254, blank=True)



class Opportunity(models.Model):
    # Organization offering the opportunity (ForeignKey relationship)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=100)
    impact_score = models.IntegerField(validators=[MinValueValidator(0)])
    # Skills required for the opportunity (Many-to-many relationship with Skill model)
    required_skills = models.ManyToManyField('Skill')
    start_date = models.DateField()
    end_date = models.DateField()
    total_hours = models.IntegerField(validators=[MinValueValidator(0)])
    # need to add location
    # need to add created time
    images = models.ImageField(upload_to='opportunity_images/')  # Define the path where images will be uploaded
    # Add location field
    location = models.CharField(max_length=100)
    # Add created time field
    created_time = models.DateTimeField(default=timezone.now)
    disability_inclusive = models.ManyToManyField('Disability')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.title


class Interest(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name  # This ensures the name of the interest is displayed


class Skill(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name  # This ensures the name of the skill is displayed


class Review(models.Model):
    # Organization being reviewed (ForeignKey relationship)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    # User submitting the review (ForeignKey relationship with UserProfile)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()


class Order(models.Model):
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Disability(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


from django.db import models
from django.db.models import Sum
from .models import UserProfile, Organization, Opportunity

class VolunteerHour(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    hours = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='waiting')
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user.username} - {self.opportunity.title} - {self.hours} hours"

    @property
    def impact_score(self):
        return (self.hours // 10) * 100  # Assuming 10 hours = 100 impact score

    @classmethod
    def category_impact_scores_by_user_category_lboard(cls, category):
        if category == "All":
            # Get the total impact score for each user across all categories
            all_category_hours = cls.objects.values('user').annotate(total_hours=Sum('hours'))
            users_impact_scores = {}  # Initialize the dictionary here
            for all_category_hour in all_category_hours:
                user_profile = UserProfile.objects.get(pk=all_category_hour['user'])
                impact_score = all_category_hour['total_hours'] * 10  # Assuming each hour contributes 10 to the impact score
                users_impact_scores[user_profile] = impact_score

            # Find the maximum impact score
            max_impact_score = max(users_impact_scores.values())

            # Filter users with the maximum impact score
            users_with_max_impact = {user: score for user, score in users_impact_scores.items() if score == max_impact_score}
            
            return users_with_max_impact
        else:
            users_impact_scores = {}
            # Assuming the category is stored in the 'category' field of Opportunity model
            # You may need to adjust this query based on your actual model structure
            category_hours = cls.objects.filter(opportunity__category=category).values('user').annotate(total_hours=Sum('hours'))
            for category_hour in category_hours:
                user_profile = UserProfile.objects.get(pk=category_hour['user'])
                impact_score = category_hour['total_hours'] * 10  # Assuming each hour contributes 10 to the impact score
                users_impact_scores[user_profile] = impact_score
            return users_impact_scores

    @classmethod
    def category_impact_scores_by_user_category(cls, user_profile):
        category_impact_scores = {}

        # Get the total impact score for the logged-in user across all categories
        all_category_hours = cls.objects.filter(user=user_profile).values('opportunity__category').annotate(total_hours=Sum('hours'))

        for category_hour in all_category_hours:
            category = category_hour['opportunity__category']
            impact_score = category_hour['total_hours'] * 10  # Assuming each hour contributes 10 to the impact score
            if category in category_impact_scores:
                category_impact_scores[category] += impact_score
            else:
                category_impact_scores[category] = impact_score

        return category_impact_scores






class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(blank=True, null=True, max_length=225)
    status = models.CharField(blank=True, null=True, max_length=225)
