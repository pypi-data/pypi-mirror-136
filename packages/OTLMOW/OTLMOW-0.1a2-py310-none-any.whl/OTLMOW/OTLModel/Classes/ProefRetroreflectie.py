# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Proef import Proef
from OTLMOW.OTLModel.Datatypes.DtcDocument import DtcDocument


# Generated with OTLClassCreator. To modify: extend, do not edit
class ProefRetroreflectie(Proef):
    """Het bepalen van de retroreflectiecoëfficiënt via een manuele retroreflectometer of via labotesten."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefRetroreflectie'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        super().__init__()

        self._retroreflectie = OTLAttribuut(field=DtcDocument,
                                            naam='retroreflectie',
                                            label='retroreflectie',
                                            objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefRetroreflectie.retroreflectie',
                                            definition='Proef om de retroreflectie van een verkeersbord te bepalen.')

    @property
    def retroreflectie(self):
        """Proef om de retroreflectie van een verkeersbord te bepalen."""
        return self._retroreflectie.waarde

    @retroreflectie.setter
    def retroreflectie(self, value):
        self._retroreflectie.set_waarde(value, owner=self)
