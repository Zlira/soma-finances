from django.db import models


class Papers(models.Model):
    paper_type = models.CharField('тип', max_length=260)
    min_price = models.IntegerField('мінімальна ціна')
    max_price = models.IntegerField('максимальна ціна')
    # days_valid = models.IntegerField('скільки днів дійсний', null=True)
    # description

    def __str__(self):
        return self.paper_type
