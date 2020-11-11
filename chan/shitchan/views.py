from rest_framework import (
    viewsets, authentication, permissions
)

from shitchan import serializers

from core import models


class ManageBoardViewSet(viewsets.ModelViewSet):
    """Manage create board in API"""
    serializer_class = serializers.BoardSerializer
    authentication_classes = [authentication.TokenAuthentication, ]
    queryset = models.Board.objects.all()

    def get_permissions(self):
        """Instantiates and returns the list of permissions
        that this view requires"""
        if self.action == 'list':
            permission_classes = [permissions.AllowAny, ]
        else:
            permission_classes = [permissions.IsAdminUser, ]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create and save board"""
        serializer.save(user=self.request.user)
