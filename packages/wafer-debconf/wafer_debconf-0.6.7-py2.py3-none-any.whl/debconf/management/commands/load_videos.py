import datetime
from uuid import UUID

from django.core.management.base import BaseCommand

import requests

from wafer.schedule.models import ScheduleItem


class Command(BaseCommand):
    help = 'Load video URLs from sreview.debian.net'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sreview-url', metavar='URL', type=str,
            default='https://sreview.debian.net/released.json',
            help='URL for the released.json file in the SReview instance',
        )

        current_year = datetime.datetime.today().year
        parser.add_argument(
            '--base-url', metavar='URL', type=str,
            default='https://meetings-archive.debian.net/pub/debian-meetings/%s' % current_year,
            help='Base URL for the videos released by sreview',
        )

        parser.add_argument(
            '--dry-run', action='store_true',
            help='Only show what would be done',
        )
        parser.add_argument(
            '--remove-lq', action='store_true',
            help='Strip .lq. from URLs',
        )

    def handle(self, *args, **options):
        jsonurl = options['sreview_url']

        jsondata = requests.get(jsonurl)
        jsondata.raise_for_status()

        data = jsondata.json()

        baseurl = options['base_url'].rstrip("/")
        scheduleitems_by_guid = {}
        for scheduleitem in ScheduleItem.objects.all():
            scheduleitems_by_guid[scheduleitem.guid] = scheduleitem

        for entry in data['videos']:
            talk_guid = UUID(entry['eventid'])
            scheduleitem = scheduleitems_by_guid.get(talk_guid)
            if not scheduleitem:
                print('ScheduleItem <%s> does not exist' % talk_guid)
            talk = scheduleitem.talk
            if talk is None:
                print('ScheduleItem <%s> is not a talk' % talk_guid)
                continue
            url = baseurl + "/" + entry['video'].lstrip("/")
            if options['remove_lq']:
                parts = url.rpartition('.lq.')
                if '.' not in parts[2]:
                    url = parts[0] + '.' + parts[2]
            if options['dry_run']:
                print('Would load video for <%s>: %s' % (talk, url))
            else:
                talk.urls.update_or_create(
                    description='Video',
                    defaults={
                        "url": url,
                    }
                )
                print('Loaded video for <%s>: %s' % (talk, url))
