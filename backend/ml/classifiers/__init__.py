from .pytorch_base import PyTorchClassifier
from .cnnspot import CNNSpotClassifier
from .effort import EffortClassifier
from .npr import NPRClassifier
from .vib import VIBClassifier

__all__ = [
    'PyTorchClassifier',
    'CNNSpotClassifier',
    'EffortClassifier',
    'NPRClassifier',
    'VIBClassifier',
]
