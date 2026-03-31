import requests
from datetime import datetime
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets, permissions, generics, views



from . import utils
from . import serializers
from . import models



class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UsersSerializer
    permission_classes = [permissions.AllowAny]
    queryset = models.User.objects.all()



class RegisterUserView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Check your email! We’ve sent you an OTP. Use it to complete your registration."
                },
                status=status.HTTP_201_CREATED,
            )
        print(serializer.errors)
        return Response(
            utils.registration_error_message(serializer),
            status=status.HTTP_400_BAD_REQUEST,
        )


class SendOTP(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        otp_identifier = request.data["otp_identifier"]
        otp_record = models.OTPVerify.objects.filter(
            Q(email=otp_identifier) | Q(phone=otp_identifier)
        ).first()
        serializer = serializers.SendOTPSerializer(data=request.data)

        if serializer.is_valid() and otp_record:
            try:
                with transaction.atomic():
                    # Mark OTP as verified
                    otp_record.is_verify = False
                    otp_record.otp = utils.generate_otp()
                    otp_record.expired = utils.expired_time()
                    otp_record.otp_type = "Reset Password"
                    otp_record.save()

                    # utils.send_otp_email.delay(otp_identifier, otp_record.new_otp)

                    utils.send_otp_email(otp_identifier, otp_record.otp)

                return Response(
                    {"message": f"Send OTP to {otp_identifier}"},
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(
            utils.error_message(serializer), status=status.HTTP_400_BAD_REQUEST
        )


class VerifyOTP(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = serializers.OTPVerifySerializer(data=request.data)

        if serializer.is_valid():
            otp_identifier = serializer.validated_data.get("otp_identifier")
            otp = serializer.validated_data.get("otp")

            # Check if OTP matches for either email or phone
            otp_record = models.OTPVerify.objects.filter(
                (Q(email=otp_identifier) | Q(phone=otp_identifier)) & Q(otp=otp)
            ).first()

            if otp_record:
                try:
                    with transaction.atomic():
                        # Mark OTP as verified
                        otp_record.is_verify = True
                        otp_record.save()

                        # Activate user account if exists
                        models.User.objects.filter(email=otp_identifier).update(
                            is_active=True,
                            is_verified=True,
                        )

                    return Response(
                        {"message": "OTP verified"}, status=status.HTTP_200_OK
                    )

                except Exception as e:
                    return Response(
                        {"message": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            return Response(
                {"message": "OTP does not match."}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            utils.error_message(serializer), status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            # Get expiration timestamp from the access token
            access_exp = refresh.access_token["exp"]
            # Convert to datetime object
            access_expires_at = datetime.fromtimestamp(access_exp)
            timestamp = int(access_expires_at.timestamp())

            user_profile_data = models.Profile.objects.get(user=user)
            serializer_data = serializers.UserProfileSerializer(
                context={"request": request}
            ).to_representation(user_profile_data)

            context = {
                "refresh": str(refresh),
                "access_expires_at": timestamp,
                "access": str(refresh.access_token),
                "profile_data": serializer_data,
            }

            return Response(context, status=status.HTTP_200_OK)

        return Response(
            utils.error_message(serializer), status=status.HTTP_400_BAD_REQUEST
        )


class ProfileUpdateApiView(generics.UpdateAPIView, generics.RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserProfileSerializer

    def get_object(self):
        profile = models.Profile.objects.get(user=self.request.user)
        self.check_object_permissions(self.request, profile)
        return profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(
            {"message": "Profile updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(generics.UpdateAPIView, generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ChangePasswordSerializer

    def get_object(self):
        user = models.User.objects.get(id=self.request.user.id)
        self.check_object_permissions(self.request, user)
        return user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance.set_password(serializer.validated_data["new_password"])
            instance.save()
            return Response(
                {"message": "Password updated successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(
            utils.error_message(serializer), status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request):
        serializer = serializers.ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"message": "Password changed successfully."}, status=status.HTTP_200_OK
            )

        return Response(
            utils.error_message(serializer), status=status.HTTP_400_BAD_REQUEST
        )


class ResetPasswordView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = serializers.ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"message": "Password reset successfully"},
                status=status.HTTP_200_OK,
            )
        print('serializer.errors==', serializer.errors)
        return Response(
            utils.error_message(serializer), status=status.HTTP_400_BAD_REQUEST
        )


class GoogleLoginApiView(views.APIView):
    permission_classes = [AllowAny]

    # def get(self, request):
    def post(self, request):
        access_token = request.data.get("access_token")
        if access_token:
            # print('access_token==', access_token)
            # return Response("hello")
            # Make a request to fetch the user's profile information
            profile_endpoint = "https://www.googleapis.com/oauth2/v1/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(profile_endpoint, headers=headers)

            if profile_response.status_code == 200:
                profile_data = profile_response.json()

                if models.User.objects.filter(email=profile_data["email"]).exists():
                    user = models.User.objects.get(email=profile_data["email"])

                else:

                    try:
                        with transaction.atomic():
                            user = models.User.objects.create(
                                email=profile_data["email"],
                                is_active=True,
                            )

                            models.Profile.objects.create(
                                user=user,
                                first_name=profile_data.get("given_name", ""),
                            )

                    except Exception as e:
                        # Handle exceptions or logging if needed
                        return Response(
                            {
                                "message": f"Registration Failed {e}",
                            },
                            status.HTTP_400_BAD_REQUEST,
                        )

                refresh = RefreshToken.for_user(user)

                # Get expiration timestamp from the access token
                access_exp = refresh.access_token["exp"]
                # Convert to datetime object
                access_expires_at = datetime.fromtimestamp(access_exp)
                timestamp = int(access_expires_at.timestamp())

                user_profile_data = models.Profile.objects.get(user=user)
                serializer_data = serializers.UserProfileSerializer().to_representation(
                    user_profile_data
                )
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "access_expires_at": timestamp,
                        "profile_data": serializer_data,
                    }
                )

            return Response(
                {
                    "message": "Google Authentication Error",
                },
                status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Access Token Not Found",
            },
            status.HTTP_400_BAD_REQUEST,
        )


class DeliveryAddressViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DeliveryAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return addresses belonging to the current user
        return models.DeliveryAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the current user when creating
        serializer.save(user=self.request.user)

    # Optional: Custom action to set address as default
    from rest_framework.decorators import action

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        address = self.get_object()  # This already checks ownership via get_queryset
        address.is_default = True
        address.save()

        return Response({
            "message": "This address has been set as default successfully."
        }, status=status.HTTP_200_OK)