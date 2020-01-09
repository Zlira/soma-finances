from django.forms import ModelForm, IntegerField

from .models import ParticipantPaper


class AddParticipantPaperForm(ModelForm):
    price = IntegerField(label='Внесок')

    class Meta:
        model = ParticipantPaper
        fields = '__all__'