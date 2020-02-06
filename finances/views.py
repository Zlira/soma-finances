from django.db.models import(
    Value, CharField, F, DurationField,
    ExpressionWrapper, fields, Count
)
from django.db.models.functions import Cast
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404

from .models import ParticipantPaper, Paper
from datetime import date

# TODO add authentication


def participant_papers(request):
    participant_id = request.GET.get('participant_id')
    if not participant_id:
        return HttpResponseBadRequest('participant_id is required')
    # TODO check if participant exists
    days_in_use = ExpressionWrapper(
        Cast(date.today(), fields.DateField()) - F('date_purchased'),
        output_field=fields.DurationField()
    )
    res = (ParticipantPaper.objects
           # TODO add expired filter
           .annotate(
               days_in_use=days_in_use,
               times_used=Count('classparticipation')
           )
           .filter(participant=participant_id)
           .select_related('participant', 'paper')
           .values(
               'id',
               name=F('paper__name'),
               days_in_use=F('days_in_use'),
               times_used=F('times_used')
           )
           )
    for i in res:
        i['days_in_use'] = i['days_in_use'].days
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
