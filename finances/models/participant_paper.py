from datetime import date

from django.db import models

from .participant import Participant
from .paper import Paper


class ParticipantPaper(models.Model):
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name="учасни_ця",
    )
    paper = models.ForeignKey(
        Paper, on_delete=models.CASCADE, verbose_name="папірець"
    )
    date_purchased = models.DateField("дата купівлі")
    is_volunteer = models.BooleanField("чи волонтерський?", default=False, editable=True)
    # check with the price of paper
    # price = models.IntegerField("ціна")
    def __str__(self):
        # TODO does this issue new db query? should select_releted be used?
        return f"{self.paper.name} ({self.get_number_of_uses()} використання, {self.participant.name})"

    def get_number_of_uses(self):
        return self.classparticipation_set.count()

    def get_first_use_date(self):
        return (
            self.classparticipation_set
            .aggregate(min_date=models.Min('class_unit__date'))['min_date']
        )

    def is_expired(self):
        uses_ran_out = (
            self.paper.number_of_uses and
            self.get_number_of_uses() >= self.paper.number_of_uses
        )
        first_use_date = self.get_first_use_date()
        time_ran_out = (
            first_use_date and
            (date.today() - self.get_first_use_date()).days >
            self.paper.days_valid
        )
        # TODO what about if we want to use it in the past?
        return any([uses_ran_out, time_ran_out])