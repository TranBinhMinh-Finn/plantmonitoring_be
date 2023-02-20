from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time


class Command(BaseCommand):
    """ Django command to pause execution until database is available"""
    def handle(self, *args, **kwargs):
        self.stdout.write('waiting for db ...')
        db_conn = None
        c = None
        while not c:
            try:
                # get the database with keyword 'default' from settings.py
                db_conn = connections['default']
                try:
                    c = db_conn.cursor()
                    print(c)
                except OperationalError:
                    self.stdout.write("Database unavailable, waiting 1 second ...")
                    time.sleep(1)
                # prints success messge in green
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second ...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('db available'))