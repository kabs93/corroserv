from django import forms


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
