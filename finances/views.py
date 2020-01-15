from django.db import connection
from django.db.models import Value, CharField
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404

from .models import ParticipantPaper, Paper


# TODO add authentication

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
    qs = connection.queries
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
