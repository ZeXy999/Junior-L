"""Fill the library with books, copies, covers, readers, reviews and loans.

Usage:
    python manage.py seed_library              # classics + 12 random books
    python manage.py seed_library --extra 30   # more random books
    python manage.py seed_library --reset      # wipe catalog data first
"""
import os
import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify

from catalog.covers import make_cover
from catalog.models import (Author, Book, BookCopy, Genre, Loan, Publisher, Review)

# name, born, died
AUTHORS = {
    "austen": ("Jane", "Austen", 1775, 1817), "shelley": ("Mary", "Shelley", 1797, 1851),
    "stoker": ("Bram", "Stoker", 1847, 1912), "melville": ("Herman", "Melville", 1819, 1891),
    "dickens": ("Charles", "Dickens", 1812, 1870), "wilde": ("Oscar", "Wilde", 1854, 1900),
    "carroll": ("Lewis", "Carroll", 1832, 1898), "stevenson": ("Robert Louis", "Stevenson", 1850, 1894),
    "wells": ("H. G.", "Wells", 1866, 1946), "cbronte": ("Charlotte", "Bront\u00eb", 1816, 1855),
    "ebronte": ("Emily", "Bront\u00eb", 1818, 1848), "dostoevsky": ("Fyodor", "Dostoevsky", 1821, 1881),
    "dumas": ("Alexandre", "Dumas", 1802, 1870), "doyle": ("Arthur Conan", "Doyle", 1859, 1930),
    "conrad": ("Joseph", "Conrad", 1857, 1924), "alcott": ("Louisa May", "Alcott", 1832, 1888),
    "twain": ("Mark", "Twain", 1835, 1910), "verne": ("Jules", "Verne", 1828, 1905),
    "tolstoy": ("Leo", "Tolstoy", 1828, 1910), "hugo": ("Victor", "Hugo", 1802, 1885),
    "london": ("Jack", "London", 1876, 1916), "montgomery": ("L. M.", "Montgomery", 1874, 1942),
    "grahame": ("Kenneth", "Grahame", 1859, 1932), "defoe": ("Daniel", "Defoe", 1660, 1731),
    "swift": ("Jonathan", "Swift", 1667, 1745), "hardy": ("Thomas", "Hardy", 1840, 1928),
}

