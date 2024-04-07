from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, ReferralSerializer
from .models import User, Referral
from rest_framework.permissions import IsAuthenticated
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
import datetime
from rest_framework import status
import string
import random
from rest_framework.pagination import PageNumberPagination

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Check if referral code is provided
            provided_referral_code = request.data.get('referral_code')
            if provided_referral_code:
                try:
                    # Check if the provided referral code matches with any previous user's referral code
                    referrer = User.objects.get(referral_code=provided_referral_code)
                    message = 'Provided referral code matches!'
                except User.DoesNotExist:
                    # If the referral code doesn't match, generate a new referral code for the user
                    user = serializer.save()
                    referral_code = self.generate_referral_code()
                    user.referral_code = referral_code
                    user.save()
                    return Response({'user_id': user.id, 'referral_code': referral_code, 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
                else:
                    # Generate a new referral code even if the provided one matches
                    user = serializer.save()
                    referral_code = self.generate_referral_code()
                    Referral.objects.create(referrer=referrer, referred_user=user, referral_code=referral_code)
                    return Response({'user_id': user.id, 'referral_code': referral_code, 'message': 'User registered successfully. ' + message}, status=status.HTTP_201_CREATED)
            else:
                # If no referral code is provided, simply save the user with a new referral code
                user = serializer.save()
                referral_code = self.generate_referral_code()
                user.referral_code = referral_code
                user.save()
                return Response({'user_id': user.id, 'referral_code': referral_code, 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_referral_code(self):
        # Generate a random code
        code_length = 6
        characters = string.ascii_letters + string.digits
        referral_code = ''.join(random.choice(characters) for _ in range(code_length))

        # Ensure the generated code is unique
        while Referral.objects.filter(referral_code=referral_code).exists():
            referral_code = ''.join(random.choice(characters) for _ in range(code_length))

        return referral_code

class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

class ReferralsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        referrals = Referral.objects.filter(referrer=user)
        serializer = ReferralSerializer(referrals, many=True)
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        # Generate access token and refresh token
        refresh = RefreshToken.for_user(user)

        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        })

class UserView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):
        return Response({'message': 'success'})


class UserReferralListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 20  # Set page size to 20

    def get(self, request):
        # Get the current user
        current_user = request.user

        # Get the referrals for the current user, ordered by id
        referrals = Referral.objects.filter(referrer=current_user).order_by('id')

        # Paginate the referrals
        paginator = self.pagination_class()
        paginated_referrals = paginator.paginate_queryset(referrals, request)

        # Extract referred users from paginated referrals
        referred_users = [referral.referred_user for referral in paginated_referrals]

        # Serialize the users
        serializer = UserSerializer(referred_users, many=True)

        # Construct paginated response
        response_data = serializer.data
        paginated_response = paginator.get_paginated_response(response_data)

        # Add next and previous page links to the response
        if paginator.page.has_next():
            paginated_response.data['next'] = paginator.get_next_link()
        if paginator.page.has_previous():
            paginated_response.data['previous'] = paginator.get_previous_link()

        return paginated_response
