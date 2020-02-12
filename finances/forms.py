from datetime import date

from django.forms import Form, ModelForm, DateField, \
    IntegerField, ValidationError
from django.contrib.admin.widgets import AdminDateWidget

from .models import ParticipantPaper, Paper, Donation


class DateRangeForm(Form):
    start_date = DateField(
        label='початок періоду',
        widget=AdminDateWidget(),
    )
    end_date = DateField(
        label="кінець періоду",
        widget=AdminDateWidget(),
    )


class AddParticipantPaperForm(ModelForm):
    price = IntegerField(label='Внесок')

    class Meta:
        model = ParticipantPaper
        fields = '__all__'

    def clean_price(self):
        # can someone make a donation form volunteer card?
        price = self.cleaned_data['price']
        if self.cleaned_data['is_volunteer']:
            return price
        paper = self.cleaned_data['paper']
        if paper.price > price:
            raise ValidationError(f'мінімальний внесок {paper.price}', code='invalid')
        return price

    def save(self, commit=True):
        instance = super().save(commit)

        # move excess money to donation
        price = self.cleaned_data['price']
        paper = self.cleaned_data['paper']
        donation = 0
        if self.cleaned_data['is_volunteer']:
            donation = price
        else:
            donation = price - paper.price

        # TODO check if all of this happens in one transaction
        if donation > 0:
            donation_source = f'Від {instance.participant.name} (папірець {instance.paper.name})'
            Donation.objects.create(
                amount=donation, date=self.cleaned_data['date_purchased'],
                source=donation_source
            ).save()
        return instance
