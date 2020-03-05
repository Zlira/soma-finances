from datetime import date

from django.forms import Form, ModelForm, DateField, \
    IntegerField, ValidationError
from django.contrib.admin.widgets import AdminDateWidget

from .models import ParticipantPaper, Paper, Donation, \
    ClassParticipation


class DateRangeForm(Form):
    start_date = DateField(
        label='початок періоду',
        widget=AdminDateWidget(),
    )
    end_date = DateField(
        label="кінець періоду",
        widget=AdminDateWidget(),
    )


class ClassParticipationForm(ModelForm):
    class Meta:
        model = ClassParticipation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        paper_used = cleaned_data.get('paper_used')
        paid_one_time_price = cleaned_data['paid_one_time_price']

        # exactly one payment method
        if paper_used and paid_one_time_price:
            raise ValidationError(
                'Учасни_ця не може використати папірець і заплатити одноразову ціну одночасно',
                code='invalid'
            )

        if not paper_used and not paid_one_time_price:
            raise ValidationError(
                'Учасни_ця мусить використати папірець або заплатити одноразову ціну',
                code='invalid'
            )

        # this is not enforced on DB level
        if not cleaned_data['paper_used'].participant == cleaned_data['participant']:
            raise ValidationError(
                'Використаний папірець не належить учасни_ці',
                code='invalid'
            )

        return cleaned_data

    def clean_paper_used(self):
        paper_used = self.cleaned_data.get('paper_used')
        class_unit = self.cleaned_data.get('class_unit')
        if not paper_used:
            return paper_used

        if paper_used.is_expired():
            self.add_error(
                'paper_used', 'Використаний папіерць протермінований',
            )
        if paper_used.is_out_of_uses(for_unit=class_unit):
            self.add_error(
                'paper_used', 'Використання папірця вичерпані',
            )
        return paper_used


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
