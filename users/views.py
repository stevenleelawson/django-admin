from rest_framework import exceptions, viewsets, status, generics, mixins
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import generate_access_token, JWTAuthentication
from .models import User
from .serializers import UserSerializer
# from django.contrib.auth.hashers import check_password
# Create your views here.

@api_view(['POST'])
def register(request):
	data = request.data

	if data['password'] != data['password_confirm']:
		raise exceptions.APIException('Passwords do not match SUCKAH')

	serializer = UserSerializer(data=data)
	serializer.is_valid(raise_exception=True)
	serializer.save()
	return Response(serializer.data)

@api_view(['POST'])
def login(request):
	email = request.data.get('email')
	password = request.data.get('password')
	user = User.objects.filter(email=email).first()

	if user is None:
		raise exceptions.AuthenticationFailed('User not found SUKAH!!')

	if not user.check_password(password):
		raise exceptions.AuthenticationFailed('DIE!')
	
	response = Response()

	token = generate_access_token(user)
	response.set_cookie(key='jwt', value=token, httponly=True)
	response.data = {
		'jwt': token
	}

	return response

@api_view(['POST'])
def logout(_):
	response = Response()
	response.delete_cookie(key='jwt')
	response.data = {
		'message': 'Success mang!'
	}

	return response


class AuthenticatedUser(APIView):
	# middleware to check if user is authenticated
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]

	def get(self, request):
		serializer = UserSerializer(request.user)

		return Response({
			'data': serializer.data
		})

@api_view(['GET'])
def users(request):
	serializer = UserSerializer(User.objects.all(), many=True)
	return Response(serializer.data)