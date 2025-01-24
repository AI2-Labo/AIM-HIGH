from django import forms
from django.forms import ModelForm

from .models import My_Profile_Model

class My_Profile_Form(forms.ModelForm):

    name = forms.CharField(widget=forms.Textarea (attrs={"placeholder":"Please enter your name"}))
    age = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder": "Please enter your age", "type": "number"}))
    learning_topic = forms.CharField(widget=forms.Textarea (attrs={"placeholder":"Please enter what you'd like to learn about"}))
    education_level = forms.ChoiceField(
        choices=My_Profile_Model.education_options,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = My_Profile_Model
        fields = "__all__"