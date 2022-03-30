from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **user_fields):
        if not email:
            raise ValueError('email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **user_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **user_fields):
        user_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **user_fields)

    def create_superuser(self, email, password, **user_fields):
        user_fields.setdefault('is_superuser', True)
        user_fields.setdefault('is_staff', True)
        return self._create_user(email, password, **user_fields)
