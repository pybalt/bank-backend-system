# This is a custom command. You use it through manage.py this way:
"py manage.py fill-data"

from django.core.management.base import BaseCommand
from faker import Faker


class Command(BaseCommand):
    
    help = "This command is to fill the database with dummy data. Just for testing purposes."
    
    def handle(self, *args, **kwargs):
        
        fake = Faker()
        pass