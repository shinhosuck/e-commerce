from django.db.models.signals import post_save
from django.contrib.auth.models import User
from users.models import UserProfile
from django.dispatch import receiver



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance, 
            user_name=instance.username,
        )


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs ):
    user = User.objects.get(id=instance.id)
    instance.userprofile.email = user.email
    instance.userprofile.save()