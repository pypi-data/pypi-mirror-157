from django.core.management.base import BaseCommand

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
                        str(i),
                        {"title": "Lion"},
                        approved=True,
                    )
                    for i in range(0, 2)
                ],
                None,
                comment="2 records attached to this event",
            )
            newEvent(
                [
                    NewEventData(
                        type.public_id,
                        str(i),
                        {"title": "Lion"},
                        approved=True,
                    )
                    for i in range(0, 4)
                ],
                None,
                comment="4 records attached to this event",
            )
            newEvent(
                [
                    NewEventData(
                        type.public_id,
                        str(i),
                        {"title": "Lion"},
                        approved=True,
                    )
                    for i in range(0, 5)
                ],
                None,
                comment="5 records attached to this event",
            )
