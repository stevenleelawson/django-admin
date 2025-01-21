from rest_framework import exceptions, viewsets, status, generics, mixins
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admin.pagination import CustomPagination
from .authentication import generate_access_token, JWTAuthentication
from .models import User, Permission, Role
from .serializers import UserSerializer, PermissionSerializer, RoleSerializer
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

class PermissionAPIView(APIView):
	# middleware to check if user is authenticated
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]

	def get(self, request):
		serializer = PermissionSerializer(Permission.objects.all(), many=True)

		return Response({
			'data': serializer.data
		})

class RoleViewSet(viewsets.ViewSet):
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]

	# not get method in a viewset, LIST is for getting the list of objects
	def list(self, request):
		serializer = RoleSerializer(Role.objects.all(), many=True)

		return Response({
			'data': serializer.data
		})

	def create(self, request):
		serializer = RoleSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response({
			'data': serializer.data
		}, status.HTTP_201_CREATED)


	# retrieve is for getting a SINGLE object
	def retrieve(self, request, pk=None):
		role = Role.objects.get(id=pk)
		serializer = RoleSerializer(role)

		return Response({
			'data': serializer.data
		})

	def update(self, request, pk=None):
		role = Role.objects.get(id=pk)
		serializer = RoleSerializer(instance=role, data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response({
			'data': serializer.data
		}, status=status.HTTP_202_ACCEPTED)

	def destroy(self, request, pk=None):
		role = Role.objects.get(id=pk)
		role.delete()

		return Response(status=status.HTTP_204_NO_CONTENT)


class UserGenericAPIView(
	generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin
):
	# now we don't have to do all the the above with list, destroy, ect coz it is all handled by the GenericView
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]
	queryset = User.objects.all()
	serializer_class = UserSerializer
	pagination_class = CustomPagination

	def get(self, request, pk=None):
		if pk:
			return Response({
				'data': self.retrieve(request, pk).data
			})

		return self.list(request)

	def post(self, request, pk=None):
		return Response({
			'data': self.create(request).data
		})

	def put(self, request):
		return Response({
			'data': self.update(request).data
		})

	def delete(self, request):
		return self.destroy(request, pk)

