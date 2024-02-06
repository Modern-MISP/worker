from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


def verified(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    if credentials is not None:
        if credentials.credentials == "mayo":
            return
    raise HTTPException(status_code=403, detail="authentication failed")
