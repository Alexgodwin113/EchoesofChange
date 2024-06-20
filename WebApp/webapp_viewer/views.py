from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView, View
from .models import Organization, Opportunity, VolunteerHour, UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from pusher import Pusher
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django import forms
from django.conf import settings
import os
import json
from django.db.models import Q
from .forms import UserSignupForm, OrganizationSignupForm
from .models import Conversation  
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ai_utils import generate_response
from django.shortcuts import render
from .models import UserProfile, VolunteerHour
from django.db.models import Sum
from django.shortcuts import render, redirect
from .models import Organization, Review
from .forms import ReviewForm, UserProfileForm


#----------------------------------------------organization views----------------------------------------------

def organization_list(request): 
    context ={}
    context["org_list"] = Organization.objects.all()
    return render(request, "organization_list_view.html", context)

def organization_details(request, pk):
    organization = get_object_or_404(Organization, user_id=pk)
    reviews = Review.objects.filter(organization=organization)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.organization = organization
            review.user = request.user.userprofile
            review.save()
            return redirect('organization_details', pk=pk)
    else:
        form = ReviewForm()

    context = {
        'organization': organization,
        'reviews': reviews,
        'form': form
    }
    return render(request, 'organization_detail_view.html', context)

class OrganizationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Organization
    fields = ['name', 'description', 'location', 'causes', 'image']
    template_name = 'organization_update_view.html'
    success_url = reverse_lazy('organization-list')

    def test_func(self):
        organization = self.get_object()
        return self.request.user == organization.user

    def get_object(self, queryset=None):
        return get_object_or_404(Organization, user=self.request.user)

def organization_count(request):
    count = Organization.objects.count()
    return JsonResponse({'count': count})

def search_organizations(request):
    search_term = request.GET.get('query', '')
    try:
        organization = Organization.objects.get(name__icontains=search_term)
        return JsonResponse({'id': organization.id})
    except Organization.DoesNotExist:
        return JsonResponse({'error' : 'Organization not found'}, status=404)


class OrganizationProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'organization_profile_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.request.user.organization
        context['organization'] = organization
        context['pending_volunteer_hours'] = VolunteerHour.objects.filter(
            organization=organization, status='waiting')
        return context

    def post(self, request, *args, **kwargs):
        organization = self.request.user.organization
        volunteer_hour_id = request.POST.get('volunteer_hour_id')
        action = request.POST.get('action')
        volunteer_hour = get_object_or_404(VolunteerHour, id=volunteer_hour_id, organization=organization)
        if action == 'approve':
            volunteer_hour.status = 'approved'
            volunteer_hour.user.hours += volunteer_hour.hours
            volunteer_hour.user.save()
        elif action == 'reject':
            volunteer_hour.status = 'rejected'
        volunteer_hour.save()
        return redirect(reverse('organization_profile'))
    
    from django.shortcuts import render

    
    
#------------------------------------------------opportunity views--------------------------------------

from django.contrib.auth.models import User

def opportunity_list(request):
    category = request.GET.get('category', '')
    total_hours_min = request.GET.get('total_hours_min', 0)
    total_hours_max = request.GET.get('total_hours_max', 0)
    start_date = request.GET.get('start_date', '')
    impact_score_min = request.GET.get('impact_score_min', 0)
    impact_score_max = request.GET.get('impact_score_max', 0)

    filters = Q()
    if category:
        filters &= Q(category=category)
    if total_hours_min:
        filters &= Q(total_hours__gte=total_hours_min)
    if total_hours_max:
        filters &= Q(total_hours__lte=total_hours_max)
    if start_date:
        filters &= Q(start_date=start_date)
    if impact_score_min:
        filters &= Q(impact_score__gte=impact_score_min)
    if impact_score_max:
        filters &= Q(impact_score__lte=impact_score_max)

    opportunities = Opportunity.objects.filter(filters)
    categories = Opportunity.objects.values_list('category', flat=True).distinct()

    user_profile = None
    user_skills = []
    user_interests = []

    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
            user_skills = user_profile.skills.all()
            user_interests = user_profile.interests.all()
        except User.userprofile.RelatedObjectDoesNotExist:
            # Handle the case when userprofile does not exist
            pass

    context = {
        'opportunities': opportunities,
        'categories': categories,
        'show_filter_by_skills': True,
        'show_filter_by_interests': True,
        'user_skills': user_skills,
        'user_interests': user_interests,
    }

    return render(request, 'opportunity_list.html', context)




