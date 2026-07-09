from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            # Try to fetch the user by username or email
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            UserModel().set_password(password)  # Prevent user enumeration
            return None
        except UserModel.MultipleObjectsReturned:
            # If multiple users with the same email exist (shouldn't happen if email is unique)
            # or if a username matches an email of another user, try to find the exact username first.
            try:
                user = UserModel.objects.get(username__iexact=username)
            except UserModel.DoesNotExist:
                user = (
                    UserModel.objects.filter(email__iexact=username)
                    .order_by("id")
                    .first()
                )

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
