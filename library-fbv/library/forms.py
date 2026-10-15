from django import forms

from .models import Book


class BookModelForm(forms.ModelForm):
    """
    Form for creating and updating Book instances.
    Used by book_create and book_update views.
    """

    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'isbn', 'author', 'publisher',
            'publication_date', 'genre', 'pages', 'summary',
            'cover_image', 'language', 'is_available', 'rating',
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'summary': forms.Textarea(attrs={'rows': 5}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
        labels = {
            'title': 'Book Title',
            'publication_date': 'Date Published',
        }
        help_texts = {
            'rating': 'Rate the book from 1 to 5.',
        }

    def __init__(self, *args, **kwargs):
        # Pop off the user kwarg before calling super() -- Django's Form
        # class has no idea what to do with it.
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Add Bootstrap-style CSS classes to every visible field.
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.HiddenInput):
                continue
            if isinstance(field.widget, forms.CheckboxInput):
                css = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                css = 'form-select'
            else:
                css = 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' ' + css).strip()

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters.')
        return title


class BookSearchForm(forms.Form):
    """
    Form for searching and filtering the book list.
    Bound to request.GET in book_list.
    """
    q = forms.CharField(
        max_length=100,
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, author, or ISBN...',
        })
    )
    genre = forms.ChoiceField(
        choices=[],  # populated in __init__ from Book.GENRE_CHOICES
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort = forms.ChoiceField(
        choices=[
            ('title', 'Title (A-Z)'),
            ('-title', 'Title (Z-A)'),
            ('-rating', 'Highest Rated'),
            ('-publication_date', 'Newest'),
            ('publication_date', 'Oldest'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['genre'].choices = [('', 'All Genres')] + list(Book.GENRE_CHOICES)
