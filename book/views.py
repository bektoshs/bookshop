from rest_framework import status
# from rest_framework.viewsets import ModelViewSet
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render
from rest_framework.permissions import(
    IsAdminUser,
    AllowAny,
)
from rest_framework.validators import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from book.models import(
    Book,
    Category,
)
from book.serializers import(
    BookListSerializer,
    BookDetailSerializer,
    CategorySerializer
)
from .paginations import DefaultLimitOffSetPagination
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import generics

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all().order_by('-cost')
    serializer_class = BookListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Book.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(title__icontains=query) |
                Q(category__category__icontains=query)


            ).distinct()
        return queryset_list

"""
# class BookModelViewSet(ModelViewSet):
#     queryset = Book.objects.all().order_by('-cost')
#     serializer_class = BookListSerializer
    
#     def get_permissions(self):
#         if self.action in ("get", "retrieve", "list"):
#             permission_classes = [AllowAny, ]
#         else:
#             permission_classes = [IsAdminUser, ]
#         return [perm() for perm in permission_classes]

#     def get_serializer_class(self):
#         if self.action == "retrieve":
#             serializer_class = BookListSerializer
#         else:
#             serializer_class = BookListSerializer
#         return serializer_class

#     def get_queryset(self):
#         user = self.request.user
#         return Book.objects.filter(book=user)

"""
class BookDetailApi(APIView):
    serializer_class = BookDetailSerializer
    pagination_class = DefaultLimitOffSetPagination
    queryset = Book.objects.all()

    """
    get:
    Return a cutomer instance
    
    delete:
    Remove an existing customer
    
    put:
    Update a customer
    """
    
    def get_object(self, pk, request):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Response({'message': 'Not found'},
                            status = status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        """
        request user will get own flows 
        """
        queryset = Book.objects.filter()
        paginator = DefaultLimitOffSetPagination()
        return paginator.generate_response(queryset, BookListSerializer, request)

    def put(self, request, pk):
        detail = self.get_object(pk)
        serializer = Book(detail,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        try:
            query = Book.objects.get(id=pk)
        except:
            raise ValidationError('NOtification was not found')
        serializer = BookListSerializer(instance=query, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'Message': 'Book was updated',
                         'Section': serializer.data},
                         status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        flow = Book.objects.get(id=pk)
        flow.delete()
        return Response({'message': 'Deleted'}, status=status.HTTP_202_ACCEPTED)


class CategoryList(APIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = DefaultLimitOffSetPagination

def contact(request, *args, **kwargs):
    if request.method == 'POST':
        user = request.user
        if not user.paid_books:
            user.paid_true = True
            user.save()
            name = request.POST.get('full-name')
            email = request.POST.get('email')
            aubject = request.POST.get('subject')
            message = request.POST.get('message')
            data = {
                'name': name,
                'email': email,
                'subject': aubject,
                'message': message
            }
            message = '''
                    New message: {}

                    From: {}
                    '''.format(data['message'], data['email'])
            send_mail(data['subject'], message, '', [user.email])
        return HttpResponse('Rahmat')
    return render(request, 'contact/index.html', {})



