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

    @abstractmethod 
    def get_args_schema(self):
        pass
    
    @abstractmethod
    def output_schema(self):
        pass