def opportunity_detail(request, opportunity_id):
    opportunity = get_object_or_404(Opportunity, pk=opportunity_id)
    return render(request, 'opportunity_detail.html', {'opportunity': opportunity})

    
def opportunity_count(request):
    count = Opportunity.objects.count()
    return JsonResponse({'count': count})

def opportunities_json(request):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    json_file_path = os.path.join(current_directory, 'management', 'commands', 'sample_data.json')

    with open(json_file_path) as f:
        data = json.load(f)

    opportunities = data.get('Opportunity', [])

    opportunity_data = []
    for opportunity in opportunities:
        opportunity_data.append({
            'title': opportunity['title'],
            'location': opportunity['location'],
            'latitude': opportunity.get('latitude', None),
            'longitude': opportunity.get('longitude', None),
        })

    return JsonResponse(opportunity_data, safe=False)



#-------------------------------------------------signupviews----------------------------------------------

def user_signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('home')
    else:
        form = UserSignupForm()
    return render(request, 'registration/user_signup.html', {'form': form})


def organization_signup(request):
    if request.method == 'POST':
        form = OrganizationSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('')
    else:
        form = OrganizationSignupForm()
    return render(request, 'registration/organization_signup.html', {'form': form})

                
def signup_choice(request):
    return render(request, 'signup.html')


def signup_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('userType')
        
        if user_type == 'volunteer':
            return redirect('user_signup')  
        elif user_type == 'organization':
            return redirect('organization_signup')
        else:
            messages.error(request, 'Invalid user type selection')
            return render (request, 'signup.html')
    
    return render(request, 'signup.html')



#--------------------------------profile_views---------------------------------------------------

def user_detail(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'userprofile'):
            user_profile = UserProfile.objects.get(user=request.user)
            return render(request, 'user_profile_view.html', {'user_profile': user_profile})
        elif hasattr(request.user, 'organization'):
            organization_profile = Organization.objects.get(user=request.user)
            return render(request, 'organization_profile_view.html', {'organization_profile': organization_profile})
    else:
        return render(request, 'not_logged_in.html')
    
from django.contrib.auth.forms import SetPasswordForm

@login_required
def edit_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_detail')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'registration/edit_profile.html', {'form': form})


@login_required
def user_detail(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'userprofile'):
            user_profile = UserProfile.objects.get(user=request.user)
            category_impact_scores = VolunteerHour.category_impact_scores_by_user_category(user_profile)
            return render(request, 'user_profile_view.html', {'user_profile': user_profile, 'category_impact_scores': category_impact_scores})
        elif hasattr(request.user, 'organization'):
            organization_profile = Organization.objects.get(user=request.user)
            return render(request, 'organization_profile_view.html', {'organization_profile': organization_profile})
    else:
        # Handle when user is not logged in
        return render(request, 'not_logged_in.html')

def maps_view(request):
    return render(request, 'maps.html')



#------------------------------------- chatbot and otehr views ---------------------------------

#@login_required
def send_message(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        # Publish message to Pusher channel
        pusher_client = Pusher(app_id='YOUR_PUSHER_APP_ID', key='YOUR_PUSHER_KEY', secret='YOUR_PUSHER_SECRET', cluster='YOUR_PUSHER_CLUSTER', ssl=True)
        pusher_client.trigger('chat-channel', 'message', {'sender': request.user.username, 'message': message})
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})
    
def chat_view(request):
    return render(request, 'chat.html')

def buy(request):
    return render(request, 'buy.html')

def donate(request):
    return HttpResponseRedirect('https://buy.stripe.com/test_fZe3f55lG3SAdeUfYY')


@csrf_exempt
def chatbot_view(request):
    print("chatbot called")
    if request.method == "POST":
        user_input = request.POST.get("user_input", "")
        
        response = generate_response(user_input)
        
        return JsonResponse({"response": response})
    
    initial_message = "Hello! I'm Zeno, your AI assistant. How can I help you today? Are you looking for volunteer opportunities or do you have any specific questions about volunteering?"
    return render(request, 'chatbot.html', {'initial_message': initial_message})




#---------pusher----------

pusher = Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True
)

pusher = Pusher(app_id=u'1791472', key=u'61ceb534a3e26347598b', secret=u'2b32d1d10c546a9abce8', cluster=u'eu')
    
    
@login_required(login_url='signup/user')
def index(request):
    print("index called")
    return render(request,"chat.html");


