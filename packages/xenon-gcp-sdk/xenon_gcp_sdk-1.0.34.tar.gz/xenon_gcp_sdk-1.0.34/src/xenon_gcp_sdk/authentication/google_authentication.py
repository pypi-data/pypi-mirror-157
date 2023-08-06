import ast
import json

from ..secretmanager import secret_manager_service
from oauth2client.service_account import ServiceAccountCredentials as Credentials
from google.oauth2.credentials import Credentials as OauthCred

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
wrong_scopes = ['https://www.googleapis.com/auth/calendar']


def get_credentials(user_identifier, delegated=False):
    scopes = wrong_scopes if user_identifier.organization_id == '5be9861a-2883-4db1-86a0-49da48838c14' else SCOPES
    credentials = Credentials.from_json_keyfile_dict(
        json.loads(secret_manager_service.get_secret('service_account_credentials')), scopes=scopes)
    # if not user_identifier.auth_token else OauthCred.from_authorized_user_info(
    # _build_oauth_cred(user_identifier.auth_token))
    return credentials if not delegated else credentials.create_delegated(user_identifier.email)


def _build_oauth_cred(oauth_token):
    oauth_client = ast.literal_eval(secret_manager_service.get_secret('oauth_client')).get('web')
    return {
        'token': oauth_token.get('token', ''),
        'refresh_token': oauth_token.get('refresh_token', ''),
        'token_uri': oauth_token.get('token_uri', ''),
        'client_id': oauth_client.get('client_id'),
        'client_secret': oauth_client.get('client_secret'),
        'scopes': SCOPES}
