
from rest_framework import serializers
from .models import User,Referral


class UserSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(max_length=20, required=False)  # Add referral_code field

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'referral_code', 'timestamp']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        referral_code = validated_data.pop('referral_code', None)

        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

        instance.save()

        # Associate referrer with the new user if referral code provided
        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
                instance.referrer = referrer
                instance.save()
            except User.DoesNotExist:
                pass  # Handle case where referral code doesn't exist

        return instance
class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = '__all__'