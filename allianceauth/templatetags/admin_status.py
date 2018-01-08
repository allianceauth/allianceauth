import requests
import logging
import amqp.exceptions
import semantic_version as semver
from django import template
from django.conf import settings
from django.core.cache import cache
from celery.app import app_or_default
from allianceauth import __version__

register = template.Library()

TAG_CACHE_TIME = 10800  # 3 hours
NOTIFICATION_CACHE_TIME = 300  # 5 minutes


logger = logging.getLogger(__name__)


def get_github_tags():
    request = requests.get('https://api.github.com/repos/allianceauth/allianceauth/releases')
    request.raise_for_status()
    return request.json()


def get_github_notification_issues():
    # notification
    request = requests.get(
        'https://api.github.com/repos/allianceauth/allianceauth/issues?labels=announcement&state=all')
    request.raise_for_status()
    return request.json()


@register.inclusion_tag('allianceauth/admin-status/overview.html', takes_context=True)
def status_overview(context):
    response = {
        'notifications': list(),
        'latest_major': True,
        'latest_minor': True,
        'latest_patch': True,
        'current_version': __version__,
        'task_queue_length': -1,
    }

    response.update(get_notifications())
    response.update(get_version_info())
    response.update({'task_queue_length': get_celery_queue_length()})

    return response


def get_celery_queue_length():
    try:
        app = app_or_default(None)
        with app.connection_or_acquire() as conn:
            return conn.default_channel.queue_declare(
                queue=getattr(settings, 'CELERY_DEFAULT_QUEUE', 'celery'), passive=True).message_count
    except amqp.exceptions.ChannelError:
        # Queue doesn't exist, probably empty
        return 0
    except Exception:
        logger.exception("Failed to get celery queue length")
    return -1


def get_notifications():
    response = {
        'notifications': list(),
    }
    try:
        notifications = cache.get_or_set('github_notification_issues', get_github_notification_issues,
                                         NOTIFICATION_CACHE_TIME)
        # Limit notifications to those posted by repo owners and members
        response['notifications'] += [n for n in notifications if n['author_association'] in ['OWNER', 'MEMBER']][:5]
    except requests.RequestException:
        logger.exception('Error while getting github notifications')
    return response


def get_version_info():
    response = {
        'latest_major': True,
        'latest_minor': True,
        'latest_patch': True,
        'current_version': __version__,
    }
    try:
        tags = cache.get_or_set('github_release_tags', get_github_tags, TAG_CACHE_TIME)
        current_ver = semver.Version.coerce(__version__)

        # Set them all to the current version to start
        # If the server has only earlier or the same version
        # then this will become the major/minor/patch versions
        latest_major = current_ver
        latest_minor = current_ver
        latest_patch = current_ver

        response.update({
            'latest_major_version': str(latest_major),
            'latest_minor_version': str(latest_minor),
            'latest_patch_version': str(latest_patch),
        })

        for tag in tags:
            tag_name = tag.get('tag_name')
            if tag_name[0] == 'v':
                # Strip 'v' off front of verison if it exists
                tag_name = tag_name[1:]
            try:
                tag_ver = semver.Version.coerce(tag_name)
            except ValueError:
                tag_ver = semver.Version('0.0.0', partial=True)
            if tag_ver > current_ver:
                if latest_major is None or tag_ver > latest_major:
                    latest_major = tag_ver
                    response['latest_major_version'] = tag_name
                    response['latest_major_url'] = tag['html_url']
                if tag_ver.major > current_ver.major:
                    response['latest_major'] = False
                elif tag_ver.major == current_ver.major:
                    if latest_minor is None or tag_ver > latest_minor:
                        latest_minor = tag_ver
                        response['latest_minor_version'] = tag_name
                        response['latest_minor_url'] = tag['html_url']
                    if tag_ver.minor > current_ver.minor:
                        response['latest_minor'] = False
                    elif tag_ver.minor == current_ver.minor:
                        if latest_patch is None or tag_ver > latest_patch:
                            latest_patch = tag_ver
                            response['latest_patch_version'] = tag_name
                            response['latest_patch_url'] = tag['html_url']
                        if tag_ver.patch > current_ver.patch:
                            response['latest_patch'] = False

    except requests.RequestException:
        logger.exception('Error while getting github release tags')
    return response
