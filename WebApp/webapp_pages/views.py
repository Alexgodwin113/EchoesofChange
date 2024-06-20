from django.urls import path
from . import views
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from webapp_viewer.forms import UserSignupForm
from webapp_viewer.models import UserProfile, Interest, Skill

from django.shortcuts import render
from django.views.generic import ListView, DetailView

from django.shortcuts import (get_object_or_404, render, redirect) 

def home(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'userprofile'):
            return HttpResponse(render(request, 'home.html')) 
        elif hasattr(request.user, 'organization'):
            return HttpResponse(render(request, 'home.html'))
        else:
            form = UserSignupForm()
            form.initial['user'] = request.user

            form.initial['username'] = request.user.username
            form.fields['username'].disabled = True 

            form.initial['email'] = request.user.email
            form.fields['email'].disabled = True 

            field1 = form.fields['password1']
            field1.widget = field1.hidden_widget()

            field2 = form.fields['password2']
            field2.widget = field2.hidden_widget()

            if request.method == 'POST':
                form = UserSignupForm(request.POST) 
                profile = UserProfile.objects.create(
                    user=request.user,
                    image='profile_pics/default.jpg',   
                    bio= form.data['bio'],
                    location= form.data['location'],
                    date_of_birth= form.data['date_of_birth'],   
                    phone_number= form.data['phone_number']
                )
                profile.interests.set(Interest.objects.filter(name__in=request.POST.getlist('interests')))
                profile.skills.set(Skill.objects.filter(name__in=request.POST.getlist('skills')))
                profile.save()
                return HttpResponse(render(request, 'home.html'))
            else:
                return render(request, 'registration/user_details_add.html', {'form': form}) 
    else:
        return HttpResponse(render(request, 'home.html'))



def about(request): 
    return render(request, "about.html")