from django.core.management import call_command
from unittest import TestCase


class TestCommand(TestCase):
    def test_command(self):
        call_command("encrypt", pwd='hola')
