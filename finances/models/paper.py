from django.db import models

from .default_constants import Constants


class Paper(models.Model):
    name = models.CharField('назва', max_length=260)
    price = models.IntegerField('внесок')
    days_valid = models.IntegerField('скільки днів дійсний', default=30)
    number_of_uses = models.IntegerField(
        'скільки занять дійсний', null=True, blank=True)
    # description

    class Meta:
        verbose_name = 'Папірець'
        verbose_name_plural = 'Папірці'

    def __str__(self):
        return self.name

    # TODO create a manager with this?
    @classmethod
    def get_one_time_price_expression(cls):
        return models.Case(
            models.When(number_of_uses__isnull=True,
                        then=models.Value(
                            Constants.get_min_one_time_paper_price())),
            default=models.F('price') / models.F('number_of_uses'),
            output_field=models.FloatField()
        )

    def get_one_time_price(self):
        return (
            self.price / self.number_of_uses
            if self.number_of_uses
            else Constants.get_min_one_time_paper_price()
        )
