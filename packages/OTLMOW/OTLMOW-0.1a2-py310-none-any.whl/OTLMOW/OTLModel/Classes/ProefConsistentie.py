# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Proef import Proef
from OTLMOW.OTLModel.Datatypes.DtcDocument import DtcDocument


# Generated with OTLClassCreator. To modify: extend, do not edit
class ProefConsistentie(Proef):
    """Zetmaat van betonspecie volgens NBN EN 12350-2 bij een cementbetonverharding of een lijnvormig element."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefConsistentie'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        super().__init__()

        self._consistentie = OTLAttribuut(field=DtcDocument,
                                          naam='consistentie',
                                          label='consistentie',
                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefConsistentie.consistentie',
                                          definition='Proefresultaten van de consistentie.')

    @property
    def consistentie(self):
        """Proefresultaten van de consistentie."""
        return self._consistentie.waarde

    @consistentie.setter
    def consistentie(self, value):
        self._consistentie.set_waarde(value, owner=self)
