from django.core.management.base import BaseCommand, CommandError
from ...encodings import B64Decrypt


class Command(BaseCommand):
    help = 'Desencripta.'
    decoder = B64Decrypt()

    def add_arguments(self, parser):
        parser.add_argument('pwd', type=str)

    def handle(self, *args, **options):
        if options['pwd'] == '':
            raise CommandError('Debe ingresar una clave a desencriptar.')
        return self.decoder.decrypt(options['pwd'])
