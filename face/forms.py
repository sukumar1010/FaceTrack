from django import forms

class loginOrRegister(forms.Form):
    email = forms.EmailField(
        label='Enter email'
        
    )
    
    password = forms.CharField(widget=forms.PasswordInput)

    

from django import forms
from django.contrib.auth.password_validation import validate_password

class UpdatePasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter new password"
        }),
        
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm new password"
        }),
        
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password")
        p2 = cleaned_data.get("confirm_password")

        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords do not match")

            
            validate_password(p1)

        return cleaned_data
