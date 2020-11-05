from rest_framework import serializers

from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Custom user model"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'date_of_birth', 'password', ]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 6
            },
        }

    def create(self, validated_data):
        """Override default create method to support hashing password"""
        return get_user_model().objects.create_user(**validated_data)
