from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin

from requests_oauthlib import OAuth1Session
from datetime import datetime
from django.utils.dateparse import parse_datetime

from dataintegration.core.importer import *
from xapi.statement.builder import *  # Formerly dataintegration.core.socialmediabuilder

import dateutil.parser
import os
from xapi.statement.xapi_settings import xapi_settings


class WordPressPlugin(DIBasePlugin, DIPluginDashboardMixin):
    platform = xapi_settings.PLATFORM_WORDPRESS
    platform_url = "https://wordpress.org/"

    xapi_verbs = [xapi_settings.VERB_CREATED, xapi_settings.VERB_SHARED,
                  xapi_settings.VERB_LIKED, xapi_settings.VERB_COMMENTED]
    xapi_objects = [xapi_settings.OBJECT_NOTE]

    user_api_association_name = 'Twitter Username'  # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Hashtags'  # eg hashtags or a group name

    config_json_keys = ['app_key', 'app_secret', 'oauth_token', 'oauth_token_secret']

    # from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = [xapi_settings.OBJECT_NOTE]
    xapi_verbs_to_includein_verbactivitywidget = [xapi_settings.VERB_CREATED, xapi_settings.VERB_SHARED,
                                                  xapi_settings.VERB_LIKED, xapi_settings.VERB_COMMENTED]

    def __init__(self):
        pass

    @classmethod
    def perform_import(cls, retrieval_param, unit):
        wp_host = os.environ.get("WP_HOST")
        client_key = os.environ.get("WP_CLIENT_KEY")
        client_secret = os.environ.get("WP_CLIENT_SECRET")
        access_token_key = os.environ.get("WP_ACCESS_TOKEN_KEY")
        access_token_secret = os.environ.get("WP_ACCESS_TOKEN_SECRET")

        oauth = OAuth1Session(client_key=client_key, client_secret=client_secret, resource_owner_key=access_token_key,
                              resource_owner_secret=access_token_secret)
        cls.get_posts(unit, oauth, wp_host)

    @classmethod
    def get_posts(cls, unit, oauth, host):
        endpoint = "{}/wp-json/multisite-posts/v1/posts".format(host)

        r = oauth.get(endpoint)
        result = r.json()

        print(result)

        for post in result["posts"]:

            try:
                user = User.objects.get(email__iexact=post["author"]["email"])

                post_created_time = parse_datetime("{}Z".format(post["post_date_gmt"]))

                insert_post(user=user, post_id=post["guid"], message=post["post_content"],
                            created_time=post_created_time, unit=unit, platform=cls.platform, platform_url=post["guid"])

                for comment in post["comments"]:
                    try:
                        commenter = User.objects.get(email__iexact=comment["author"]["email"])

                        comment_created_time = parse_datetime("{}Z".format(comment["comment_date_gmt"]))

                        insert_comment(user=commenter, post_id=post["guid"], comment_id=comment["comment_guid"],
                                       comment_message=comment["comment_content"],
                                       comment_created_time=comment_created_time, unit=unit,
                                       platform=cls.platform, platform_url=comment["comment_guid"], parent_user=user)

                    except User.DoesNotExist:
                        # Don't store the comment if the author doesn't exist
                        pass

            except User.DoesNotExist:
                # Do nothing if the post author doesn't exist
                pass

    def get_verbs(self):
        return self.xapi_verbs

    def get_objects(self):
        return self.xapi_objects


registry.register(WordPressPlugin)
