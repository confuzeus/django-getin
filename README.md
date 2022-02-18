# Django Getin

Easily turn your app into a private area by requiring users to
have an invitation code before they can register.

**Features:**

- Easy management from the Django admin.
- Or from the CLI with the full fledged interface.
- Integrates with any authentication provider.

## Quick start

Install using pip, preferably inside your virtualenv:

```shell
pip install django-getin
```

Then, add it to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "getin"
]
```

We store invitations in the database, so, you need to apply migrations:

```shell
python manage.py migrate getin
```

## Copyright and License

License is MIT.

Copyright 2022 Josh Michael Karamuth