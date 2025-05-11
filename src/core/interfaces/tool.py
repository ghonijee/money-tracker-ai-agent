from abc import abstractmethod

class Tool:
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def description(self) -> str:
        pass
    
    @abstractmethod
    def run(self, *args, **kwargs):
        pass