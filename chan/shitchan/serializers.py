from rest_framework import serializers

from core.models import Board


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for board"""

    class Meta:
        model = Board
        fields = ['id', 'title', 'code']
        read_only_fields = ['id', ]
