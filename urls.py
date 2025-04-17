from django.urls import path
from django.conf import settings
from . import views
from .views import soil_analysis_results, analyze_soil_image

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path("suggest_crops/", views.suggest_crops, name="suggest_crops"),
    path('expense/', views.expense_tracker, name='expense'),
    path("view_expenses/", views.view_expenses, name="view_expenses"),
    path('weather/', views.get_weather, name='weather'),
    path('analytics/', views.analytics, name='analytics'),
    path('upload-soil-map/', views.upload_soil_map, name='upload_soil_map'),
    path('soil-analysis-results/', soil_analysis_results, name='soil_analysis_results'),
    path('analyze-soil-image/', analyze_soil_image, name='analyze_soil_image'),
    path("analyze-result/<str:image_name>/<int:fake>/", views.analyze_soil_image, name="analyze_result"),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

]

from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


