from abc import abstractmethod
from pydantic import BaseModel


class ConfigData(BaseModel):
    @abstractmethod
    def load_config(self):
        pass
