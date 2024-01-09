from pydantic import BaseModel


class NotExistentJobException(BaseModel):
    message: str = "Job does not exist"


class JobNotFinishedException(BaseModel):
    message: str = "Job is not finished yet, please try again later"


class JobHasNoResultException(BaseModel):
    message: str = "Jobtype has no result that can be returned"
