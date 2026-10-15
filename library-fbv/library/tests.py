import io
import shutil
import tempfile
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import get_template
from django.test import TestCase, override_settings
from django.urls import resolve, reverse
from PIL import Image

from .forms import BookModelForm, BookSearchForm
from .models import Author, Book, Publisher

FAST_HASH = ['django.contrib.auth.hashers.MD5PasswordHasher']
PASSWORD = 'pass12345'


def make_book(author, title, isbn, **kw):
    data = dict(title=title, isbn=isbn, author=author, publication_date=date(2000, 1, 1),
                genre='F', pages=100, summary='Summary text', rating=3)
    data.update(kw)
    return Book.objects.create(**data)


def form_data(author, **overrides):
    data = {'title': 'A Brand New Book', 'subtitle': '', 'isbn': '9781111111111', 'author': author.pk,
            'publisher': '', 'publication_date': '2021-05-04', 'genre': 'SF', 'pages': 321,
            'summary': 'A fine summary.', 'language': 'English', 'is_available': 'on', 'rating': 4}
    data.update(overrides)
    return data


@override_settings(PASSWORD_HASHERS=FAST_HASH)
class LibraryTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(first_name='Jane', last_name='Austen')
        cls.author2 = Author.objects.create(first_name='Arthur', last_name='Doyle')
        cls.publisher = Publisher.objects.create(name='Karoo Press')
        cls.owner = User.objects.create_user('owner', password=PASSWORD)
        cls.other = User.objects.create_user('other', password=PASSWORD)
        cls.staff = User.objects.create_user('staff', password=PASSWORD, is_staff=True)
        cls.book = make_book(cls.author, 'Pride and Prejudice', '9780000000001', rating=5,
                             created_by=cls.owner, publisher=cls.publisher)

    def login(self, name):
        self.assertTrue(self.client.login(username=name, password=PASSWORD))


class RouteAndTemplateTests(LibraryTestBase):
    def test_url_table_from_step_7(self):
        expected = {'/books/': 'book_list', '/books/add/': 'book_create', '/books/5/': 'book_detail',
                    '/books/5/edit/': 'book_update', '/books/5/delete/': 'book_delete'}
        for path, view_name in expected.items():
            self.assertEqual(resolve(path).func.__name__, view_name, path)
        self.assertEqual(reverse('library:book-list'), '/books/')
        self.assertEqual(reverse('library:book-detail', args=[5]), '/books/5/')

    def test_every_template_compiles(self):
        for name in ['base.html', 'registration/login.html', 'includes/pagination.html',
                     'library/book_list.html', 'library/book_detail.html', 'library/book_form.html',
                     'library/book_confirm_delete.html']:
            get_template(name)

    def test_root_redirects_to_list(self):
        self.assertRedirects(self.client.get('/'), '/books/', fetch_redirect_response=False)

    def test_no_unrendered_template_syntax_leaks(self):
        self.login('owner')
        urls = [reverse('library:book-list'), reverse('library:book-detail', args=[self.book.pk]),
                reverse('library:book-create'), reverse('library:book-edit', args=[self.book.pk]),
                reverse('library:book-delete', args=[self.book.pk]), reverse('login')]
        for url in urls:
            html = self.client.get(url).content.decode()
            self.assertNotIn('{%', html, url)
            self.assertNotIn('{{', html, url)


class ModelTests(LibraryTestBase):
    def test_str_and_helpers(self):
        self.assertEqual(str(self.author), 'Austen, Jane')
        self.assertEqual(str(self.book), 'Pride and Prejudice')
        self.assertEqual(self.book.full_title(), 'Pride and Prejudice')
        self.book.subtitle = 'A Novel'
        self.assertEqual(self.book.full_title(), 'Pride and Prejudice: A Novel')
        self.assertFalse(self.book.is_recent())
        self.assertEqual(self.book.get_absolute_url(), f'/books/{self.book.pk}/')


