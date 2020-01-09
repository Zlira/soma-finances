from django.forms import ModelForm, IntegerField

from .models import ParticipantPaper


class AddParticipantPaperForm(ModelForm):
    внесок = IntegerField()

    class Meta:
        model = ParticipantPaper
        fields = '__all__'
