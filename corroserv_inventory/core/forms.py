from django import forms
from django.forms import TextInput

from .models import Item, UoM


class ConsumeForm(forms.Form):
    location = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )
    quantity = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )
    # def clean_instructions(self):
    #     instructions = self.cleaned_data["instructions"]
    #     if not instructions:
    #         return instructions

    #     if not instructions[0].isupper():
    #         self.add_error("instructions", "Should start with an uppercase letter")

    #     if instructions.endswith("."):
    #         self.add_error("instructions", "Should not end with a full stop")

    #     return instructions


class InboundForm(forms.Form):
    location = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )
    quantity = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )
    # def clean_instructions(self):
    #     instructions = self.cleaned_data["instructions"]
    #     if not instructions:
    #         return instructions

    #     if not instructions[0].isupper():
    #         self.add_error("instructions", "Should start with an uppercase letter")

    #     if instructions.endswith("."):
    #         self.add_error("instructions", "Should not end with a full stop")

    #     return instructions


class OutboundForm(forms.Form):
    location = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )
    quantity = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )
    # def clean_instructions(self):
    #     instructions = self.cleaned_data["instructions"]
    #     if not instructions:
    #         return instructions

    #     if not instructions[0].isupper():
    #         self.add_error("instructions", "Should start with an uppercase letter")

    #     if instructions.endswith("."):
    #         self.add_error("instructions", "Should not end with a full stop")

    #     return instructions


class CreateItemForm(forms.ModelForm):

    uom = forms.ModelChoiceField(
        queryset=UoM.objects.all(),
        widget=forms.Select(
            attrs={"class": "selectpicker form-control pt-exercise-form-input"}
        ),
    )

    class Meta:
        model = Item
        fields = (
            "name",
            "uom",
            "size",
        )
        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Item name",
                }
            ),
            "size": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Item size",
                }
            ),
        }

    # def clean_instructions(self):
    #     instructions = self.cleaned_data["instructions"]
    #     if not instructions:
    #         return instructions

    #     if not instructions[0].isupper():
    #         self.add_error("instructions", "Should start with an uppercase letter")

    #     if instructions.endswith("."):
    #         self.add_error("instructions", "Should not end with a full stop")

    #     return instructions