# title, author key, year, pages, genre, summary
CLASSICS = [
    ("Pride and Prejudice", "austen", 1813, 432, "Romance", "Elizabeth Bennet and the proud Mr Darcy misjudge each other in a sparkling comedy about family, money and first impressions."),
    ("Emma", "austen", 1815, 474, "Romance", "A confident young matchmaker meddles in her friends' love lives and learns how little she understands her own heart."),
    ("Frankenstein", "shelley", 1818, 280, "Gothic & Horror", "A young scientist builds a living creature and then refuses responsibility for it, with tragic results for everyone."),
    ("Dracula", "stoker", 1897, 418, "Gothic & Horror", "Told through letters and diaries, a band of friends hunts the ancient count who has crossed the sea to feed on England."),
    ("Moby-Dick", "melville", 1851, 635, "Adventure", "Captain Ahab's obsessive hunt for the white whale drives a whaling crew toward disaster, narrated by the sailor Ishmael."),
    ("Great Expectations", "dickens", 1861, 505, "Classic Fiction", "Orphan Pip rises from a marsh village to London society and discovers who really paid for his fortune."),
    ("A Tale of Two Cities", "dickens", 1859, 341, "Historical", "Love and sacrifice link London and Paris during the upheaval of the French Revolution."),
    ("The Picture of Dorian Gray", "wilde", 1890, 254, "Gothic & Horror", "A handsome young man stays youthful while his portrait quietly records every one of his sins."),
    ("Alice's Adventures in Wonderland", "carroll", 1865, 192, "Fantasy", "Alice tumbles down a rabbit hole into a world of grinning cats, mad tea parties and playing-card royalty."),
    ("Treasure Island", "stevenson", 1883, 292, "Adventure", "Young Jim Hawkins finds a pirate's map and sails after buried gold with the charming, treacherous Long John Silver."),
    ("Strange Case of Dr Jekyll and Mr Hyde", "stevenson", 1886, 96, "Gothic & Horror", "A respectable doctor's experiment unleashes a darker self that slowly takes over."),
    ("The Time Machine", "wells", 1895, 118, "Science Fiction", "An inventor travels to the year 802,701 and finds humanity split into two very different species."),
    ("The War of the Worlds", "wells", 1898, 192, "Science Fiction", "Martian machines land in Surrey and sweep aside every defence humanity can muster."),
    ("Jane Eyre", "cbronte", 1847, 532, "Romance", "An orphaned governess finds love at Thornfield Hall, but its master hides a terrible secret in the attic."),
    ("Wuthering Heights", "ebronte", 1847, 416, "Gothic & Horror", "On the wild Yorkshire moors, the bond between Heathcliff and Catherine turns into a generations-long feud."),
    ("Crime and Punishment", "dostoevsky", 1866, 551, "Classic Fiction", "A poor student commits a murder he believes is justified, then cannot escape his own conscience."),
    ("The Count of Monte Cristo", "dumas", 1844, 1276, "Adventure", "Wrongly imprisoned Edmond Dant\u00e8s escapes, finds a fortune and plots an elaborate revenge."),
    ("The Adventures of Sherlock Holmes", "doyle", 1892, 307, "Mystery", "Twelve short cases in which the brilliant detective and Dr Watson untangle Victorian London's strangest puzzles."),
    ("The Hound of the Baskervilles", "doyle", 1902, 256, "Mystery", "Holmes investigates a spectral dog said to haunt the Devon moors and stalk the Baskerville family."),
    ("Heart of Darkness", "conrad", 1899, 96, "Classic Fiction", "Marlow's river journey into the African interior to find the enigmatic Kurtz becomes a descent into moral darkness."),
    ("Little Women", "alcott", 1868, 449, "Classic Fiction", "Four sisters grow up in Civil War-era New England, each chasing a very different dream."),
    ("The Adventures of Tom Sawyer", "twain", 1876, 274, "Adventure", "Mischievous Tom whitewashes fences, witnesses a murder and gets lost in a cave along the Mississippi."),
    ("Twenty Thousand Leagues Under the Seas", "verne", 1870, 424, "Science Fiction", "Professor Aronnax is taken aboard Captain Nemo's submarine for a tour of the world's oceans."),
    ("War and Peace", "tolstoy", 1869, 1225, "Historical", "Five aristocratic families live through Napoleon's invasion of Russia in a sweeping panorama of love and war."),
    ("Les Mis\u00e9rables", "hugo", 1862, 1463, "Historical", "Ex-convict Jean Valjean tries to build an honest life while the relentless inspector Javert pursues him."),
    ("The Call of the Wild", "london", 1903, 232, "Adventure", "Buck, a pampered dog, is stolen and sold into the brutal sled-dog teams of the Klondike gold rush."),
    ("Anne of Green Gables", "montgomery", 1908, 320, "Children's", "Imaginative orphan Anne Shirley wins over the Cuthberts and the whole village of Avonlea."),
    ("The Wind in the Willows", "grahame", 1908, 259, "Children's", "Mole, Rat, Badger and the reckless Mr Toad share riverbank adventures."),
    ("Robinson Crusoe", "defoe", 1719, 320, "Adventure", "Shipwrecked on a remote island, Crusoe rebuilds a life through ingenuity and faith."),
    ("Gulliver's Travels", "swift", 1726, 306, "Fantasy", "Lemuel Gulliver visits tiny Lilliput, giant Brobdingnag and stranger lands in a sharp satire of human folly."),
    ("Tess of the d'Urbervilles", "hardy", 1891, 518, "Classic Fiction", "A poor country girl is crushed by fate and Victorian morality in Hardy's tragic masterpiece."),
]

GENRE_NAMES = ["Romance", "Gothic & Horror", "Adventure", "Classic Fiction", "Historical", "Fantasy",
               "Science Fiction", "Mystery", "Children's"]

PUBLISHERS = [("Karoo Press", "Beaufort West"), ("Table Mountain Books", "Cape Town"),
              ("Highveld House", "Johannesburg"), ("Drakensberg & Sons", "Pietermaritzburg"),
              ("Lowveld Editions", "Mbombela"), ("Cape Quill", "Stellenbosch"),
              ("Baobab Publishing", "Polokwane")]

READERS = ["thandi", "sipho", "naledi", "kagiso", "lerato", "themba", "nomsa", "pieter",
           "aisha", "johan", "zanele", "bongani", "refilwe", "dumisani"]

