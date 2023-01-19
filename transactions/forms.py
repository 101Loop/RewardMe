from django import forms

from transactions.models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["product_type", "invoice_amount", "payment_amount", "payment_type", "note"]

    def clean_invoice_amount(self):
        invoice_amount = self.cleaned_data["invoice_amount"]
        if invoice_amount < 0:
            raise forms.ValidationError("Invoice amount cannot be negative")
        return invoice_amount
