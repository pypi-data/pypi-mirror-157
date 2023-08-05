from elasticsearch import Elasticsearch
from fastapi import FastAPI, Depends, status
from bdating_common.model import HealthResponse, ConsumerProfile
from pydantic import BaseSettings
import os
from fastapi.security import HTTPBearer

from elasticsearch.exceptions import NotFoundError
from fastapi.encoders import jsonable_encoder
from bdating_common.auth0_token_helper import IllegalTokenExcpetion, Auth0TokenVerifier
from fastapi.responses import JSONResponse
from bdating_common.es_helper import es_get_result_to_dict
from fastapi.middleware.cors import CORSMiddleware


class Settings(BaseSettings):
    app_name: str = 'StandardBdatingAPI'
    app_namespace: str = os.getenv('NAMESPACE', "")
    admin_email: str = "admin@bdating.io"
    app_type: str = 'consumer'
    es_endpoint: str = os.getenv('ELASTICSEARCH_HOSTS')
    es_index: str = 'bdating'
    auth0_namespace: str = 'https://app.bdating.io/'
    redis_host: str = os.getenv('REDIS_HOST')
    redis_port: int = 6379
    cors_origins: str = os.getenv('CORS_ORIGINS', 'http://localhost:3000')


settings = Settings()
token_auth_scheme = HTTPBearer()
token_verifier = Auth0TokenVerifier()


def get_wallet(token: str, token_verifier: object):
    try:
        result = token_verifier.verify(token.credentials)
        if result.get("status") == 'error':
            raise IllegalTokenExcpetion()
        return result.get(f"{settings.auth0_namespace}wallet")
    except Exception as e:
        raise IllegalTokenExcpetion(e)


def create_app():
    app = FastAPI(title=settings.app_name)
    es = Elasticsearch(settings.es_endpoint)

    @ app.get("/health", response_model=HealthResponse)
    def get_health():
        return {"status": "OK"}

    @app.exception_handler(NotFoundError)
    async def es_not_found_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"detail": "Not found"}),)

    @app.exception_handler(IllegalTokenExcpetion)
    async def illegal_Auth0_token_exception_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=jsonable_encoder({"detail": "Illegal token"}),)

    @app.get("/me")
    def get_own_profile_info(token: str = Depends(token_auth_scheme)):
        """
        Find this user's own profile info.
        """
        wallet = get_wallet(token, token_verifier)
        return es_get_result_to_dict(es.get(index=settings.es_index, id=f"{wallet}:{settings.app_type}"))

    @app.patch("/me")
    def update_own_profile_info(profile: ConsumerProfile,):
        """
        Update the profile for the user.
        If the profile does not exist, create it in the first place.
        """
        profile = jsonable_encoder(profile)
        wallet = get_wallet(token, token_verifier)
        return es.update(index=settings.es_index, id=f"{wallet}:{settings.app_type}", doc_as_upsert=True, doc=profile)

    if settings.cors_origins:
        origins = settings.cors_origins.split(',')
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    return app
