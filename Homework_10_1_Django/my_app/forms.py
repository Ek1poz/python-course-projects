from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form including date of birth."""

    class Meta(UserCreationForm.Meta):
        """Form metadata options."""
        model = CustomUser
        fields = (UserCreationForm.Meta.fields +
                  ('phone_number', 'date_of_birth'))
