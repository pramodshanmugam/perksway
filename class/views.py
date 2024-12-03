from urllib import request
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from users.models import CustomUser
from .models import Class, Wallet
from .serializers import BulkGroupCreateSerializer, ClassSerializer, GroupDetailSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Class, Group
from .serializers import GroupSerializer
from django.shortcuts import get_object_or_404
# Custom permission to allow only teachers to create classes
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

# List all classes for authenticated users (students can view and join, teachers can view their own classes)
class ClassListView(generics.ListAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # If the user is a teacher, show only the classes they have created
        if user.role == 'teacher':
            return Class.objects.filter(teacher=user)
        elif user.role == 'student':
            return Class.objects.filter(students=user)
        # If the user is a student, show all classes

# Create a class (only for teachers)
class ClassCreateView(generics.CreateAPIView):
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def perform_create(self, serializer):
        # Automatically set the teacher to the logged-in user
        serializer.save(teacher=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_class(request, class_code):
    try:
        class_to_join = Class.objects.get(class_code=class_code)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role == 'student':
        if class_to_join.students.filter(id=request.user.id).exists():
            return Response({'error': 'You are already enrolled in this class'}, status=status.HTTP_409_CONFLICT)
        
        class_to_join.students.add(request.user)
        class_to_join.save()
        # Create a wallet for the student for this class
        Wallet.objects.get_or_create(owner=request.user, class_ref=class_to_join, defaults={'balance': 0.00})
        return Response({'message': 'Joined class successfully and wallet created'})
    
    return Response({'error': 'Only students can join classes'}, status=status.HTTP_403_FORBIDDEN)


class GroupDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_id):
        """Retrieve list of groups for the class where the user is present (either as a student or teacher)."""
        # Get the class object
        class_obj = get_object_or_404(Class, id=class_id)
        
        # Check if the user is the teacher of the class
        if request.user == class_obj.teacher:
            # If user is the teacher, return all groups of this class
            groups = Group.objects.filter(class_ref=class_obj)
        
        # Check if the user is a student in the class
        elif class_obj.students.filter(id=request.user.id).exists():
            # If user is a student, return all groups of this class
            groups = Group.objects.filter(class_ref=class_obj)
        
        else:
            # If the user is neither a teacher nor a student in the class, deny access
            return Response({"detail": "You are not a member of this class."}, status=status.HTTP_403_FORBIDDEN)
        
        # Serialize and return the group data
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, group_id):
        """Update group details (only by the creator)."""
        group = self.get_group(group_id, request.user)
        if not group:
            return Response({"detail": "Permission denied. You are not the creator of this group."}, status=status.HTTP_403_FORBIDDEN)

        serializer = GroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, group_id):
        """Delete group (only by the creator)."""
        group = self.get_group(group_id, request.user)
        if not group:
            return Response({"detail": "Permission denied. You are not the creator of this group."}, status=status.HTTP_403_FORBIDDEN)

        group.delete()
        return Response({"detail": "Group deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class AllGroupsInClassView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this API

    def get(self, request, class_id):
        """Retrieve all groups for a given class."""
        class_obj = get_object_or_404(Class, id=class_id)

        # Get all groups associated with this class
        groups = Group.objects.filter(class_ref=class_obj)
        serializer = GroupSerializer(groups, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)



class GroupCreateView(generics.CreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def perform_create(self, serializer):
        # Get the class based on class_id from the URL
        class_id = self.request.data.get('class_ref')
        class_obj = get_object_or_404(Class, id=class_id)

        # Ensure the logged-in user is the teacher of this class
        if self.request.user != class_obj.teacher:
            return Response({"detail": "You are not authorized to create groups for this class."}, status=status.HTTP_403_FORBIDDEN)

        # Create the group and set the current user as the creator and class_ref as the class
        serializer.save(creator=self.request.user, class_ref=class_obj) 



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    user = request.user
    
    # Check if student is already in another group in the same class
    class_groups = Group.objects.filter(class_ref=group.class_ref, students=user)
    if class_groups.exists():
        return Response({"error": "Already in another group in this class."}, status=403)
    
    # Check if max_students limit has been reached
    if group.max_students and group.students.count() >= group.max_students:
        return Response({"error": "Group is full."}, status=403)

    # If approval is required, add to pending approvals
    if group.requires_approval:
        group.pending_approvals.add(user)
        return Response({"message": "Join request submitted for approval."}, status=200)
    else:
        group.students.add(user)
        return Response({"message": "Successfully joined the group."}, status=200)


class GroupDetailWithStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        # Get the group based on the provided group_id
        group = get_object_or_404(Group, id=group_id)
        
        # Serialize the group data, including nested students
        serializer = GroupDetailSerializer(group)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserEnrolledClassView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the class the user is enrolled in."""
        user = request.user

        if user.role == 'student':
            # Get the class where the student is enrolled
            enrolled_classes = Class.objects.filter(students=user)
            if enrolled_classes.exists():
                serializer = ClassSerializer(enrolled_classes.first())  # Assuming a student is enrolled in one class
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "User is not enrolled in any class."}, status=status.HTTP_404_NOT_FOUND)

        elif user.role == 'teacher':
            # Get the classes where the teacher is the creator
            created_classes = Class.objects.filter(teacher=user)
            serializer = ClassSerializer(created_classes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"detail": "User role not recognized."}, status=status.HTTP_400_BAD_REQUEST)
    



class ApproveJoinRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        
        # Ensure the request is made by the teacher
        if request.user != group.class_ref.teacher:
            return Response({"error": "Not authorized"}, status=403)

        # Check if only the count is needed
        only_count = request.query_params.get('count', False)

        # List pending approvals
        pending_users = group.pending_approvals.all()
        
        # If only the count is needed
        if only_count:
            return Response({"count": pending_users.count()})

        # Return details if count is not specifically requested
        user_details = [{"id": user.id, "username": user.username} for user in pending_users]
        return Response({"pending_approvals": user_details, "count": len(user_details)})

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        user_id = request.data.get("user_id")
        action = request.data.get("action")  # 'approve' or 'decline'
        
        if request.user != group.class_ref.teacher:
            return Response({"error": "Not authorized"}, status=403)

        student = get_object_or_404(CustomUser, id=user_id)
        
        if action == "approve":
            group.students.add(student)
            group.pending_approvals.remove(student)
            return Response({"message": "Student approved to join."})
        
        elif action == "decline":
            group.pending_approvals.remove(student)
            return Response({"message": "Student request declined."})
        
        return Response({"error": "Invalid action"}, status=400)



class BulkGroupCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, class_id):
        # Check if the logged-in user is the teacher for the class
        class_obj = get_object_or_404(Class, id=class_id)
        if request.user != class_obj.teacher:
            return Response({"error": "Not authorized to create groups for this class."}, status=status.HTTP_403_FORBIDDEN)

        serializer = BulkGroupCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            groups = []

            # Loop to create the specified number of groups
            for i in range(data['number_of_groups']):
                group_name = f"{data['group_name_prefix']} {i + 1}"
                group = Group(
                    name=group_name,
                    max_students=data['max_students'],
                    requires_approval=data['requires_approval'],
                    class_ref=class_obj,
                    creator=request.user
                )
                group.save()
                groups.append(group)

            return Response(
                {"message": f"{data['number_of_groups']} groups created successfully.", "groups": [group.name for group in groups]},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BulkApprovalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        user_ids = request.data.get("user_ids", [])  # List of user IDs
        action = request.data.get("action")  # 'approve' or 'decline'
        
        if request.user != group.class_ref.teacher:
            return Response({"error": "Not authorized"}, status=403)
        
        students = CustomUser.objects.filter(id__in=user_ids)
        
        if action == "approve":
            group.students.add(*students)
            group.pending_approvals.remove(*students)
            message = "Students approved to join."
        elif action == "decline":
            group.pending_approvals.remove(*students)
            message = "Student requests declined."
        else:
            return Response({"error": "Invalid action"}, status=400)

        return Response({"message": message})



class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_id):
        """Get the wallet balance for the logged-in user in the specified class."""
        # Check if the class exists and the user is enrolled in it
        class_obj = get_object_or_404(Class, id=class_id)

        if request.user.role == 'student' and not class_obj.students.filter(id=request.user.id).exists():
            return Response({'error': 'User is not a student in this class'}, status=status.HTTP_403_FORBIDDEN)

        # Fetch the wallet associated with this user and class
        try:
            wallet = Wallet.objects.get(owner=request.user, class_ref=class_obj)
            return Response({'balance': wallet.balance}, status=status.HTTP_200_OK)
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found for this class'}, status=status.HTTP_404_NOT_FOUND)