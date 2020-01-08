from itertools import groupby
from operator import itemgetter

from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
import pandas as pd

# TODO add unique constraints


ONE_TIME_PRICE_LABEL = 'одноразова ціна'
MIN_ONE_TIME_PAPER_PRICE = 35
MIN_TEACHERS_SALARY = 100


class Paper(models.Model):
    name = models.CharField('назва', max_length=260)
    price = models.IntegerField('внесок')
    days_valid = models.IntegerField('скільки днів дійсний', default=30)
    number_of_uses = models.IntegerField('скільки занять дійсний', null=True, blank=True)
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
            models.When(number_of_uses__isnull=True, then=models.Value(MIN_ONE_TIME_PAPER_PRICE)),
            default=models.F('price') / models.F('number_of_uses'),
            output_field=models.FloatField()
        )

    def get_one_time_price(self):
        return (
            self.price / self.number_of_uses
            if self.number_of_uses
            else MIN_ONE_TIME_PAPER_PRICE
        )



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
    #TODO add a method to calculate salary for a period

    def get_detailed_salary_for_period(self, start_date, end_date):
        paper_prices = (
            Paper.objects
            .annotate(one_time_price=Paper.get_one_time_price_expression())
            .values('id', 'one_time_price', 'name')
        )
        paper_prices = {
            str(item['id']): {'name': item['name'], 'price': item['one_time_price']}
            for item in paper_prices
        }
        prices_df = pd.DataFrame.from_dict(paper_prices)
        units = ClassUnit.objects.filter(
            teacher=self,
            date__gte=start_date,
            date__lte=end_date,
        ).order_by('regular_class', 'date').select_related('regular_class')
        unit_payments = []
        for unit in units:
            payment_methods = unit.get_price_by_payement_methods()
            unit_payments.append({
                'regular_class': unit.regular_class, 'date': unit.date,
                'payment_methods':payment_methods,
            })
        res = {}
        for regular_class, unit_group in groupby(unit_payments, itemgetter('regular_class')):
            prices_df = prices_df.assign(**{
                ONE_TIME_PRICE_LABEL: pd.Series(
                    [ONE_TIME_PRICE_LABEL, regular_class.one_time_price],
                    index=['name', 'price']
                )
            })
            salary_df = pd.DataFrame.from_dict(
                {i['date']: i['payment_methods'] for i in unit_group}, orient='index'
            ).fillna(0).astype(int)
            unit_salary = (salary_df * prices_df.loc['price']).sum(axis=1) / 2
            unit_salary = unit_salary.where(
                unit_salary >= MIN_TEACHERS_SALARY, MIN_TEACHERS_SALARY
            )
            salary_df.columns = [prices_df.loc['name', col] for col in salary_df]
            unit_salary_label = 'всього за заняття'
            salary_df = salary_df.assign(**{unit_salary_label: unit_salary})
            res[regular_class.name] = salary_df
        return res


class RegularClass(models.Model):
    name = models.CharField('назва', max_length=260)
    start_date = models.DateField('дата початку')
    end_date = models.DateField('дата кінця', null=True, blank=True)
    one_time_price = models.IntegerField('ціна за одне заняття', blank=True, null=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курси'

    def __str__(self):
        return self.name


class Participant(models.Model):
    # todo distingiush between several people with the same name
    name = models.CharField("ім'я", max_length=260)
    papers = models.ManyToManyField(Paper, through='ParticipantPaper')
    date_created = models.DateField('дата першого знаяття', auto_now=True)
    phone_number = PhoneNumberField(verbose_name='номер телефону', region="UA", blank=True, null=True)
    email = models.EmailField('електронна адреса', blank=True, null=True)
    # TODO how did you learn about us

    class Meta:
        verbose_name = 'Учасни_ця'
        verbose_name_plural = 'Учасни_ці'

    def __str__(self):
        return self.name


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
    def is_expired(self):
        # TODO
        pass

    def __str__(self):
        # TODO does this issue new db query? should select_releted be used?
        # TODO add number of uses
        return f"{self.paper.name} належить {self.participant.name}"



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

    def get_price_by_payement_methods(self, filters=None):
        filters = filters or []
        payment_methods = ClassParticipation.get_aggregated_payment_methods(
            ClassParticipation.objects
            .filter(class_unit=self, *filters)
        )
        return {item['payment_method']: item['count'] for item in payment_methods}


class ClassParticipation(models.Model):
    # TODO add a constraint that only paper_used or one time price is
    # filled out or use
    class_unit = models.ForeignKey(
        ClassUnit, on_delete=models.CASCADE, verbose_name="заняття"
    )
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name="учасни_ця"
    )
    # TODO add restriction that this should be participant's paper, make this field optional
    paper_used = models.ForeignKey(
        ParticipantPaper, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name="використаний папірець"
    )
    paid_one_time_price = models.BooleanField('одноразовий внесок', default=False)

    def __str__(self):
        return f'{self.participant} на {self.class_unit}'

    @classmethod
    def get_payment_method_expression(cls):
        # TODO maybe use one type: either strig or int
        return models.Case(
            models.When(paid_one_time_price=True, then=models.Value(ONE_TIME_PRICE_LABEL)),
            models.When(paper_used__isnull=False, then=models.F('paper_used__paper')),
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