from http.server import BaseHTTPRequestHandler

from util.http import returnErrorUIToUA, sendRedirectAndErrorToClient
from util.client import getClientById
from util.user import is_authorization_code_valid

'''
認可リクエスト
  GET /authorize?response_type=code&client_id=s6BhdRkqt3&state=xyz
        &redirect_uri=https%3A%2F%2Fclient%2Eexample%2Ecom%2Fcb HTTP/1.1
    Host: server.example.com
'''
def checkAuthorizationRequest(context:BaseHTTPRequestHandler,query_components:dict[str, list[str]])->bool:
    registeredClient=getClientById(query_components.get('client_id', [None])[0])
    state=query_components.get('state', [None])[0]
    if registeredClient is None:
        returnErrorUIToUA(context, "invalid_client_id",
             "The client is not authorized to request an authorization code using this method."
        )
        return
    redirect_uri = query_components.get('redirect_uri', [None])[0]
    if redirect_uri is None or not redirect_uri.startswith(registeredClient[1]):
        returnErrorUIToUA(context=context, error="invalid_request",
                              error_description="The redirect_uri is invalid.")
        return False
    if query_components.get('response_type', [None])[0] != 'code':
        sendRedirectAndErrorToClient(context, "unsupported_response_type", "The authorization server does not support obtaining an authorization code using this method.", redirect_uri, state)
        return False

    requested_scope = query_components.get('scope', [None])[0]
    if requested_scope is None or not set(requested_scope.split()).issubset(set(registeredClient[2].split(' '))):
        sendRedirectAndErrorToClient(context, "invalid_scope", "The requested scope is invalid, unknown, or malformed.",redirect_uri=redirect_uri,state=state)
        return False
    return True
'''
アクセストークンリクエスト
 POST /token HTTP/1.1
     Host: server.example.com
     Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW
     Content-Type: application/x-www-form-urlencoded

     grant_type=authorization_code&code=SplxlOBeZQQYbYS6WxSbIA
     &redirect_uri=https%3A%2F%2Fclient%2Eexample%2Ecom%2Fcb
'''
def checkAccessTokentRequest(context:BaseHTTPRequestHandler,query_components:dict[str, list[str]])->bool:
    registeredClient=getClientById(query_components.get('client_id', [None])[0])
    redirect_uri = query_components.get('redirect_uri', [None])[0]
    if redirect_uri is None or not redirect_uri.startswith(registeredClient[1]):
        returnErrorUIToUA(context=context, error="invalid_request",
                              error_description="The redirect_uri is invalid.")
        return False
    if query_components.get('grant_type', [None])[0]!="authorization_code":
        returnErrorUIToUA(context,error="invalid grant_type",error_detail="We support only authorization_code")
        return False
    if not is_authorization_code_valid(query_components.get('username', [''])[0],code=query_components.get('code', [''])[0]):
        returnErrorUIToUA(context,error="invalid grant_type",error_detail="We support only authorization_code")
        return False
    return True