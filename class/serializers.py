from rest_framework import serializers
from .models import Class, Group, Item, PurchaseRequest, Wallet
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'role']

class ClassSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.email')  # Teacher's email will be read-only
    students = serializers.StringRelatedField(many=True, read_only=True)  # Student names in the response

    class Meta:
        model = Class
        fields = ['id', 'name', 'description', 'class_code', 'teacher', 'students']
        read_only_fields = ['teacher', 'students']

class GroupSerializer(serializers.ModelSerializer):
    students = UserSerializer(many=True, read_only=True)  # Display students in the response

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'class_ref', 'creator', 'students', 'created_at', 'updated_at']
        read_only_fields = ['creator', 'students']  # Make creator and students read-only

class GroupDetailSerializer(serializers.ModelSerializer):
    students = UserSerializer(many=True)  # Serialize the students as a nested field

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'students']


class BulkGroupCreateSerializer(serializers.Serializer):
    number_of_groups = serializers.IntegerField(min_value=1)
    group_name_prefix = serializers.CharField(max_length=100)
    max_students = serializers.IntegerField(min_value=1)
    requires_approval = serializers.BooleanField(default=False)

    def validate(self, data):
        # Ensure a sensible number of groups is requested (optional validation)
        if data['number_of_groups'] > 100:  # Arbitrary limit to prevent excessive group creation
            raise serializers.ValidationError("Too many groups requested.")
        return data
    
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'image', 'class_ref']

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance']

class PurchaseRequestSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()  # Display the username of the student
    item = serializers.StringRelatedField()  # Display the name of the item
    class_ref = serializers.StringRelatedField()  # Display the name of the class (optional)
    
    class Meta:
        model = PurchaseRequest
        fields = ['id', 'student', 'item', 'amount', 'status', 'requested_at', 'class_ref']
        read_only_fields = ['id', 'student', 'item', 'requested_at', 'class_ref']