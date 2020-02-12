from django.urls import path

from . import views


urlpatterns = [
    path('participant_papers/', views.participant_papers, name='participant_papers'),
    path('paper/', views.paper, name="paper"),
    path('teacher/<int:teacher_id>/detailed_salary/',
         views.detialed_teachers_salary,
         name='detailed_teachers_salary',
    )
]