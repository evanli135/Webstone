from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from abc import ABC, abstractclassmethod

class ObservabilityStore(ABC):
    """
    Basic Persistence Layer for an observability store
    """

class ObservabilityCollector(ABC):
    """
    Basic Collector for agentic events
    """
    
    @abstractclassmethod
    def register(self, agent):
        """
        Begin to record actions from an agent
        """
        pass

    @abstractclassmethod
    def notify(self, item):
        """
        Record an item
        """
        pass