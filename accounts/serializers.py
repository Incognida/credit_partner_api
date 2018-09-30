from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')


class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        min_length=1, max_length=32,
        validators=[UniqueValidator(User.objects.all())]
    )
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(User.objects.all())]
    )
    password = serializers.CharField(
        required=True, min_length=8, write_only=True
    )
    password_2 = serializers.CharField(
        required=True, min_length=8, write_only=True
    )
    role = serializers.ChoiceField(choices=['partner', 'creditor'], required=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email',
            'password', 'password_2',
            'role'
        )

    def validate_password(self, value):
        data = self.get_initial()
        password_2 = data.get('password_2')
        if value != password_2:
            raise serializers.ValidationError('Passwords must match.')
        return value

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data.get('email', '')
        password = validated_data['password']
        role = validated_data['role']
        user = User(
            username=username, email=email, role=role
        )
        user.set_password(password)
        user.save()
        return user
