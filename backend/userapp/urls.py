from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView ,UserReferralListView
from .views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserView.as_view(), name='user'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user-referrals/', UserReferralListView.as_view(), name='user_referrals_list')
]