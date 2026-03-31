
from rest_framework import serializers
from . import models as user_models
from . import utils

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.User
        fields = '__all__'




import datetime
from django.db.models import Q
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.exceptions import ValidationError




class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = user_models.User
        fields = ['email', 'password', 'first_name', 'user_type', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        try:
            email = validated_data.get('email')
            password = validated_data.pop('password')
            first_name = validated_data.get('first_name', '')
            user_type = validated_data.get('user_type', '')
            is_staff = validated_data.get('is_staff', False)


            # User creation (Profile will be created automatically by signal)
            user = user_models.User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                user_type=user_type,
                is_staff=is_staff,

            )

            # Create OTPVerify record for email verification
            otp_record = user_models.OTPVerify.objects.create(
                user=user,
                email=email,
                otp=utils.generate_otp(),
                expired=utils.expired_time(),
                otp_type='Registration',
                is_verify=False
            )

            # Send OTP email
            # utils.send_otp_email(email, otp_record.otp)

            return user
        except Exception as e:
            raise ValidationError({'error': str(e)})

    def to_internal_value(self, data):
        """
        Override to return all validation errors in the {'error': 'message'} format.
        """
        try:
            return super().to_internal_value(data)
        except ValidationError as exc:
            # Extract the first error message from the error details
            error_message = next(iter(exc.detail.values()))[0]
            raise ValidationError({'message': error_message.title()})



class SendOTPSerializer(serializers.Serializer):
    otp_identifier = serializers.CharField()

    def validate(self, data):
        otp_identifier = data.get('otp_identifier')

        # get_otp_verify = user_models.OTPVerify.objects.filter(Q(email=otp_identifier) | Q(phone=otp_identifier)).exists()
        get_otp_verify = user_models.OTPVerify.objects.filter(email=otp_identifier).exists()

        if get_otp_verify:
            return data
        else:
            raise serializers.ValidationError({"error": f"{otp_identifier} is not registered!"})



class OTPVerifySerializer(serializers.Serializer):
    otp_identifier = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        otp_identifier = data.get('otp_identifier')
        otp = data.get('otp')

        # get_otp_verify = user_models.OTPVerify.objects.filter(
        #         (Q(email=otp_identifier) | Q(phone=otp_identifier)) & Q(otp=otp)
        #     ).first()
        get_otp_verify = user_models.OTPVerify.objects.filter(
                (Q(email=otp_identifier) | Q) & Q(otp=otp)
            ).first()

        if get_otp_verify:
            # Check if OTP has expired
            from django.utils.timezone import now as django_now
            if get_otp_verify.expired < django_now():
                raise serializers.ValidationError({"error": "OTP expired!"})
            return data
        return data




class LoginSerializer(serializers.Serializer):
    login_identifier = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        login_identifier = data.get('login_identifier')
        password = data.get('password')

        user = None

        # Try to authenticate by email or username
        try:
            # Try email first
            user_obj = user_models.User.objects.get(email=login_identifier)
            user_password_valid = user_obj.check_password(password)
            if user_password_valid and user_obj.is_active:
                user = user_obj
            else:
                # Try by username if email didn't work
                user_obj = user_models.User.objects.get(username=login_identifier)
                user_password_valid = user_obj.check_password(password)
                if user_password_valid and user_obj.is_active:
                    user = user_obj
        except user_models.User.DoesNotExist:
            pass

        if user is None:
            raise serializers.ValidationError({'error': 'No active account found with the given credentials'})

        data['user'] = user
        return data



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def to_internal_value(self, data):
        # Accept common typo from client input
        if 'confrim_password' in data and 'confirm_password' not in data:
            data = data.copy()
            data['confirm_password'] = data.get('confrim_password')
        return super().to_internal_value(data)

    def validate(self, data):
        user = self.context['request'].user
        old_password = data.get('old_password')
        # Check the old password
        if not user.check_password(old_password):
            # Raise ValidationError in a global way, with "error" as the key
            raise serializers.ValidationError({"error": "Old password is not correct."})

        # Check if new password matches confirm password
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"error": "New and Confirm Password do not match."})

        # Ensure the new password is different from the old password
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({"error": "New password must be different from the old password."})

        return data



class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    reset_identifier = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"error": "Password fields didn't match."})

        reset_identifier = attrs['reset_identifier']

        get_identifier_otp_verify = user_models.OTPVerify.objects.filter(email=reset_identifier).first()
        if get_identifier_otp_verify:
            if get_identifier_otp_verify.is_verify == False:
                raise serializers.ValidationError({"error": "OTP not verified !"})

            # valided_time = get_identifier_otp_verify.expired

            # _valided_time = datetime.datetime(
            #     valided_time.year, valided_time.month, valided_time.day,
            #     valided_time.hour, valided_time.minute, valided_time.second
            #     )

            # current_time = datetime.datetime.now()

            # _current_time = datetime.datetime(
            #     current_time.year, current_time.month, current_time.day,
            #     current_time.hour, current_time.minute, current_time.second
            #     )

            # if _valided_time < _current_time:
            #     raise serializers.ValidationError({"error": "OTP expired!"})


            _user = user_models.User.objects.get(email=reset_identifier)
            _user.set_password(attrs['password'])
            _user.save()
            return attrs

        raise serializers.ValidationError({"error": "OTP not verified !"})




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.Profile
        fields = '__all__'



class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.DeliveryAddress
        fields = '__all__'
        read_only_fields = ['user']