@csrf_exempt
def broadcast(request):
        print("broadcast called")

        # collect the message from the post parameters, and save to the database
        message = Conversation(message=request.POST.get('message', ''), status='', user=request.user);
        message.save();
        # create an dictionary from the message instance so we can send only required details to pusher
        message = {'name': message.user.username, 'status': message.status, 'message': message.message, 'id': message.id}
        #trigger the message, channel and event to pusher
        pusher.trigger(u'a_channel', u'an_event', message)
        # return a json response of the broadcasted message
        return JsonResponse(message, safe=False)

    #return all conversations in the database
def conversations(request):
        print("conversations called")

        data = Conversation.objects.all()
        # loop through the data and create a new list from them. Alternatively, we can serialize the whole object and send the serialized response 
        data = [{'name': person.user.username, 'status': person.status, 'message': person.message, 'id': person.id} for person in data]
        # return a json response of the broadcasted messgae
        return JsonResponse(data, safe=False)

        #use the csrf_exempt decorator to exempt this function from csrf checks
@csrf_exempt
def delivered(request, id):
        print("delivered called")

        message = Conversation.objects.get(pk=id);
        # verify it is not the same user who sent the message that wants to trigger a delivered event
        if request.user.id != message.user.id:
            socket_id = request.POST.get('socket_id', '')
            message.status = 'Delivered';
            message.save();
            message = {'name': message.user.username, 'status': message.status, 'message': message.message, 'id': message.id}
            pusher.trigger(u'a_channel', u'delivered_message', message, socket_id)
            return HttpResponse('ok');
        else:
            return HttpResponse('Awaiting Delivery');
        
        
        
#------------------------------------------------volunteerhours and impact score views------------------------------
@login_required
def submit_volunteer_hours(request, opportunity_id):
    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    
    if request.method == 'POST':
        hours = request.POST.get('hours')
        user_profile = request.user.userprofile
        
        # Check if the submitted hours exceed the total hours available for the opportunity
        if float(hours) > opportunity.total_hours:
            messages.error(request, 'Cannot submit more hours than available for this opportunity.')
            return redirect('opportunity_detail', opportunity_id=opportunity_id)
        
        volunteer_hour = user_profile.submit_volunteer_hours(opportunity, hours)
        messages.success(request, 'Volunteer hours submitted successfully!')
        return redirect('opportunity_detail', opportunity_id=opportunity_id)
    
    return render(request, 'submit_volunteer_hours.html', {'opportunity': opportunity})




@login_required
def timesheet_detail(request, timesheet_id):
    timesheet = get_object_or_404(VolunteerHour, id=timesheet_id, user=request.user.userprofile)
    return render(request, 'timesheet_detail.html', {'timesheet': timesheet})

@login_required
def timesheet_list(request):
    user_profile = request.user.userprofile
    timesheets = VolunteerHour.objects.filter(user=user_profile)
    return render(request, 'timesheet_list.html', {'timesheets': timesheets})

from django.db.models import Sum

# Ensure that the leaderboard view is calculating and displaying the leaderboard correctly
def leaderboard(request):
    selected_category = None
    sorted_users = None
    categories = ["Environmental", "Social Welfare", "Educational", "Health Care", "Animal Welfare", "Sports and Recreation", "Disability Services", "Faith Based", "All"]

    if request.method == 'POST':
        category = request.POST.get('category')
        selected_category = category
        if category == "All":
            # Get the total impact score for each user across all categories
            all_category_hours = VolunteerHour.objects.values('user').annotate(total_hours=Sum('hours'))
            users_impact_scores = {}
            for hour in all_category_hours:
                user_profile = UserProfile.objects.get(pk=hour['user'])
                impact_score = hour['total_hours'] * 10  # Assuming each hour contributes 10 to the impact score
                users_impact_scores[user_profile] = impact_score

            # Sort the users by their total impact scores
            sorted_users = sorted(users_impact_scores.items(), key=lambda x: x[1], reverse=True)
        else:
            # Get impact scores for the specified category
            users_impact_scores = VolunteerHour.category_impact_scores_by_user_category_lboard(category)
            # Sort the users by their impact scores
            sorted_users = sorted(users_impact_scores.items(), key=lambda x: x[1], reverse=True)

    return render(request, 'leaderboard.html', {'selected_category': selected_category, 'sorted_users': sorted_users, 'categories': categories})
