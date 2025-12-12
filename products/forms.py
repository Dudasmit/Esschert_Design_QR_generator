from django import forms

class QRForm(forms.Form):
    barcode_checkbox = forms.BooleanField(label="Штрих код",  required=False)


