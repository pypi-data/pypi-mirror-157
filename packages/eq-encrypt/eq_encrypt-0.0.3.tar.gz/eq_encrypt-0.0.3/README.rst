=====
eq_encrypt version 0.0.3
=====

'eq_encrypt' is a Django reusable app to help you encrypt passwords.


Quick start
-----------
1. pip install eq_encrypt==<version>
2. Add "eq_encrypt" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        'eq_encrypt',
    ]

And that's all.

Usage:

Encript:
1. Run ./manage.py encrypt <password>
    It will display the encrypted result in command window.
