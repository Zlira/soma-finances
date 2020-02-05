from django.db import models

from .participant import Participant
from .participant_paper import ParticipantPaper
from .constants import ONE_TIME_PRICE_LABEL


class ClassParticipation(models.Model):
    # TODO add a constraint that only paper_used or one time price is
    # filled out or use

    class_unit = models.ForeignKey(
        'ClassUnit', on_delete=models.CASCADE, verbose_name="заняття"
    )
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name="учасни_ця"
    )
    # TODO add restriction that this should be participant's paper
    paper_used = models.ForeignKey(
        ParticipantPaper, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name="використаний папірець"
    )
    paid_one_time_price = models.BooleanField(
        'одноразовий внесок', default=False)

    def __str__(self):
        return f'{self.participant} на {self.class_unit}'

    @classmethod
    def get_payment_method_expression(cls):
        # TODO maybe use one type: either strig or int
        return models.Case(
            models.When(paid_one_time_price=True,
                        then=models.Value(ONE_TIME_PRICE_LABEL)),
            models.When(paper_used__isnull=False,
                        then=models.F('paper_used__paper')),
            default=models.Value(0)
        )

    # TODO move this to a custom manager?
    @classmethod
    def get_aggregated_payment_methods(cls, query_set):
        return (
            query_set
            .annotate(payment_method=cls.get_payment_method_expression())
            .values('payment_method')
            .annotate(count=models.Count('payment_method'))
            .values('payment_method', 'count')
        )

    def get_price(self):
        price = None
        if self.paid_one_time_price:
            price = self.class_unit.regular_class.one_time_price
        elif self.paper_used:
            price = self.paper_used.paper.get_one_time_price()
        return price
