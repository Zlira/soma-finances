from django.db import models

from .custom_fields import SimpleJsonField


def add_to_month(year, month, delta_months):
    new_month = (month -1 + delta_months) % 12 + 1
    year_delta = (month -1 + delta_months) // 12
    return year + year_delta, new_month


class MonthlyReport(models.Model):
    MONTH_CHOICES = [
        (1, 'січень'),
        (2, "лютий"),
        (3, "березень"),
        (4, "квітень"),
        (5, "травень"),
        (6, "червень"),
        (7, "липень"),
        (8, "серпень"),
        (9, "вересень"),
        (10, "жовтень"),
        (11, "листопад"),
        (12, "грудень"),
    ]
    year = models.IntegerField('рік')
    month = models.IntegerField('місяць', choices=MONTH_CHOICES)
    total_balance = models.DecimalField('баланс за місяць',
        max_digits=12, decimal_places=2, null=True, blank=True)
    money_left = models.DecimalField('в наявності',
        max_digits=12, decimal_places=2, null=True, blank=True)
    report = SimpleJsonField('звіт', null=True, blank=True)

    class Meta:
        ordering = ['-year', '-month']
        verbose_name = 'Звіт за місяць'
        verbose_name_plural = 'Звіти за місяць'
        constraints = (models.UniqueConstraint(
            fields=['year', 'month'],
            name='%(app_label)s_%(class)s_year_month_unique_together',
        ), )

    def __str__(self):
        return f'Звіт за {self.get_month_display()} {self.year}'

    def _previous(self):
        # FIXME doesn't work with deferred instances?
        cls = type(self)
        prev_year, prev_month = add_to_month(self.year, self.month, -1)
        return cls.objects.filter(
            year=prev_year,
            month=prev_month,
        )

    def _next(self):
        # FIXME doesn't work with deferred instances?
        cls = type(self)
        prev_year, prev_month = add_to_month(self.year, self.month, 1)
        return cls.objects.filter(
            year=prev_year,
            month=prev_month,
        )

    def get_previous(self):
        return self._previous().only()

    def get_next(self):
        return self._next().only()

    def is_latest(self):
        return not self._next().exists()