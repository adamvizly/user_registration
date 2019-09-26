from django.contrib.auth import get_user_model
from rest_framework import serializers

from .tasks import *

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, label="Username")
    password = serializers.CharField(required=True, label="Password", style={'input_type': 'password'})

    class Meta(object):
        model = User
        fields = ['username', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("username already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password should be at least 8 characters long.")
        return value

    def create(self, validated_data):
        request = self.context.get('request', None)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        try:
            if User.objects.filter(ip=ip).first().ip_banned:
                raise serializers.ValidationError("Your ip is banned")
        except ObjectDoesNotExist:
            pass
        user = User.objects.create_user(username=validated_data['username'], password=validated_data['password'])
        user.ip = ip
        user.save()
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    class Meta(object):
        model = User
        fields = ['username', 'password']

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)

        if not username:
            raise serializers.ValidationError("Please enter username to login.")

        user = User.objects.filter(username=username).distinct()

        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise serializers.ValidationError("This username is not valid.")

        if user_obj:
            if user_obj.ip_banned:
                raise serializers.ValidationError("Your ip is banned for one day.")
            if user_obj.is_banned:
                raise serializers.ValidationError("Your username is banned for one hour.")
            elif not user_obj.check_password(password):
                ban_user.delay(user_obj.id)
                ban_ip.delay(user_obj.ip)
                raise serializers.ValidationError("Invalid password.")
            else:
                reset_counter.delay(user_obj.id)

        return data
