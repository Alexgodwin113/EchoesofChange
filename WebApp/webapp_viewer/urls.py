from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static
from .views import OrganizationUpdateView
from .views import leaderboard
from .views import OrganizationUpdateView, chatbot_view

urlpatterns = [
        path('organizations', views.organization_list , name='organization_list'),
        path('organizations/<int:pk>', views.organization_details, name= 'organization_details'),
        path('organizations/<int:pk>/update/', views.OrganizationUpdateView.as_view(), name='organization_update'),
    
        path('signup/', views.signup_view, name='signup'),
        path('signup/user', views.user_signup, name='user_signup'),
        path('signup/organization', views.organization_signup, name='organization_signup'),
        
        path('profile/edit', views.edit_profile, name='edit_profile'),
        path('userprofile/', views.user_detail, name='user_detail'),
        path('organizationprofile/', views.OrganizationProfileView.as_view(), name='organization_profile'),
        
        path('opportunities/', views.opportunity_list, name='opportunity_list'),
        path('opportunities/<int:opportunity_id>/', views.opportunity_detail, name='opportunity_detail'),
        path('opportunities/json/', views.opportunities_json, name='opportunities_json'),
        path('opportunities/<int:opportunity_id>/submit-hours/', views.submit_volunteer_hours, name='submit_volunteer_hours'),

        path('api/organizations/count', views.organization_count, name='organization-count'),
        path('api/opportunity/count', views.opportunity_count, name='opportunity-count'),
        path('api/search_organizations/', views.search_organizations, name='search_organizations'),
        
      
        path('maps', views.maps_view, name='maps_view'),
        path('chat', views.index, name='index'),
        path('conversation', views.broadcast, name='conversation_detail'),  # Added name for clarity
        path('conversations', views.conversations, name='conversation_list'),
        path('conversations/<int:id>/delivered', views.delivered, name='conversation_delivered'),  # Use `int` for numeric IDs
        path('send_message/', views.send_message, name='send_message'),
        
        path('buy', views.buy, name='buy'),
        path('donate/', views.donate, name='donation'),

        path('timesheets/<int:timesheet_id>/', views.timesheet_detail, name='timesheet_detail'),   
        path('timesheets/', views.timesheet_list, name='timesheet_list'),  

        path('leaderboard/', leaderboard, name='leaderboard'),
        path('chatbot/', views.chatbot_view, name='chatbot'),

]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)