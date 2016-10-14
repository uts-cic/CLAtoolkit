from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from common.CLRecipe import CLRecipe
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin
from requests_oauthlib import OAuth1, OAuth1Session
from dataintegration.models import PlatformConfig
from clatoolkit.models import UnitOffering, UnitOfferingMembership
import requests
import os


class WordPressPlugin(DIBasePlugin, DIPluginDashboardMixin):
    platform = CLRecipe.PLATFORM_WORDPRESS

    xapi_verbs = ['created', 'commented']
    xapi_objects = ['Note']

    user_api_association_name = "WP username"

    def __init__(self):
        self.client_key = os.environ.get("WORDPRESS_KEY")
        self.client_secret = os.environ.get("WORDPRESS_SECRET")
        self.wp_root = os.environ.get("WORDPRESS_ROOT")

    def start_authentication(self, request):
        request_token_url = "{}/oauth1/request".format(self.wp_root)
        base_authorization_url = "{}/oauth1/authorize".format(self.wp_root)
        callback_uri = "{}://{}{}authorize".format(request.scheme, request.get_host(), request.path)

        oauth = OAuth1Session(self.client_key, self.client_secret, callback_uri)
        fetch_response = oauth.fetch_request_token(request_token_url)

        temp_token = fetch_response.get('oauth_token')
        temp_secret = fetch_response.get('oauth_token_secret')

        # Save credentials to the session as they will need to be reused in the authorization step
        request.session["wp_temp_token"] = temp_token
        request.session["wp_temp_secret"] = temp_secret
        request.session["wp_temp_unit"] = request.GET["unit"]

        authorization_url = oauth.authorization_url(base_authorization_url, oauth_callback=callback_uri)

        return HttpResponseRedirect(authorization_url)

    def authorize(self, request):
        access_token_url = "{}/oauth1/access".format(self.wp_root)

        verifier = request.GET['oauth_verifier']

        oauth = OAuth1Session(self.client_key,
                              client_secret=self.client_secret,
                              resource_owner_key=request.session["wp_temp_token"],
                              resource_owner_secret=request.session["wp_temp_secret"],
                              verifier=verifier)
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        config_dict = {
            "access_token_key": oauth_tokens.get('oauth_token'),
            "access_token_secret": oauth_tokens.get('oauth_token_secret')
        }

        unit_id = request.session["wp_temp_unit"]

        try:
            unit = UnitOffering.objects.get(id=unit_id)
        except UnitOffering.DoesNotExist:
            raise Http404

        if UnitOfferingMembership.is_admin(request.user, unit):
            config = PlatformConfig(unit=unit, config=config_dict, platform=self.platform)
            config.save()
        else:
            raise PermissionDenied

        return HttpResponseRedirect("/")

    def perform_import(self, retrieval_param, unit):
        pass
