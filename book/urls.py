from django.urls import path, include
from rest_framework.routers import SimpleRouter
from book.views import(
    BookListView,
    BookDetailApi,
    CategoryList,
    contact,
)

urlpatterns = [
    path('',          BookListView.as_view(),  name='book list'),
    path('<int:pk>/', BookDetailApi.as_view(), name='book detail'),
    path('category/', CategoryList.as_view(),  name='book category'),
    path('contact/',  contact,                 name='contact')
]