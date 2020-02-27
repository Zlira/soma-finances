from django.db import models
from django.utils.timezone import now



class Expense(models.Model):
    MAIN_CAT = 'main'
    BAR_CAT = 'bar'
    SPACE_CAT = 'space'
    FEES_CAT = 'fees'
    CATEGORY_CHOICES =  [
        (MAIN_CAT, 'основні'),
        (BAR_CAT, "бар"),
        (SPACE_CAT, "простір"),
        (FEES_CAT, "гонорари"),
    ]

    category = models.CharField('категорія', max_length=191, choices=CATEGORY_CHOICES)
    description = models.CharField('опис', max_length=250)
    date = models.DateField('дата', default=now)
    amount = models.IntegerField('сума', default=0)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Витрати'
        verbose_name_plural = 'Витрати'

    def __str__(self):
        return f'{self.description} ({self.date})'

    @classmethod
    def aggregate_for_period(cls, start_date, end_date):
        filtered = cls.objects.filter(
            date__gte=start_date, date__lte=end_date
        )
        res = {}
        detailed_categories = [
            cls.FEES_CAT, cls.MAIN_CAT,
        ]
        for category in detailed_categories:
            entries = (
                filtered.filter(category=category)
                .values('description', 'amount')
            )
            res[category] = {
                'total': sum(e['amount'] for e in entries),
                'detailed': {
                    e['description']: e['amount'] for e in entries
                }
            }
        not_detailed_categories = [
            cat[0] for cat in cls.CATEGORY_CHOICES if cat[0] not in detailed_categories
        ]
        entries = (
            filtered.filter(category__in=not_detailed_categories)
                    .values('category')
                    .annotate(total=models.Sum('amount'))
                    .order_by('category'))
        for e in entries:
            res[e['category']] = {'total': e['total']}
        return res