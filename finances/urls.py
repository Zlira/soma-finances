from django.urls import path

from . import views


urlpatterns = [
    path(
        'participant/<int:participant_id>/papers',
        views.participant_papers, name='participant_papers'
    ),
    path('paper/', views.paper, name="paper"),
]
