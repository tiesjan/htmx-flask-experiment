import csv
import sqlite3
import uuid

from flask import abort, g


DATABASE = f'/tmp/contacts.{uuid.uuid4()}.db'
PAGE_SIZE = 20


def _get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


def _close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    # Add teardown context
    app.teardown_appcontext(_close_db)

    # Create database schema
    connection = _get_db()
    cursor = connection.cursor()
    cursor.execute(
        '''
        CREATE TABLE contacts (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email_address TEXT NOT NULL,
            gender TEXT NOT NULL
        );
        '''
    )

    # Insert initial data from CSV file
    with open('contacts.csv', 'r') as contacts_csv:
        cursor.executemany(
            '''
            INSERT INTO contacts (first_name, last_name, email_address, gender)
            VALUES (:first_name, :last_name, :email_address, :gender);
            ''',
            csv.DictReader(contacts_csv)
        )
        connection.commit()

    cursor.close()


# Multiple contacts
def get_contacts(query=None, gender=None, page=1):
    where_clauses = []
    parameters = {}

    # Narrow down results by search query, if given
    if query is not None:
        where_clause = '({})'.format(
            ' OR '.join([
                f'LOWER({field}) LIKE (\'%\' || LOWER(:query) || \'%\')'
                for field in ('first_name', 'last_name', 'email_address')
            ])
        )
        where_clauses.append(where_clause)
        parameters['query'] = query

    # Narrow down results by gender, if given
    if gender is not None:
        where_clause = 'UPPER(gender) = UPPER(:gender)'
        where_clauses.append(where_clause)
        parameters['gender'] = gender

    # Construct SQL WHERE clause
    if where_clauses:
        sql_where_clause = 'WHERE {}'.format(' AND '.join(where_clauses))
    else:
        sql_where_clause = ''

    # Construct SQL LIMIT OFFSET clause for pagination
    parameters['limit'] = PAGE_SIZE
    parameters['offset'] = PAGE_SIZE * (page - 1)
    sql_limit_offset_clause = 'LIMIT :limit OFFSET :offset'

    # Query contacts
    connection = _get_db()
    cursor = connection.cursor()
    results = cursor.execute(
        f'''
        SELECT id, first_name, last_name, email_address, gender
        FROM contacts
        {sql_where_clause}
        ORDER BY first_name, last_name
        {sql_limit_offset_clause};
        ''',
        parameters
    )
    contacts = results.fetchall()

    # Determine next page number, if available
    parameters['limit'] += 1
    count_result = cursor.execute(
        f'''
        SELECT COUNT(id) AS num_contacts
        FROM contacts
        {sql_where_clause};
        ''',
        parameters
    ).fetchone()
    if count_result['num_contacts'] > (PAGE_SIZE * page):
        next_page = page + 1
    else:
        next_page = None

    return contacts, next_page


# Single contact
def _get_contact(pk):
    connection = _get_db()
    cursor = connection.cursor()
    results = cursor.execute(
        '''
        SELECT id, first_name, last_name, email_address, gender
        FROM contacts
        WHERE id = :pk;
        ''',
        {'pk': pk}
    )
    return results.fetchone()


def get_contact_or_404(pk):
    # Retrieve contact for given primary key, or abort request if not found
    contact = _get_contact(pk)
    if contact is None:
        abort(404, 'Unable to find contact. Perhaps it was removed?')
    return contact


def create_contact(first_name, last_name, email_address, gender):
    # Insert contact into database
    connection = _get_db()
    cursor = connection.cursor()
    cursor.execute(
        '''
        INSERT INTO contacts (first_name, last_name, email_address, gender)
        VALUES (:first_name, :last_name, :email_address, :gender)
        ''',
        {
            'first_name': first_name, 'last_name': last_name,
            'email_address': email_address, 'gender': gender,
        }
    )
    connection.commit()

    # Retrieve new contact from database and return
    contact_pk = cursor.lastrowid
    return _get_contact(contact_pk)


def update_contact(pk, first_name, last_name, email_address, gender):
    # Update contact in database
    connection = _get_db()
    cursor = connection.cursor()
    cursor.execute(
        '''
        UPDATE contacts
        SET
            first_name = :first_name, last_name = :last_name,
            email_address = :email_address, gender = :gender
        WHERE id = :pk;
        ''',
        {
            'first_name': first_name, 'last_name': last_name,
            'email_address': email_address, 'gender': gender,
            'pk': pk,
        }
    )
    connection.commit()

    # Retrieve updated contact from database and return
    return _get_contact(pk)


def delete_contact(pk):
    # Delete contact from database
    connection = _get_db()
    cursor = connection.cursor()
    cursor.execute(
        'DELETE FROM contacts WHERE id = :pk;',
        {'pk': pk}
    )
    connection.commit()
