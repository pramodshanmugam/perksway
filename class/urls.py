from django.urls import path
from .views import ApproveJoinRequestView, BulkApprovalView, BulkGroupCreateView, ClassListView, ClassCreateView, GroupDetailWithStudentsView, UserEnrolledClassView, WalletBalanceView,  join_class, GroupDetailView, AllGroupsInClassView, GroupCreateView, join_group

urlpatterns = [
    path('', ClassListView.as_view(), name='class_list'),
    path('create/', ClassCreateView.as_view(), name='class_create'),
    path('join/<str:class_code>/', join_class, name='join_class'),
    path('group/<int:group_id>/', GroupDetailView.as_view(), name='group_detail'),
    path('group/all-groups/<int:class_id>/', AllGroupsInClassView.as_view(), name='all_groups_in_class'),
    path('group/create-group/', GroupCreateView.as_view(), name='create_group'),
    path('group/join/<int:group_id>/', join_group, name='join_group'),
    path('group/details/<int:group_id>/', GroupDetailWithStudentsView.as_view(), name='group_detail_with_students'),
    path('enrolled/', UserEnrolledClassView.as_view(), name='user_enrolled_class'),
    path('group/<int:group_id>/approve-request/', ApproveJoinRequestView.as_view(), name='approve-join-request'),
    path('<int:class_id>/bulk-create-groups/', BulkGroupCreateView.as_view(), name='bulk-create-groups'),
    path('group/<int:group_id>/bulk-approve/', BulkApprovalView.as_view(), name='bulk-approve'),
    path('wallets/<int:class_id>/balance/', WalletBalanceView.as_view(), name='wallet-balance'),
]



