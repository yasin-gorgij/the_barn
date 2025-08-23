import hashlib

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from storages.backends.s3boto3 import S3Boto3Storage


class Author(models.Model):
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self))
        super().save(*args, **kwargs)

    name = models.CharField(max_length=255, blank=False, unique=True)
    slug = models.SlugField(blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Category(models.Model):
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self))
        super().save(*args, **kwargs)

    name = models.CharField(max_length=255, blank=False, unique=True)
    slug = models.SlugField(blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Publisher(models.Model):
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self))
        super().save(*args, **kwargs)

    name = models.CharField(max_length=100, blank=False, unique=True)
    slug = models.SlugField(blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Recommender(models.Model):
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self))
        super().save(*args, **kwargs)

    name = models.CharField(max_length=255, blank=False, unique=True)
    slug = models.SlugField(blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self))
        super().save(*args, **kwargs)

    name = models.CharField(max_length=255, blank=False, unique=True)
    slug = models.SlugField(blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Book(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'subtitle', 'edition', 'volume'],
                name='unique_book_name',
            )
        ]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['title']),
            models.Index(fields=['subtitle']),
            models.Index(fields=['publication_year']),
            models.Index(fields=['is_read']),
            models.Index(fields=['is_beta']),
            models.Index(fields=['i_wish_it']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        name = [self.title]
        if self.subtitle:
            name.append(f'- {self.subtitle}')
        if self.edition:
            name.append(f'({self.edition} ed)')
        if self.volume:
            name.append(f'Vol. {self.volume}')

        return ' '.join(name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self))
        super().save(*args, **kwargs)

    title = models.CharField(max_length=255, blank=False)
    subtitle = models.CharField(max_length=255, blank=True)
    edition = models.CharField(max_length=20, blank=True)
    volume = models.CharField(max_length=20, blank=True)
    authors = models.ManyToManyField(Author, related_name='books', blank=True)
    publisher = models.ForeignKey(
        Publisher,
        related_name='books',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    publication_year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(3000)],
        blank=True,
        null=True,
    )
    cover_image = models.ImageField(
        storage=S3Boto3Storage(),
        upload_to='cover_images/',
        blank=True,
        null=True,
    )
    cover_image_thumbnail = ImageSpecField(
        source='cover_image',
        processors=[ResizeToFill(150, 242)],
        format='WEBP',
        options={'quality': 60},
    )
    has_physical_copy = models.BooleanField(default=False)
    is_beta = models.BooleanField(default=False, help_text='Is the book completed or not?')
    is_read = models.BooleanField(default=False, help_text='Did you finish reading this book?')
    i_wish_it = models.BooleanField(default=False)
    read_it_again = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name='books', blank=True)
    categories = models.ManyToManyField(Category, related_name='books', blank=True)
    recommenders = models.ManyToManyField(Recommender, related_name='books', blank=True)
    notes = models.TextField(blank=True)
    slug = models.SlugField(blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Asset(models.Model):
    class Meta:
        ordering = ['file_extension']

    def save(self, *args, **kwargs):
        self.file_extension = self.file.name.split('.')[-1].lower()
        self.file_name = f'{str(self.book)}.{self.file_extension}'
        self.file.seek(0, 2)
        self.file_size = self.file.tell()
        self.file.seek(0)
        self.file_hash = hashlib.blake2b(self.file.read()).hexdigest()
        self.file.seek(0)

        super().save(*args, **kwargs)

    book = models.ForeignKey(
        Book,
        related_name='assets',
        on_delete=models.CASCADE,
    )
    file = models.FileField(storage=S3Boto3Storage(), upload_to='assets/')
    file_name = models.CharField(blank=False)
    file_extension = models.CharField(max_length=10, blank=False)
    file_size = models.PositiveBigIntegerField(blank=False)
    file_hash = models.CharField(max_length=128, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ReadingList(models.Model):
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self))
        super().save(*args, **kwargs)

    name = models.CharField(max_length=255, blank=False, unique=True)
    slug = models.SlugField(blank=False, unique=True)
    books = models.ManyToManyField(Book, through='ReadingListBooks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ReadingListBooks(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE)
