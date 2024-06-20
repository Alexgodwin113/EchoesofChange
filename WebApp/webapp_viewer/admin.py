

from django.contrib import admin
from .models import UserProfile, Organization, Opportunity, Interest, Skill, Review

admin.site.register(UserProfile)
admin.site.register(Organization)
admin.site.register(Opportunity)
admin.site.register(Interest)
admin.site.register(Skill)
admin.site.register(Review)
