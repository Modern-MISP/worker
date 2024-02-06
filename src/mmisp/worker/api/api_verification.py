from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mmisp.worker.system_config_data import system_config_data


def verified(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    if credentials is not None:
        if credentials.credentials == system_config_data.api_key:
            return
    raise HTTPException(status_code=403, detail="authentication failed")