class BookListTests(LibraryTestBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        for i in range(14):  # 15 books in total -> 2 pages of 12 + 3
            make_book(cls.author2, f'Filler Book {i:02d}', f'97800000001{i:02d}', rating=1 + i % 5,
                      genre='MYS', publication_date=date(1990 + i, 6, 1))

    def test_list_renders_and_paginates(self):
        r = self.client.get(reverse('library:book-list'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['page_obj']), 12)
        self.assertContains(r, 'Showing 1-12')
        self.assertContains(r, 'of 15 books')
        self.assertContains(r, 'page-link')
        r2 = self.client.get(reverse('library:book-list'), {'page': 2})
        self.assertEqual(len(r2.context['page_obj']), 3)
        self.assertContains(r2, 'Showing 13-15')

    def test_bad_page_numbers_do_not_crash(self):
        url = reverse('library:book-list')
        self.assertEqual(self.client.get(url, {'page': 'abc'}).status_code, 200)
        self.assertEqual(self.client.get(url, {'page': 999}).context['page_obj'].number, 2)

    def test_pagination_links_keep_filters(self):
        r = self.client.get(reverse('library:book-list'), {'genre': 'MYS', 'sort': '-rating', 'page': 1})
        self.assertEqual(r.context['query_params'], 'genre=MYS&sort=-rating')
        self.assertNotIn('page=', r.context['query_params'])
        self.assertContains(r, 'href="?page=2&amp;genre=MYS&amp;sort=-rating"')

    def test_search_by_title_author_and_isbn(self):
        url = reverse('library:book-list')
        self.assertContains(self.client.get(url, {'q': 'pride'}), 'Pride and Prejudice')
        r = self.client.get(url, {'q': 'austen'})
        self.assertEqual([b.pk for b in r.context['page_obj']], [self.book.pk])
        r = self.client.get(url, {'q': '9780000000001'})
        self.assertEqual([b.pk for b in r.context['page_obj']], [self.book.pk])
        self.assertContains(r, 'matching "<strong>9780000000001</strong>"')

    def test_search_is_html_escaped(self):
        r = self.client.get(reverse('library:book-list'), {'q': '<script>alert(1)</script>'})
        self.assertNotContains(r, '<script>alert(1)</script>')
        self.assertContains(r, 'No books found')

    def test_genre_filter(self):
        r = self.client.get(reverse('library:book-list'), {'genre': 'F'})
        self.assertEqual([b.pk for b in r.context['page_obj']], [self.book.pk])

    def test_sorting(self):
        url = reverse('library:book-list')
        titles = lambda r: [b.title for b in r.context['page_obj']]
        self.assertEqual(titles(self.client.get(url, {'sort': 'title'}))[0], 'Filler Book 00')
        self.assertEqual(titles(self.client.get(url, {'sort': '-title'}))[0], 'Pride and Prejudice')
        self.assertEqual(self.client.get(url, {'sort': '-rating'}).context['page_obj'][0].rating, 5)
        newest = self.client.get(url, {'sort': '-publication_date'}).context['page_obj'][0]
        self.assertEqual(newest.title, 'Filler Book 13')
        oldest = self.client.get(url, {'sort': 'publication_date'}).context['page_obj'][0]
        self.assertEqual(oldest.title, 'Filler Book 00')  # 1990 is the earliest date in this fixture

    def test_invalid_sort_falls_back_to_title(self):
        r = self.client.get(reverse('library:book-list'), {'sort': 'DROP TABLE'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['page_obj'][0].title, 'Filler Book 00')

    def test_empty_result_message(self):
        self.assertContains(self.client.get(reverse('library:book-list'), {'q': 'zzzzzz'}), 'No books found')

    def test_search_form_choices(self):
        form = BookSearchForm()
        self.assertEqual(form.fields['genre'].choices[0], ('', 'All Genres'))
        self.assertEqual(len(form.fields['genre'].choices), len(Book.GENRE_CHOICES) + 1)


class BookDetailTests(LibraryTestBase):
    def test_detail_page(self):
        r = self.client.get(reverse('library:book-detail', args=[self.book.pk]))
        self.assertContains(r, 'Pride and Prejudice')
        self.assertContains(r, 'Austen, Jane')
        self.assertContains(r, 'Fiction')  # get_genre_display
        self.assertContains(r, 'Available')

    def test_unavailable_badge(self):
        self.book.is_available = False
        self.book.save()
        self.assertContains(self.client.get(self.book.get_absolute_url()), 'Unavailable')

    def test_404(self):
        self.assertEqual(self.client.get(reverse('library:book-detail', args=[9999])).status_code, 404)

    def test_similar_books_same_genre_best_rated_first_max_four(self):
        for i in range(6):
            make_book(self.author2, f'Sibling {i}', f'97811111111{i:02d}', rating=1 + i % 5, genre='F')
        make_book(self.author2, 'Other Genre', '9782222222222', genre='SF', rating=5)
        similar = list(self.client.get(self.book.get_absolute_url()).context['similar_books'])
        self.assertEqual(len(similar), 4)
        self.assertNotIn(self.book, similar)
        self.assertTrue(all(b.genre == 'F' for b in similar))
        self.assertEqual([b.rating for b in similar], sorted([b.rating for b in similar], reverse=True))

    def test_edit_delete_buttons_only_when_logged_in(self):
        url = self.book.get_absolute_url()
        self.assertNotContains(self.client.get(url), '/edit/')
        self.login('owner')
        r = self.client.get(url)
        self.assertContains(r, f'/books/{self.book.pk}/edit/')
        self.assertContains(r, f'/books/{self.book.pk}/delete/')


class BookCreateTests(LibraryTestBase):
    def test_login_required(self):
        url = reverse('library:book-create')
        r = self.client.get(url)
        self.assertRedirects(r, f'/accounts/login/?next={url}', fetch_redirect_response=False)
        self.assertEqual(self.client.post(url, form_data(self.author)).status_code, 302)
        self.assertEqual(Book.objects.count(), 1)

    def test_get_shows_empty_form(self):
        self.login('owner')
        r = self.client.get(reverse('library:book-create'))
        self.assertContains(r, 'Add a Book')
        self.assertContains(r, 'Create Book')
        self.assertContains(r, 'multipart/form-data')
        self.assertContains(r, 'form-control')
        self.assertContains(r, 'form-select')

    def test_valid_post_creates_book_sets_creator_and_flashes_message(self):
        self.login('owner')
        r = self.client.post(reverse('library:book-create'), form_data(self.author), follow=True)
        book = Book.objects.get(isbn='9781111111111')
        self.assertEqual(book.created_by, self.owner)
        self.assertRedirects(r, book.get_absolute_url())
        self.assertContains(r, '&quot;A Brand New Book&quot; was added to the library.')
        self.assertContains(r, 'alert-success')

    def test_invalid_post_rerenders_with_errors_and_bootstrap_danger_alert(self):
        self.login('owner')
        r = self.client.post(reverse('library:book-create'), form_data(self.author, title='Ab'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Title must be at least 3 characters.')
        self.assertContains(r, 'Please correct the errors below.')
        self.assertContains(r, 'alert-danger')   # not the non-existent "alert-error"
        self.assertNotContains(r, 'alert-error')
        self.assertEqual(Book.objects.count(), 1)

    def test_duplicate_isbn_is_a_form_error_not_a_server_error(self):
        self.login('owner')
        r = self.client.post(reverse('library:book-create'), form_data(self.author, isbn='9780000000001'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'already exists')

    def test_isbn_field_is_on_the_form(self):
        # Without it, every book saved through the form would get isbn='' and the 2nd one would crash.
        self.assertIn('isbn', BookModelForm().fields)
        self.login('owner')
        for i in range(2):
            self.client.post(reverse('library:book-create'),
                             form_data(self.author, title=f'Book number {i}', isbn=f'97833333333{i:02d}'))
        self.assertEqual(Book.objects.filter(title__startswith='Book number').count(), 2)

    def test_rating_must_be_1_to_5(self):
        self.login('owner')
        for bad in (0, 6):
            r = self.client.post(reverse('library:book-create'), form_data(self.author, rating=bad))
            self.assertEqual(r.status_code, 200)
        self.assertEqual(Book.objects.count(), 1)

    def test_cover_image_upload(self):
        buf = io.BytesIO()
        Image.new('RGB', (40, 60), 'teal').save(buf, format='PNG')
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        with override_settings(MEDIA_ROOT=tmp):
            self.login('owner')
            data = form_data(self.author, isbn='9784444444444')
            data['cover_image'] = SimpleUploadedFile('cover.png', buf.getvalue(), content_type='image/png')
            self.client.post(reverse('library:book-create'), data)
            book = Book.objects.get(isbn='9784444444444')
            self.assertTrue(book.cover_image.name.startswith('covers/'))
            self.assertContains(self.client.get(book.get_absolute_url()), book.cover_image.url)


class BookUpdateTests(LibraryTestBase):
    def url(self):
        return reverse('library:book-edit', args=[self.book.pk])

    def test_login_required(self):
        self.assertEqual(self.client.get(self.url()).status_code, 302)

    def test_owner_sees_prefilled_form(self):
        self.login('owner')
        r = self.client.get(self.url())
        self.assertContains(r, 'Save Changes')
        self.assertContains(r, 'value="Pride and Prejudice"')
        self.assertContains(r, 'value="2000-01-01"')   # date input pre-fill works for type=date
        self.assertContains(r, 'Cancel')

    def test_owner_can_update(self):
        self.login('owner')
        r = self.client.post(self.url(), form_data(self.author, title='Pride & Prejudice', isbn=self.book.isbn),
                             follow=True)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Pride & Prejudice')
        self.assertContains(r, 'was updated.')

    def test_other_user_is_forbidden(self):
        self.login('other')
        self.assertEqual(self.client.get(self.url()).status_code, 403)
        self.assertEqual(self.client.post(self.url(), form_data(self.author, isbn=self.book.isbn)).status_code, 403)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Pride and Prejudice')

    def test_staff_can_update_anyones_book(self):
        self.login('staff')
        self.assertEqual(self.client.get(self.url()).status_code, 200)

    def test_invalid_update_keeps_original(self):
        self.login('owner')
        r = self.client.post(self.url(), form_data(self.author, title='x', isbn=self.book.isbn))
        self.assertEqual(r.status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Pride and Prejudice')

    def test_missing_book_404(self):
        self.login('owner')
        self.assertEqual(self.client.get(reverse('library:book-edit', args=[9999])).status_code, 404)


class BookDeleteTests(LibraryTestBase):
    def url(self):
        return reverse('library:book-delete', args=[self.book.pk])

    def test_login_required(self):
        self.assertEqual(self.client.post(self.url()).status_code, 302)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_get_shows_confirmation_and_does_not_delete(self):
        self.login('owner')
        r = self.client.get(self.url())
        self.assertContains(r, 'Delete "Pride and Prejudice"?')
        self.assertContains(r, 'This action cannot be undone.')
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_post_deletes_and_redirects_to_list(self):
        self.login('owner')
        r = self.client.post(self.url(), follow=True)
        self.assertRedirects(r, reverse('library:book-list'))
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())
        self.assertContains(r, 'was removed from the library.')

    def test_other_user_forbidden(self):
        self.login('other')
        self.assertEqual(self.client.post(self.url()).status_code, 403)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_staff_can_delete(self):
        self.login('staff')
        self.client.post(self.url())
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

    def test_book_without_creator_is_editable_only_by_staff(self):
        orphan = make_book(self.author, 'Orphan Book', '9785555555555')
        self.login('other')
        self.assertEqual(self.client.get(reverse('library:book-edit', args=[orphan.pk])).status_code, 403)
        self.login('staff')
        self.assertEqual(self.client.get(reverse('library:book-edit', args=[orphan.pk])).status_code, 200)

    def test_deleting_the_creator_keeps_the_book(self):
        self.owner.delete()
        self.book.refresh_from_db()
        self.assertIsNone(self.book.created_by)


class OptionalAjaxTests(LibraryTestBase):
    def test_search_needs_two_characters(self):
        r = self.client.get(reverse('library:book-search-ajax'), {'q': 'p'})
        self.assertEqual(r.json(), {'results': []})

    def test_search_by_title_and_author_last_name(self):
        url = reverse('library:book-search-ajax')
        self.assertEqual(self.client.get(url, {'q': 'Pride'}).json()['results'],
                         [{'id': self.book.pk, 'title': 'Pride and Prejudice', 'author': 'Austen, Jane'}])
        self.assertEqual(len(self.client.get(url, {'q': 'Austen'}).json()['results']), 1)
        self.assertEqual(self.client.get(url, {'q': 'nothing-matches'}).json()['results'], [])

    def test_search_returns_at_most_ten(self):
        for i in range(12):
            make_book(self.author2, f'Many Match {i}', f'97866666666{i:02d}')
        self.assertEqual(len(self.client.get(reverse('library:book-search-ajax'), {'q': 'Many'}).json()['results']), 10)

    def test_toggle_availability(self):
        url = reverse('library:book-toggle-availability', args=[self.book.pk])
        self.assertEqual(self.client.get(url).status_code, 405)           # @require_POST is outermost: GET is refused first
        self.login('other')
        self.assertEqual(self.client.get(url).status_code, 405)           # POST only
        r = self.client.post(url)
        self.assertEqual(r.json(), {'success': True, 'is_available': False})
        self.book.refresh_from_db()
        self.assertFalse(self.book.is_available)
        self.assertEqual(self.client.post(url).json()['is_available'], True)

    def test_toggle_requires_login(self):
        url = reverse('library:book-toggle-availability', args=[self.book.pk])
        self.assertEqual(self.client.post(url).status_code, 302)
        self.book.refresh_from_db()
        self.assertTrue(self.book.is_available)


class AuthFlowTests(LibraryTestBase):
    def test_login_page_and_login_flow(self):
        self.assertContains(self.client.get(reverse('login')), 'Login')
        r = self.client.post(reverse('login'), {'username': 'owner', 'password': PASSWORD, 'next': '/books/add/'})
        self.assertRedirects(r, '/books/add/')

    def test_wrong_password_shows_error(self):
        r = self.client.post(reverse('login'), {'username': 'owner', 'password': 'nope'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'text-danger')

    def test_nav_shows_login_or_user(self):
        self.assertContains(self.client.get(reverse('library:book-list')), 'Login')
        self.login('owner')
        r = self.client.get(reverse('library:book-list'))
        self.assertContains(r, 'Add Book')
        self.assertContains(r, 'owner')
        self.assertContains(r, 'Logout')

    def test_logout(self):
        self.login('owner')
        r = self.client.post(reverse('logout'))
        self.assertRedirects(r, reverse('library:book-list'))
        self.assertNotIn('_auth_user_id', self.client.session)


@override_settings(PASSWORD_HASHERS=FAST_HASH)
class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('root', 'r@example.com', PASSWORD)
        cls.author = Author.objects.create(first_name='Jane', last_name='Austen')
        cls.book = make_book(cls.author, 'Emma', '9780000000009')

    def test_admin_pages_load(self):
        self.client.force_login(self.admin)
        for url in ['/admin/', '/admin/library/book/', '/admin/library/author/', '/admin/library/publisher/',
                    '/admin/library/book/add/', f'/admin/library/book/{self.book.pk}/change/',
                    f'/admin/library/author/{self.author.pk}/change/', '/admin/library/publisher/add/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_admin_actions(self):
        self.client.force_login(self.admin)
        url = '/admin/library/book/'
        self.client.post(url, {'action': 'mark_as_unavailable', '_selected_action': [self.book.pk]})
        self.book.refresh_from_db()
        self.assertFalse(self.book.is_available)
        self.client.post(url, {'action': 'increase_rating', '_selected_action': [self.book.pk]})
        self.book.refresh_from_db()
        self.assertEqual(self.book.rating, 4)
