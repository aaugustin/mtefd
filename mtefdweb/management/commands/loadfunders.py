import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import Funder


class Command(BaseCommand):
    args = 'path/to/contributions.csv'
    help = "Load a contributions.csv file exported from Indiegogo"

    def handle(self, *args, **options):
        try:
            csv_file = args[0]
        except IndexError:
            raise CommandError("Missing argument: path/to/contributions.csv")

        rev_perk = {v: k for k, v in Funder.PERK_CHOICES}
        rev_appearance = {v: k for k, v in Funder.APPEARANCE_CHOICES}
        count = 0
        with open(csv_file) as csv_handle:
            reader = csv.DictReader(csv_handle)
            with transaction.atomic():
                for row in reader:
                    Funder.objects.create(
                        name=row['Name'],
                        email=row['Email'],
                        perk=rev_perk[row['Perk']],
                        appearance=rev_appearance[row['Appearance']],
                    )
                    count += 1
        self.stdout.write("Imported %d funders." % count)
