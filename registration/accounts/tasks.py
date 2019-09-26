from datetime import datetime, timedelta

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from .models import User


@shared_task
def reset_counter(user_id):
    try:
        user = User.objects.get(id=user_id)
        user.fail_count = 0
        user.login_attempt_time = None
        user.save()
    except ObjectDoesNotExist:
        pass


@shared_task
def un_ban_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.ban_time < datetime.now():
            user.fail_count = 0
            user.login_attempt_time = None
            user.ban_time = None
            user.is_banned = False
            user.save()
    except ObjectDoesNotExist:
        pass


@shared_task
def ban_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.fail_count == 0:
            user.fail_count = 1
            user.login_attempt_time = datetime.now()
            user.save()
        elif user.fail_count > 2 and user.login_attempt_time > datetime.now() - timedelta(minutes=10):
            user.is_banned = True
            user.ban_time = datetime.now() + timedelta(hours=1)
            user.save()
            un_ban_user.apply_async((user_id,), eta=user.ban_time)
        else:
            user.fail_count += 1
            user.save()
    except ObjectDoesNotExist:
        pass


@shared_task
def ban_ip(user_ip):
    try:
        fail_sum = 0
        first_attempt = datetime.now()
        users = User.objects.filter(ip=user_ip)
        for user in users:
            fail_sum += user.fail_count
            if user.login_attempt_time < first_attempt:
                first_attempt = user.login_attempt_time
        if fail_sum > 9 and first_attempt > datetime.now() - timedelta(minutes=60):
            for user in users:
                user.is_banned = True
                user.ip_banned = True
                user.ban_time = datetime.now() + timedelta(days=1)
                user.save()
                un_ban_user.apply_async((user.id,), eta=user.ban_time)
    except ObjectDoesNotExist:
        pass
