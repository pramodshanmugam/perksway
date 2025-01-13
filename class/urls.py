from django.urls import path
from .views import ApproveJoinRequestView, PurchaseView, BulkApprovalView, BulkGroupCreateView, ClassListView, ClassCreateView, GroupDetailWithStudentsView, ItemDetailView, ItemListCreateView, PurchaseApprovalView, PurchaseRequestView, UserEnrolledClassView, WalletBalanceView, WalletUpdateView,  join_class, GroupDetailView, AllGroupsInClassView, GroupCreateView, join_group

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
    path('wallets/<int:class_id>/', WalletUpdateView.as_view(), name='wallet-update'),
    path('<int:class_id>/items/', ItemListCreateView.as_view(), name='item-list-create'),
    path('<int:class_id>/items/<int:item_id>/', ItemDetailView.as_view(), name='item-detail'),
    path('<int:class_id>/purchase-approval/', PurchaseApprovalView.as_view(), name='view-purchase-requests'),
     path('<int:class_id>/purchase-item/<int:item_id>/', PurchaseRequestView.as_view(), name='send-purchase-request'),
    # URL to approve/decline a specific purchase request by request_id
    path('purchase-request/<int:request_id>/action/', PurchaseApprovalView.as_view(), name='approve-decline-purchase-request'),
    path('<int:class_id>/purchase/', PurchaseView.as_view(), name='purchase-item'),
]



