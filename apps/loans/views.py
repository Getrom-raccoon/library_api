from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Loan
from .serializers import LoanSerializer

class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.returned:
            return Response({'detail': 'Книга уже возвращена'}, status=status.HTTP_400_BAD_REQUEST)
        instance.returned = True
        instance.book.available_copies += 1
        instance.book.save()
        instance.save()
        return Response({'detail': 'Книга возвращена'}, status=status.HTTP_200_OK)