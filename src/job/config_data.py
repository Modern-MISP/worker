from abc import abstractmethod
from pydantic import BaseModel

class configData(BaseModel):
    @abstractmethod
    def load_config(self):
        pass
