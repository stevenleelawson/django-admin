from rest_framework import serializers
from .models import User, Permission, Role

class PermissionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Permission
		fields = '__all__'

class PermissionRelatedField(serializers.StringRelatedField):
	# get the roles
	def to_representation(self, value):
		return PermissionSerializer(value).data

	#store the roles
	def to_internal_value(self, data):
		return data

class RoleSerializer(serializers.ModelSerializer):
	permissions = PermissionRelatedField(many=True)
	class Meta:
		model = Role
		fields = '__all__'

		def create(self, validated_data):
			permissions = validated_data.pop('permissions', None)
			instance = self.Meta.model(**validated_data)
			instance.save()
			instance.permissions.add(*permissions)
			instance.save()
			return instance

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'first_name', 'last_name', 'email', 'password']
		extra_kwargs = {
			'password': {'write_only': True}
		}

	# this overrides the default behavior of create so we can HASH THE PASS
	def create(self, validated_data):
		password = validated_data.pop('password', None)
		instance = self.Meta.model(**validated_data)
		if password is not None:
			instance.set_password(password)
			instance.save()
			return instance
