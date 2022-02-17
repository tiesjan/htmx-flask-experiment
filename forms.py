import re

from flask_wtf import FlaskForm
from wtforms.fields import (
    EmailField, IntegerField, SearchField, SelectField, StringField
)
from wtforms.validators import InputRequired, NumberRange, Optional, Regexp


GENDER_OPTIONS = (
    ('M', 'Male'),
    ('F', 'Female'),
)


# Filters
def strip_value(value):
    return value.strip() if value is not None else value


def value_or_none(value):
    return value if value else None


# Forms
class EmailAddressForm(FlaskForm):
    email_address = EmailField(
        'Email address',
        filters=[strip_value],
        validators=[
            InputRequired(),
            Regexp(
                r'^[\w\.\-]+@([\w\-]+\.)+[\w\-]{2,}$',
                flags=re.I,
                message='Please enter a valid email address.'
            ),
        ],
    )


class ContactForm(EmailAddressForm):
    first_name = StringField(
        'First name',
        filters=[strip_value],
        validators=[
            InputRequired(),
        ],
    )
    last_name = StringField(
        'Last name',
        filters=[strip_value],
        validators=[
            InputRequired(),
        ],
    )
    gender = SelectField(
        'Gender',
        choices=GENDER_OPTIONS,
        filters=[],
        validators=[
            InputRequired(),
        ],
    )


class ContactSearchForm(FlaskForm):
    search_query = SearchField(
        'Search through your contacts...',
        filters=[strip_value, value_or_none],
        validators=[
            Optional(),
        ],
    )
    gender_query = SelectField(
        'Filter by gender:',
        choices=(('', 'All'),) + GENDER_OPTIONS,
        filters=[strip_value, value_or_none],
        validators=[
            Optional(),
        ],
    )
    page = IntegerField(
        'Page',
        default=1,
        filters=[],
        validators=[
            Optional(),
            NumberRange(min=1, message='Please provide a minimum integer value of 1.')
        ]
    )
