from django.db import models


class SingleEvent(models.Model):
    name = models.CharField("назва", max_length=191)
    date = models.DateField('дата')
    admission_sum = models.IntegerField('сума внесків', default=0)
    bar_sum = models.IntegerField('сума за бар', default=0)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Одноразова подія'
        verbose_name_plural = 'Одноразові події'

    def overall_sum(self):
        return self.admission_sum + self.bar_sum
    overall_sum.short_description = 'Загалом'

    def __str__(self):
        return f'{self.name} ({self.date})'

    @classmethod
    def aggregate_earnings_for_period(cls, start_date, end_date):
        filtered = cls.objects.filter(
            date__gte=start_date, date__lte=end_date
        )
        total = (
            filtered.annotate(total_sum=models.F('admission_sum') + models.F('bar_sum'))
            .aggregate(total=models.Sum('total_sum'))
        )
        total = total['total'] or 0
        detailed = filtered.values(
            'name', admission=models.F('admission_sum'),
            bar=models.F('bar_sum')
        )
        detailed = {event.pop('name'): event for event in detailed}
        return {'total': total, 'detailed': detailed}