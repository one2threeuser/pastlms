from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self) -> None:
        from django.db.models.signals import post_save
        from .models import User
        from .signals import post_save_account_receiver
        # from .signals import post_save_account_receiver_again

        post_save.connect(post_save_account_receiver, sender=User)
        # post_save.connect(post_save_account_receiver_again, sender=User)


        return super().ready()
