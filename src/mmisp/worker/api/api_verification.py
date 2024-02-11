from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mmisp.worker.config.system_config_data import system_config_data


def verified(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    """
    A function to verify the api key that is sent by the client
    if the api key is not correct, it will raise an HTTPException

    :param credentials: credentials sent by the client
    :type credentials: HTTPAuthorizationCredentials
    """
    if credentials is not None:
        if credentials.credentials == system_config_data.api_key:
            return
    raise HTTPException(status_code=403, detail="authentication failed")
