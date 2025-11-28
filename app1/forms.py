from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'phone', 'user_type']
