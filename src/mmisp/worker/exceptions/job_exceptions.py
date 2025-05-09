from typing import Self


class JobException(Exception):
    """
    Exception raised when an error occurred while processing a job
    """

    def __init__(
        self: Self, job_id: str | None = None, message: str = "An error occurred while processing the Job"
    ) -> None:
        self.message: str
        if job_id:
            self.message = f"An error occurred while processing the Job with id: {job_id}"
        else:
            self.message = message
        super().__init__(self.message)


class NotExistentJobException(Exception):
    """
    Exception raised when a requested job does not exist
    """

    def __init__(self: Self, job_id: str | None = None, message: str = "The requested Job does not exist") -> None:
        self.message: str
        if job_id is None:
            self.message = message
        else:
            self.message = f"The requested job with id: {job_id} does not exist"
        super().__init__(self.message)


class JobNotFinishedException(Exception):
    """
    Exception raised when a requested job is not finished yet
    """

    def __init__(
        self: Self, job_id: str | None = None, message: str = "The Job is not finished yet, please try again later"
    ) -> None:
        self.message: str
        if job_id is None:
            self.message = message
        else:
            self.message = f"The Job with id: {job_id} is not finished yet, please try again later"

        super().__init__(self.message)


class JobHasNoResultException(Exception):
    """
    Exception raised when a requested job has no result that can be returned
    """

    def __init__(
        self: Self,
        job_id: str | None = None,
        job_type: str | None = None,
        message: str = "The requestet Jobtype has no result that can be returned",
    ) -> None:
        self.message: str
        if job_id is None and job_type is None:
            self.message = message
        elif job_id is None:
            self.message = f"The requested Job of type {job_type} has no result that can be returned"
        elif job_type is None:
            self.message = f"The requested Job with id: {job_id} has no result that can be returned"
        else:
            self.message = (
                f"The requested Job with id: {job_id} is of type {job_type}, which has no result that can be returned"
            )
        super().__init__(self.message)
