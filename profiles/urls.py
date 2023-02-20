from django.urls import path

from . import views


urlpatterns = [
    path("profile/<int:pk>/", views.ProfileDetail.as_view()),
    path("update/<int:pk>/", views.ProfileUpdateView.as_view()),
    path("update/avatar/<int:pk>/", views.AvatarProfileUpdateView.as_view()),
]