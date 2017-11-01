import json
import os

from django.conf import settings
from django.core.management import BaseCommand

from system.models import Person


class Command(BaseCommand):

    def handle(self, *args, **options):
        # This is sample management command
        #
        # Do something here
        #
        print("This is sample management command")



