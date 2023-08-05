from django.core.management.base import BaseCommand

from jsondataferret import EVENT_MODE_MERGE, EVENT_MODE_REPLACE
from jsondataferret.models import Type
from jsondataferret.pythonapi.newevent import NewEventData, newEvent


class Command(BaseCommand):
    help = "Create Test Records"

    def add_arguments(self, parser):
        parser.add_argument("type_id")

    def handle(self, *args, **options):
        type = Type.objects.get(public_id=options["type_id"])
        if type:
            newEvent(
                [
                    NewEventData(
                        type.public_id,
                        "0",
                        {"status": "DISPUTED"},
                        approved=False,
                        mode=EVENT_MODE_MERGE,
                    )
                ],
                None,
                comment="Make Disputed With Modereration!",
            )
            newEvent(
                [
                    NewEventData(
                        type.public_id,
                        "0",
                        {"status": "DISPUTED"},
                        approved=True,
                        mode=EVENT_MODE_MERGE,
                    )
                ],
                None,
                comment="Make Disputed RIGHT NOW",
            )
