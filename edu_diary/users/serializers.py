from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile, StudentParent

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'class_number', 'class_letter', 'phone', 'address']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'role', 'avatar', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'role', 'avatar', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'password', 'password2', 'role', 'avatar', 'profile']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            role=validated_data['role']
        )

        if 'avatar' in validated_data:
            user.avatar = validated_data['avatar']

        user.set_password(validated_data['password'])
        user.save()

        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults=profile_data or {}
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        return attrs


class StudentParentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    parent = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'), source='student', write_only=True
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='parent'), source='parent', write_only=True
    )

    class Meta:
        model = StudentParent
        fields = ['id', 'student', 'student_id', 'parent', 'parent_id']

    def validate(self, attrs):
        student = attrs.get('student')
        parent = attrs.get('parent')

        if student.role != 'student':
            raise serializers.ValidationError({'student': 'Пользователь должен быть учеником'})
        if parent.role != 'parent':
            raise serializers.ValidationError({'parent': 'Пользователь должен быть родителем'})

        if self.instance is None:
            if StudentParent.objects.filter(student=student).count() >= 2:
                raise serializers.ValidationError(
                    {'student': 'Ученик уже привязан к максимальному количеству родителей (2)'}
                )

        return attrs