COMMENTS = {
    5: ["Absolutely loved it \u2013 I stayed up far too late finishing it.", "A masterpiece. Every page earns its place.",
        "Brilliant from start to finish; I'll be re-reading this one.", "Beautifully written, and it has aged remarkably well.",
        "One of the best books I've borrowed from this library."],
    4: ["Very good, with a few slow stretches in the middle.", "Great characters and a satisfying ending.",
        "Highly recommended if you enjoy this kind of story.", "A strong read; the prose really carries it.",
        "Worth the two weeks \u2013 I only wish it were shorter."],
    3: ["Decent, but it didn't completely grab me.", "Some wonderful moments, some heavy going.",
        "Interesting ideas, although the pacing dragged for me.", "Glad I read it, though I probably won't return to it."],
    2: ["Hard work. I admired it more than I enjoyed it.", "The setup was promising but I lost interest halfway."],
    1: ["Couldn't finish it, sadly.", "Not for me at all."],
}

ADJ = ["Silent", "Crimson", "Hidden", "Last", "Forgotten", "Golden", "Broken", "Distant", "Burning", "Hollow",
       "Midnight", "Restless", "Winter", "Wandering", "Secret", "Iron", "Paper", "Salt"]
NOUN = ["Garden", "Lighthouse", "Orchard", "River", "Letter", "Compass", "Kingdom", "Harvest", "Mirror",
        "Station", "Atlas", "Shadow", "Library", "Voyage", "Tide", "Citadel", "Promise", "Archive"]
PLACE = ["Karoo", "Highveld", "Cape", "Veld", "Delta", "Northern Sea", "Old Town", "Valley", "Islands"]
FIRST = ["Amara", "Lindiwe", "Marcus", "Elena", "Tariq", "Hannah", "Pieter", "Naomi", "Oliver", "Sibusiso",
         "Ingrid", "Kofi", "Rosa", "Dmitri", "Yusuf", "Clara"]
LAST = ["Mokoena", "van der Merwe", "Okafor", "Fernandez", "Naidoo", "Whitfield", "Dlamini", "Kowalski",
        "Abrahams", "Nkosi", "Lindqvist", "Botha", "Haddad", "Pretorius", "Moyo", "Sutherland"]
SUMMARY_BY_GENRE = {
    "Romance": "Two people who should never have met are drawn together, and must decide what they are willing to risk for love.",
    "Gothic & Horror": "A crumbling house, a whispered rumour and a secret that someone would kill to keep buried.",
    "Adventure": "A reckless journey across unforgiving country where one wrong decision could cost the whole expedition.",
    "Classic Fiction": "A quiet, deeply observed story of family, duty and the choices that shape a life.",
    "Historical": "Ordinary lives collide with extraordinary events in a vividly imagined past.",
    "Fantasy": "A reluctant hero discovers that the old stories were true and the kingdom needs them now.",
    "Science Fiction": "A discovery at the edge of the solar system forces humanity to rethink everything it believed.",
    "Mystery": "A body, a locked room and a detective who notices exactly the detail everyone else missed.",
    "Children's": "A curious young hero and some unlikely friends set out to put things right.",
}


