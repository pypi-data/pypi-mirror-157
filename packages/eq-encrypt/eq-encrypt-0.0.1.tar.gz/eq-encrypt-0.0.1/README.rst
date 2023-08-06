=====
eq-encrypt version 0.0.1
=====

'eq-encrypt' is a Django reusable app to help you encrypt passwords.


Quick start
-----------
1. pip install eq-encrypt==<version>
2. Add "eq-encrypt" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        'eq-encrypt',
    ]

And that's all.

Usage:

Encript:
1. Run ./manage.py encrypt <password>
    It will display the encrypted result in command window.

Decript:
1. Run ./manage.py decrypt <encrypted password>
    It will display the decrypted result in command window.
