import pytest

from my_app.forms import CustomUserCreationForm
from my_app.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


def user_data(**overrides: str) -> dict[str, str]:
    """
    Return valid registration data with optional changes.
    """
    data = {
        'username': 'new-reader',
        'password1': 'SafePassword123!',
        'password2': 'SafePassword123!',
        'phone_number': '+380501234567',
        'date_of_birth': '2000-01-02',
    }
    data.update(overrides)
    return data


def test_registration_form_save() -> None:
    """
    Check that valid registration data creates a user.
    """
    form = CustomUserCreationForm(user_data())
    assert form.is_valid()
    user = form.save()
    assert user.phone_number == '+380501234567'
    assert user.check_password('SafePassword123!')


def test_registration_form_passwords_must_match() -> None:
    """
    Check that the form rejects passwords that do not match.
    """
    form = CustomUserCreationForm(
        user_data(password2='DifferentPassword123!')
    )
    assert not form.is_valid()
    assert 'password2' in form.errors


def test_registration_form_duplicate_username() -> None:
    """
    Check that the form rejects a username already in use.
    """
    UserFactory(username='already-used')
    form = CustomUserCreationForm(user_data(username='already-used'))
    assert not form.is_valid()
    assert 'username' in form.errors


def test_registration_form_duplicate_phone() -> None:
    """
    Check that the form rejects a phone number already in use.
    """
    UserFactory(phone_number='+380501234567')
    form = CustomUserCreationForm(user_data())
    assert not form.is_valid()
    assert 'phone_number' in form.errors


def test_registration_form_optional_fields() -> None:
    """
    Check that phone number and date of birth are optional.
    """
    form = CustomUserCreationForm(
        user_data(phone_number='', date_of_birth='')
    )
    assert form.is_valid()
