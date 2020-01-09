from django.db import models

from .regular_class import RegularClass
from .participant import Participant
from .class_participation import ClassParticipation
from .teacher import Teacher


class ClassUnit(models.Model):
    regular_class = models.ForeignKey(
        RegularClass, on_delete=models.CASCADE, verbose_name="курс"
    )
    date = models.DateField('дата')
    participants = models.ManyToManyField(
        Participant, through='ClassParticipation', verbose_name="учасни_ці"
    )
    teacher = models.ForeignKey(
        Teacher, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name='викладач/ка',
    )
    comment = models.TextField('коментар', null=True, blank=True)

    class Meta:
        ordering = ['-date', 'regular_class']
        verbose_name = 'Конкретне заняття'
        verbose_name_plural = 'Конкретні заняття'


    def __str__(self):
        return f'{self.regular_class} ({self.date})'

    # TODO add halfmonthly balance

    def get_price_by_payement_methods(self, filters=None):
        filters = filters or []
        payment_methods = ClassParticipation.get_aggregated_payment_methods(
            ClassParticipation.objects
            .filter(class_unit=self, *filters)
        )
        return {item['payment_method']: item['count'] for item in payment_methods}

