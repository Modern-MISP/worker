class JobException(Exception):
    """
    Exception raised when an error occurred while processing a Job
    """

    def __init__(self, job_id: str = None, message="An error occurred while processing the Job"):
        if job_id:
            self.message = f"An error occurred while processing the Job with id: {job_id}"
        else:
            self.message = message
        super().__init__(self.message)


class NotExistentJobException(Exception):
    """
    Exception raised when a requested Job does not exist
    """

    def __init__(self, job_id: str = None, message="The requested Job does not exist"):
        if job_id is None:
            self.message = message
        else:
            self.message = f"The requested job with id: {job_id} does not exist"
        super().__init__(self.message)


class JobNotFinishedException(Exception):
    """
    Exception raised when a requested Job is not finished yet
    """

    def __init__(self, job_id: str = None, message="The Job is not finished yet, please try again later"):
        if job_id is None:
            self.message = message
        else:
            self.message = f"The Job with id: {job_id} is not finished yet, please try again later"

        super().__init__(self.message)


class JobHasNoResultException(Exception):
    """
    Exception raised when a requested Job has no result that can be returned
    """

    def __init__(self, job_id: str = None, job_type: str = None, message="The requestet Jobtype has no result that can "
                                                                         "be returned"):
        if job_id is None and job_type is None:
            self.message = message
        elif job_id is None:
            self.message = f"The requested Job of type {job_type} has no result that can be returned"
        elif job_type is None:
            self.message = f"The requested Job with id: {job_id} has no result that can be returned"
        else:
            self.message = (f"The requested Job with id: {job_id} is of type {job_type}, which has no result that can "
                            f"be returned")
        super().__init__(self.message)
