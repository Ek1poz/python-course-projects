from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form including date of birth.
    """

    class Meta(UserCreationForm.Meta):
        """Form metadata options."""
        model = CustomUser
        fields = (UserCreationForm.Meta.fields +
                  ('phone_number', 'date_of_birth'))
        labels = {
            'phone_number': _('Phone number'),
            'date_of_birth': _('Date of birth'),
        }
