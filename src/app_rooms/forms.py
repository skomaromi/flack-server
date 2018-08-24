from django import forms
from django.core.exceptions import ValidationError

from .models import Room


class RoomModelForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'

    def clean_participants(self, *args, **kwargs):
        print("RoomModelForm::clean_participants()")
        participants = self.cleaned_data.get('participants')

        if participants.count() < 2:
            raise ValidationError("A room must contain at least 2 participants")

        return self.cleaned_data
