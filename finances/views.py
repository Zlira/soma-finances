from django.db import connection
from django.db.models import Value, CharField
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponseBadRequest

from .models import ParticipantPaper


def participant_papers(request):
    participant_id = request.GET.get('participant_id')
    if not participant_id:
        return HttpResponseBadRequest('participant_id is required')
    res = (ParticipantPaper.objects
        # TODO add expired filter
        .filter(participant=participant_id)
        .select_related('participant', 'paper')
        .values(
            'id',
            name=Concat(
                'paper__paper_type', Value(' належить '), 'participant__name',
            )
        )
    )
    qs = connection.queries
    print(len(qs))
    return JsonResponse({'participantPapers': list(res)})
