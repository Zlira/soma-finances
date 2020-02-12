from django.db.models import Value, CharField
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe
from django.forms.fields import DateField
from django.forms import ValidationError

from .models import ParticipantPaper, Paper, Teacher
from .accounting import get_detailed_teachers_salary_for_period
from .forms import DateRangeForm


# TODO should we use something like ajax_required decorator


def participant_papers(request):
    participant_id = request.GET.get('participant_id')
    if not participant_id:
        return HttpResponseBadRequest('participant_id is required')
    # TODO check if participant exists
    res = (ParticipantPaper.objects
           # TODO add expired filter
           .filter(participant=participant_id)
           .select_related('participant', 'paper')
           .values(
               'id',
               name=Concat(
                   'paper__name', Value(' належить '), 'participant__name',
               )
           )
           )
    return JsonResponse({'participantPapers': list(res)})


def paper(request):
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)
    paper_id = request.GET.get('paper_id')
    if not paper_id:
        return HttpResponseBadRequest('paper_id is required')
    paper = get_object_or_404(Paper, id=paper_id)
    fields = ['id', 'name', 'price', 'number_of_uses']
    return JsonResponse(
        {field: getattr(paper, field) for field in fields}
    )


# TODO delete this or fix date isoformat
@require_safe
def detialed_teachers_salary(request, teacher_id):
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)
    query_str_form = DateRangeForm(request.GET)
    if not query_str_form.is_valid():
        return JsonResponse(query_str_form.errors, status=400)
    teacher = get_object_or_404(Teacher, id=teacher_id)
    detailed_salary = get_detailed_teachers_salary_for_period(
        teacher, **query_str_form.cleaned_data
    )
    return JsonResponse(detailed_salary)
