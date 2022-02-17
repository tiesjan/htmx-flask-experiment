import functools
import random
import secrets
import string
import time

from flask import Flask, abort, g, render_template, redirect, request, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import HTTPException

from .db import (
    create_contact, delete_contact, get_contact_or_404, init_db, get_contacts,
    update_contact
)
from .forms import (
    GENDER_OPTIONS, ContactForm, ContactSearchForm, EmailAddressForm
)


# Initialize Flask application
app = Flask(__name__)
app.secret_key = ''.join(
    secrets.choice(string.ascii_letters + string.digits) for _ in range(64)
)


# Enable CSRF protection
csrf = CSRFProtect(app)


# Initialize database
with app.app_context():
    init_db(app)


# Functions to run before each request
@app.before_request
def detect_htmx():
    g.htmx = request.headers.get('HX-Request') == 'true'


# Decorators
def require_htmx(function):
    @functools.wraps(function)
    def check_htmx(*args, **kwargs):
        if g.htmx:
            return function(*args, **kwargs)
        else:
            return abort(403, 'This route may only be accessed from HTMX.')

    return check_htmx


# Exception handler
@app.errorhandler(HTTPException)
def handle_http_exception(exception):
    template = 'partials/exception.html' if g.get('htmx') else 'exception.html'
    return render_template(template, exception=exception), exception.code


# Template filters
@app.template_filter()
def gender_display(gender):
    return dict(GENDER_OPTIONS).get(gender, 'Unknown')


# Routes
@app.route('/', methods=('GET',))
def index():
    return redirect(url_for('contact_list'))


@app.route('/contacts/', methods=('GET', 'POST'))
def contact_list():
    if request.method == 'GET':
        search_form = ContactSearchForm(request.args)

        # Query database
        search_query = search_form.search_query.data
        gender_query = search_form.gender_query.data
        page = search_form.page.data
        contact_list, next_page = get_contacts(search_query, gender_query, page)

        # Return contact details
        context = {
            'contact_list': contact_list,
            'next_page': next_page,
            'search_form': search_form,
        }
        template = 'partials/contact-list.html' if g.htmx else 'contacts.html'

    elif request.method == 'POST':
        # Validate and create contact
        contact_form = ContactForm()
        if contact_form.validate_on_submit():
            contact = create_contact(
                contact_form.data['first_name'], contact_form.data['last_name'],
                contact_form.data['email_address'], contact_form.data['gender'],
            )
            context = {'contact': contact, 'add_contact_list_entry': True}
            template = 'partials/contact-details.html'
        else:
            context = {'contact_form': contact_form}
            template = 'partials/contact-form.html'

    # Spend some extra processing time
    time.sleep(random.randrange(3, 8) / 10.0)

    # Render template and return response
    return render_template(template, **context)


@app.route('/contacts/<int:pk>/', methods=('GET', 'DELETE', 'PUT'))
@require_htmx
def contact_detail(pk):
    contact = get_contact_or_404(pk) if pk else None

    if request.method == 'GET':
        # Return contact details
        context = {'contact': contact}
        template = 'partials/contact-details.html'

    elif request.method == 'DELETE':
        # Delete contact
        delete_contact(pk)
        context = {'contact': contact}
        template = 'partials/contact-deleted.html'

    elif request.method == 'PUT':
        # Validate and update contact
        contact_form = ContactForm(data=contact)
        if contact_form.validate_on_submit():
            contact = update_contact(
                pk,
                contact_form.data['first_name'], contact_form.data['last_name'],
                contact_form.data['email_address'], contact_form.data['gender'],
            )
            context = {'contact': contact, 'update_contact_list_entry': True}
            template = 'partials/contact-details.html'
        else:
            context = {'contact': contact, 'contact_form': contact_form}
            template = 'partials/contact-form.html'

    # Spend some extra processing time
    time.sleep(random.randrange(3, 8) / 10.0)

    # Render template and return response
    return render_template(template, **context)


@app.route('/contacts/add/', methods=('GET',))
@require_htmx
def contact_add_form():
    # Return form for creating new contact
    context = {'contact_form': ContactForm()}
    template = 'partials/contact-form.html'
    return render_template(template, **context)


@app.route('/contacts/<int:pk>/change/', methods=('GET',))
@require_htmx
def contact_change_form(pk):
    # Return form for updating existing contact
    contact = get_contact_or_404(pk)

    context = {'contact_form': ContactForm(data=contact), 'contact': contact}
    template = 'partials/contact-form.html'
    return render_template(template, **context)


@app.route('/validate/email-address/', methods=('POST',))
@require_htmx
def validate_email_address():
    # Validate given email address
    form = EmailAddressForm()

    if not form.validate_on_submit():
        errors = form.email_address.errors
        return render_template('partials/form-errors.html', errors=errors), 400
    else:
        return ''
