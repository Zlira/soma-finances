from django.contrib import messages
from django.db.models import Value, CharField
from django.db.models.functions import Concat
from django.forms.fields import DateField
from django.forms import ValidationError
from django.http import JsonResponse, HttpResponseBadRequest, \
    HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_safe, require_POST
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import ParticipantPaper, Paper, Teacher, Expense
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


@require_POST
def teachers_salary(request, teacher_id):
    # TODO replace this with a decorator
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)
    form = DateRangeForm(request.POST)
    if not form.is_valid():
        return HttpResponse(form.errors, status=400)
    start_date = form.cleaned_data['start_date']
    end_date = form.cleaned_data['end_date']

    teacher = get_object_or_404(Teacher, pk=teacher_id)
    salary_report = get_detailed_teachers_salary_for_period(
        teacher, start_date, end_date
    )
    salary = sum(class_.sum_teachers_share() for class_ in salary_report)
    if salary <= 0:
        messages.warning(
            request,
            "Винагорода становила 0 грн, тому не записана"
        )
    else:
        description = (
            f'Винагорода для {teacher.name} за {start_date} - {end_date}'
        )
        expense = Expense.objects.create(
            category=Expense.FEES_CAT,
            amount=salary,
            description=description
        )
        # TODO get admin urls from model
        expense_url = reverse(
            'admin:finances_expense_change', args=[expense.id]
        )
        messages.info(
            request,
            mark_safe(f'<a href="{expense_url}">Винагорода</a> збережена!')
        )

    # TODO or maybe redirect to the expense page?
    redirect_url = (
        reverse('admin:finances_teacher_change', args=[teacher.id]) +
        f'?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}'
    )
    return HttpResponseRedirect(redirect_url)