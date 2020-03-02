from datetime import date

from django.db.models import Value, CharField, F, DurationField, \
    ExpressionWrapper, fields, Count, Min, Q
from django.db.models.functions import Cast, Concat
from django.contrib import messages
from django.forms.fields import DateField
from django.forms import ValidationError
from django.http import JsonResponse, HttpResponseBadRequest, \
    HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_safe, require_POST
from django.utils.safestring import mark_safe
from django.urls import reverse

from .auth import require_authentification
from .models import ParticipantPaper, Paper, Participant, Teacher, Expense
from .accounting import get_detailed_teachers_salary_for_period
from .forms import DateRangeForm


# TODO should we use something like ajax_required decorator


@require_safe
@require_authentification
def participant_papers(request, participant_id):
    get_object_or_404(Participant, pk=participant_id)
    days_in_use = ExpressionWrapper(
        Cast(date.today(), fields.DateField()) -
        Min('classparticipation__class_unit__date'),
        output_field=fields.DurationField()
    )
    res = (ParticipantPaper.objects
           .annotate(
               days_in_use=days_in_use,
               times_used=Count('classparticipation')
           )
           .filter(
               Q(paper__number_of_uses__gt=F('times_used')) |
               Q(paper__number_of_uses__isnull=True),
               participant=participant_id
           )
           .select_related('participant', 'paper')
           .values(
               'id',
               name=F('paper__name'),
               days_in_use=F('days_in_use'),
               times_used=F('times_used'),
               days_valid=F('paper__days_valid')
           )
           .order_by(F('times_used').desc())
           )

    response = []
    for paper in res:
        if paper['days_in_use'] is None:
            paper['days_in_use'] = 0
        else:
            paper['days_in_use'] = paper['days_in_use'].days
        if paper['days_valid']*2 < paper['days_in_use']:
            continue
        paper['tentatively_expired'] = paper['days_in_use'] > paper['days_valid']
        paper.pop('days_valid')
        response.append(paper)

    return JsonResponse({'participantPapers': list(response)})


@require_safe
@require_authentification
def paper(request):
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
