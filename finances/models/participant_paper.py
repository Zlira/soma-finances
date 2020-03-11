from datetime import date

from django.db import models
from django.utils.timezone import now

from .participant import Participant
from .paper import Paper


class ParticipantPaper(models.Model):
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name="учасни_ця",
    )
    paper = models.ForeignKey(
        Paper, on_delete=models.CASCADE, verbose_name="папірець"
    )
    date_purchased = models.DateField("дата купівлі", default=now)
    is_volunteer = models.BooleanField("чи волонтерський?", default=False, editable=True)

    def __str__(self):
        return f"Папірець ({self.id}) учасни_ці {self.participant.id}"

    @classmethod
    def aggregate_earnings_for_period(cls, start_date, end_date):
        return (
            cls.objects
               .filter(date_purchased__gte=start_date, date_purchased__lte=end_date)
               .values('paper__name', 'paper__price')
               .annotate(count=models.Count('paper__name'), amount=models.Sum('paper__price'))
        )

    def get_number_of_uses(self):
        return self.classparticipation_set.count()

    def get_first_use_date(self):
        return (
            self.classparticipation_set
            .aggregate(min_date=models.Min('class_unit__date'))['min_date']
        )

    def has_use_number_limit(self):
        return bool(self.paper.number_of_uses)

    def is_expired(self, for_unit=None):
        first_use_date = self.get_first_use_date()
        if not first_use_date:
            return False
        soft_limit = self.paper.days_valid
        hard_limit = soft_limit * 2 if self.has_use_number_limit() else soft_limit

        for_date = date.today() if not for_unit else for_unit.date
        return (for_date - first_use_date).days > hard_limit

    def is_tentatively_expired(self):
        first_use_date = self.get_first_use_date()
        if not first_use_date:
            return False
        soft_limit = self.paper.days_valid
        hard_limit = soft_limit * 2 if self.has_use_number_limit() else soft_limit
        days_in_use = (date.today() - first_use_date).days
        return (
            soft_limit < days_in_use <= hard_limit
        )

    def was_used_on_unit(self, unit_id):
        return self.classparticipation_set.filter(class_unit=unit_id).exists()

    def is_out_of_uses(self, for_unit=None):
        number_of_uses = self.get_number_of_uses()
        if for_unit:
            if self.was_used_on_unit(for_unit):
                number_of_uses -= 1
        return (
            self.paper.number_of_uses and
            number_of_uses >= self.paper.number_of_uses
        )

    def is_valid(self):
        return not self.is_out_of_uses() and not self.is_expired() \
            and not self.is_tentatively_expired()