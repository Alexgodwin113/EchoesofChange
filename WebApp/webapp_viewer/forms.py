from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Organization, UserProfile, Interest, Skill
from django import forms
from .models import Review
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Review

class UserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(help_text="Required. Format: YYYY-MM-DD")
    location = forms.CharField(max_length=100, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'date_of_birth', 'location', 'bio', 'phone_number', 'interests', 'skills')

    def save(self, commit=True):
        user = super(UserSignupForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            self.save_m2m()  

            user_profile = UserProfile.objects.create(
                user=user,
                bio=self.cleaned_data['bio'],
                location=self.cleaned_data['location'],     
                date_of_birth=self.cleaned_data['date_of_birth'],
                phone_number=self.cleaned_data['phone_number']
            )

            user_profile.interests.set(self.cleaned_data['interests'])
            user_profile.skills.set(self.cleaned_data['skills'])
            user_profile.save()

        return user



class OrganizationSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    location = forms.CharField(max_length=100)
    causes = forms.CharField(max_length=100)
    website = forms.URLField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'name', 'description', 'location', 'causes', 'website')

    def save(self, commit=True):
        user = super(OrganizationSignupForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Organization.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                description=self.cleaned_data['description'],
                location=self.cleaned_data['location'],
                causes=self.cleaned_data['causes'],
                website=self.cleaned_data['website']
            )
        return user



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    rating = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    
from django.forms import EmailInput, TextInput

class UserProfileForm(UserSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password1', None)
        self.fields.pop('password2', None)
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['email'].widget = EmailInput(attrs={'readonly': 'readonly'})
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['username'].widget = TextInput(attrs={'readonly': 'readonly'})

        # Initialize form fields with UserProfile data
        try:
            user_profile = kwargs['instance'].userprofile
            self.fields['bio'].initial = user_profile.bio
            self.fields['location'].initial = user_profile.location
            self.fields['date_of_birth'].initial = user_profile.date_of_birth
            self.fields['phone_number'].initial = user_profile.phone_number
            self.fields['interests'].initial = user_profile.interests.all()
            self.fields['skills'].initial = user_profile.skills.all()
        except UserProfile.DoesNotExist:
            pass

    def clean_username(self):
        return self.instance.username

    def save(self, commit=True):
        user = self.instance
        if commit:
            user.save()

            user_profile = self.instance.userprofile
            user_profile.bio = self.cleaned_data['bio']
            user_profile.location = self.cleaned_data['location']
            user_profile.date_of_birth = self.cleaned_data['date_of_birth']
            user_profile.phone_number = self.cleaned_data['phone_number']
            user_profile.interests.set(self.cleaned_data['interests'])
            user_profile.skills.set(self.cleaned_data['skills'])
            user_profile.save()

        return user_profile