# HTMX &amp; Flask experiment: a simple address book

This experiment comprises a simple address book management site, exploring the
feature set of [HTMX][htmx-site]. The site is backed by the [Flask][flask-site]
web framework and the [WTForms][wtforms-site] form handling library. Visitors
can perform CRUD operations on a preloaded set of fake contacts.

[htmx-site]: https://htmx.org/
[flask-site]: https://flask.palletsprojects.com/
[wtforms-site]: https://wtforms.readthedocs.io/


## Get the site up and running
1. Create and activate a virtual environment:

   ```sh
   $ python3 -m venv venv
   $ source venv/bin/activate
   ```

1. Install the requirements:

   ```sh
   $ pip install -r requirements.txt
   ```

1. Run the Flask development server:

   ```sh
   $ FLASK_ENV=development flask run
   ```


## Screenshot
![Screenshot](/docs/screenshot.png)


## License
The scripts and documentation in this project are released under the
BSD-3-Clause License.
