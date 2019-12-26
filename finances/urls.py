from django.urls import path

from . import views


urlpatterns = [
    path('participant_papers/', views.participant_papers, name='participant_papers'),
]