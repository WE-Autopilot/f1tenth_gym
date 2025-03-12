from abc import ABC, abstractmethod

class AbstractController(ABC):
    @abstractmethod
    def startup(self)->None:
        pass

    @abstractmethod
    def compute(obs: dict)->tuple[2 | 3]:
        '''
        This should return the speed, steering angle, and optionally current set of waypoints to be rendered.
        NOTE if you do not want to provide a set of waypoints, return none for the third parameter.
        '''

        pass
    
    @abstractmethod
    def shutdown(self)->None:
        pass