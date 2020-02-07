from itertools import groupby
from operator import itemgetter

from django.db import models

from .constants import ONE_TIME_PRICE_LABEL
from .default_constants import Constants
from .paper import Paper
from .class_unit import ClassUnit


class Teacher(models.Model):
    name = models.CharField("ім'я", max_length=260)

    class Meta:
        verbose_name = 'Викладач_ка'
        verbose_name_plural = 'Викладач_ки'

    def __str__(self):
        return self.name

    def get_classes_for_period(self, start_date, end_date):
        # TODO do i even need this?
        return RegularClass.objects.filter(
            classunit__teacher=self,
            classunit__date__gte=start_date,
            classunit__date__lte=end_date,
        ).distinct()

    def get_units_for_period(self, start_date, end_date):
        return (ClassUnit.objects
            .filter(
                teacher=self,
                date__gte=start_date,
                date__lte=end_date)
            # TODO write a test to confirm sortin is correct
            .order_by('regular_class', 'date')
            .select_related('regular_class'))