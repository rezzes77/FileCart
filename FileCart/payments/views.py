from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import Transaction
from .serializers import TopUpSerializer, ConfirmTransactionSerializer
from .services import process_top_up
from users.models import Profile


class TopUpBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TopUpSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            transaction = serializer.save()
            return Response({
                "message": f"Код подтверждения отправлен на {serializer.validated_data['phone']}",
                "transaction_id": transaction.id
            }, status=201)
        return Response(serializer.errors, status=400)


class ConfirmTopUpView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, id=transaction_id, profile=request.user.profile)
        serializer = ConfirmTransactionSerializer(data=request.data)

        if serializer.is_valid() and transaction.code == serializer.validated_data['code']:
            transaction.status = 'success'
            transaction.profile.balance += transaction.amount
            transaction.profile.save()
            transaction.save()
            return Response({"message": "Баланс успешно пополнен!"})

        transaction.status = 'failed'
        transaction.save()
        return Response({"error": "Неверный код"}, status=400)