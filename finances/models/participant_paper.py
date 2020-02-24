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
    # check with the price of paper
    # price = models.IntegerField("ціна")
    def __str__(self):
        # TODO does this issue new db query? should select_releted be used?
        first_use = self.get_first_use_date()
        days_in_use = 0 if not first_use else (date.today() - first_use).days
        return f"{self.paper.name} (використовується {days_in_use} днів, {self.get_number_of_uses()} раз)"

    def get_number_of_uses(self):
        return self.classparticipation_set.count()

    def get_first_use_date(self):
        return (
            self.classparticipation_set
            .aggregate(min_date=models.Min('class_unit__date'))['min_date']
        )

    def has_use_number_limit(self):
        return bool(self.paper.number_of_uses)

    def is_expired(self):
        first_use_date = self.get_first_use_date()
        if not first_use_date:
            return False
        soft_limit = self.paper.days_valid
        hard_limit = soft_limit * 2 if self.has_use_number_limit() else soft_limit
        return (
            (date.today() - first_use_date).days > hard_limit
        )

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

    def is_out_of_uses(self):
        return (
            self.paper.number_of_uses and
            self.get_number_of_uses() >= self.paper.number_of_uses
        )

    def is_valid(self):
        return not self.is_out_of_uses() and not self.is_expired() \
            and not self.is_tentatively_expired()