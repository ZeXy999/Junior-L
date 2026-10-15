"""Optional: add demo authors, publishers and books so the list, search and pagination have data.

    python manage.py seed_demo            # 30 books
    python manage.py seed_demo --count 45
"""
import random
from datetime import date

from django.core.management.base import BaseCommand

from library.models import Author, Book, Publisher

AUTHORS = [("Jane", "Austen"), ("Mary", "Shelley"), ("Bram", "Stoker"), ("Charles", "Dickens"),
           ("H. G.", "Wells"), ("Arthur Conan", "Doyle"), ("Jules", "Verne"), ("Mark", "Twain"),
           ("Emily", "Bront\u00eb"), ("Herman", "Melville")]
PUBLISHERS = [("Karoo Press", "Beaufort West", "South Africa"), ("Table Mountain Books", "Cape Town", "South Africa"),
              ("Highveld House", "Johannesburg", "South Africa")]
TITLES = ["The Silent Garden", "A Winter Voyage", "The Hollow Crown", "Letters from the Delta", "The Iron Orchard",
          "Midnight at the Station", "The Paper Compass", "Shadows over the Karoo", "The Last Lighthouse",
          "Salt and Starlight", "The Forgotten Archive", "A Crimson Tide", "The Wandering Atlas", "River of Glass",
          "The Burning Library", "Song of the Highveld", "The Distant Citadel", "Harvest of Secrets",
          "The Quiet Mirror", "Beneath the Baobab", "The Golden Promise", "Clockwork Kingdoms",
          "The Cartographer's Daughter", "Windfall", "The Long Dry Season", "Tales from the Lowveld",
          "The Glass Mountain", "Echoes of the Cape", "The Restless Shore", "Ink and Ember",
          "The Salt Road", "A Map of Small Hours", "The Lantern Keepers", "The Ninth Orchard"]


class Command(BaseCommand):
    help = "Create demo authors, publishers and books."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=30)

    def handle(self, *args, **opts):
        rng = random.Random(2024)
        authors = [Author.objects.get_or_create(first_name=f, last_name=l)[0] for f, l in AUTHORS]
        publishers = [Publisher.objects.get_or_create(name=n, defaults={"city": c, "country": k})[0]
                      for n, c, k in PUBLISHERS]
        genres = [g for g, _ in Book.GENRE_CHOICES]
        created = 0
        for i in range(opts["count"]):
            title = TITLES[i % len(TITLES)] + ("" if i < len(TITLES) else f" {i // len(TITLES) + 1}")
            isbn = f"978{rng.randint(10**9, 10**10 - 1)}"
            if Book.objects.filter(title=title).exists() or Book.objects.filter(isbn=isbn).exists():
                continue
            Book.objects.create(
                title=title, isbn=isbn, author=rng.choice(authors), publisher=rng.choice(publishers),
                publication_date=date(rng.randint(1950, 2024), rng.randint(1, 12), rng.randint(1, 28)),
                genre=rng.choice(genres), pages=rng.randint(120, 650),
                summary="A demo book created by seed_demo so the list, search and pagination have something to show.",
                is_available=rng.random() > 0.25, rating=rng.randint(1, 5))
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {created} demo books."))
