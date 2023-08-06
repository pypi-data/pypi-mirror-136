# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from abc import abstractmethod
from OTLMOW.OTLModel.Classes.AIMNaamObject import AIMNaamObject


# Generated with OTLClassCreator. To modify: extend, do not edit
class VerkeersregelaarModule(AIMNaamObject):
    """Abstracte voor de verschillende modules waaruit een verkeersregelaar opgebouwd is."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#VerkeersregelaarModule'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    @abstractmethod
    def __init__(self):
        super().__init__()