class Command(BaseCommand):
    help = "Seed the library with random books, covers, readers, reviews and loans."

    def add_arguments(self, parser):
        parser.add_argument("--extra", type=int, default=12, help="Number of extra randomly generated books.")
        parser.add_argument("--reset", action="store_true", help="Delete existing catalog data first.")
        parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible data.")
        parser.add_argument("--no-covers", action="store_true", help="Skip cover image generation.")

    @transaction.atomic
    def handle(self, *args, **opts):
        rng = random.Random(opts["seed"])
        if opts["reset"]:
            Loan.objects.all().delete()
            Review.objects.all().delete()
            Book.objects.all().delete()
            Author.objects.all().delete()
            Publisher.objects.all().delete()
            Genre.objects.all().delete()
            User.objects.filter(username__in=READERS).delete()
            self.stdout.write("Existing catalog data removed.")

        genres = {n: Genre.objects.get_or_create(name=n, defaults={"slug": slugify(n)})[0] for n in GENRE_NAMES}
        publishers = [Publisher.objects.get_or_create(name=n, defaults={"city": c})[0] for n, c in PUBLISHERS]
        authors = {k: Author.objects.get_or_create(first_name=f, last_name=l,
                                                   defaults={"birth_year": b, "death_year": d,
                                                             "bio": f"{f} {l} ({b}\u2013{d}) is among the best-loved authors of the classic canon."})[0]
                   for k, (f, l, b, d) in AUTHORS.items()}

        books = []
        for title, akey, year, pages, gname, summary in CLASSICS:
            if Book.objects.filter(title=title).exists():
                continue
            books.append(self._make_book(rng, title, [authors[akey]], year, pages, genres[gname],
                                         summary, rng.choice(publishers)))

        for _ in range(opts["extra"]):
            gname = rng.choice(GENRE_NAMES)
            title = rng.choice([f"The {rng.choice(ADJ)} {rng.choice(NOUN)}",
                                f"{rng.choice(NOUN)} of the {rng.choice(ADJ)} {rng.choice(PLACE)}",
                                f"{rng.choice(ADJ)} {rng.choice(NOUN)}"])
            if Book.objects.filter(title=title).exists():
                continue
            first, last = rng.choice(FIRST), rng.choice(LAST)
            author, _ = Author.objects.get_or_create(
                first_name=first, last_name=last,
                defaults={"birth_year": rng.randint(1940, 1992),
                          "bio": f"{first} {last} writes contemporary fiction."})
            books.append(self._make_book(rng, title, [author], rng.randint(1950, 2024), rng.randint(140, 640),
                                         genres[gname], SUMMARY_BY_GENRE[gname], rng.choice(publishers)))

        readers = []
        for name in READERS:
            user, created = User.objects.get_or_create(username=name, defaults={"email": f"{name}@example.com"})
            if created:
                user.set_unusable_password()
                user.save()
            readers.append(user)

        reviews = loans = 0
        for book in books:
            quality = rng.uniform(3.0, 4.8)
            for user in rng.sample(readers, rng.randint(2, 9)):
                rating = max(1, min(5, round(rng.gauss(quality, 0.9))))
                Review.objects.get_or_create(book=book, user=user, defaults={
                    "rating": rating, "comment": rng.choice(COMMENTS[rating]),
                    "created_at": timezone.now() - timedelta(days=rng.randint(1, 400))})
                reviews += 1

        # historical (returned) loans and some active ones, a few overdue
        copies = list(BookCopy.objects.filter(book__in=books))
        for copy in rng.sample(copies, min(len(copies), 40)):
            user = rng.choice(readers)
            start = timezone.now() - timedelta(days=rng.randint(20, 200))
            Loan.objects.create(copy=copy, user=user, borrowed_at=start,
                                due_date=(start + timedelta(days=14)).date(),
                                returned_at=start + timedelta(days=rng.randint(3, 16)))
            loans += 1
        busy = set()
        for copy in rng.sample(copies, min(len(copies), max(8, len(copies) // 6))):
            if copy.is_available and copy.pk not in busy:
                user = rng.choice(readers)
                if Loan.objects.filter(user=user, copy__book=copy.book, returned_at__isnull=True).exists():
                    continue
                days_ago = rng.randint(0, 24)
                start = timezone.now() - timedelta(days=days_ago)
                Loan.objects.create(copy=copy, user=user, borrowed_at=start,
                                    due_date=(start + timedelta(days=14)).date())
                busy.add(copy.pk)
                loans += 1

        admin_msg = ""
        if not User.objects.filter(username="junior").exists():
            password = os.environ.get("LIBRARY_ADMIN_PASSWORD") or get_random_string(14)
            User.objects.create_superuser("junior", "junior@example.com", password)
            admin_msg = f"\nAdmin account created -> username: junior  password: {password}"

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(books)} books, {len(readers)} readers, {reviews} reviews, {loans} loans.{admin_msg}"))

    def _make_book(self, rng, title, book_authors, year, pages, genre, summary, publisher):
        isbn = "978" + "".join(str(rng.randint(0, 9)) for _ in range(10))
        while Book.objects.filter(isbn=isbn).exists():
            isbn = "978" + "".join(str(rng.randint(0, 9)) for _ in range(10))
        book = Book.objects.create(title=title, isbn=isbn, publication_year=year, pages=pages,
                                   genre=genre, summary=summary, publisher=publisher)
        book.authors.set(book_authors)
        for number in range(1, rng.randint(2, 4) + 1):
            BookCopy.objects.create(book=book, copy_number=number, condition=rng.choice("EGGGF"),
                                    shelf=f"{genre.name[0]}-{rng.randint(1, 12)}{rng.choice('ABC')}")
        names = ", ".join(a.full_name for a in book_authors)
        data = make_cover(title, names, genre.name, seed_key=isbn)
        book.cover.save(f"{slugify(title)[:60]}.jpg", ContentFile(data), save=True)
        return book
