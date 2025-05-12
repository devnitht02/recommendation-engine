from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Updates the vector database'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting vector DB update...")

        from ...services.vectordb_update_service import VectorDbDataService
        VectorDbDataService.start()

        self.stdout.write("Vector DB update completed!")
