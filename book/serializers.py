from rest_framework.serializers import ModelSerializer, SerializerMethodField
from book.models import Book, Category
from django.contrib.auth import get_user_model

User = get_user_model()

class BookListSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'cost', 'author', 'paid_book')

    paid_book = SerializerMethodField()
    def get_paid_book(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        user = User.objects.filter(id=user.id).first()
        if obj in user.paid_books.all():
            return True
        return False

class BookDetailSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'cost', 'author', 'image')

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')