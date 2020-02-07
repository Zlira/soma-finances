from datetime import date

from django.db.models import(
    Value, CharField, F, DurationField,
    ExpressionWrapper, fields, Count, Min, Q
)
from django.db.models.functions import Cast
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe

from .models import ParticipantPaper, Paper, Participant
from .auth import require_authentification


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
               times_used=F('times_used')
           )
           .order_by(F('times_used').desc())
           )
    for i in res:
        if i['days_in_use'] is None:
            i['days_in_use'] = 0
        else:
            i['days_in_use'] = i['days_in_use'].days
    return JsonResponse({'participantPapers': list(res)})


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
