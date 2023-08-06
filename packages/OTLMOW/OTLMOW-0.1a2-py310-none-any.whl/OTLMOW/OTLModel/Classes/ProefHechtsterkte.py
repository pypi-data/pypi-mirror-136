# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Proef import Proef
from OTLMOW.OTLModel.Datatypes.DtcDocument import DtcDocument


# Generated with OTLClassCreator. To modify: extend, do not edit
class ProefHechtsterkte(Proef):
    """Het resultaat van de trekproef waarbij een proefstuk wordt blootgesteld aan een stijgende spanning tot er een breuk optreedt."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefHechtsterkte'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        super().__init__()

        self._hechtsterkte = OTLAttribuut(field=DtcDocument,
                                          naam='hechtsterkte',
                                          label='hechtsterkte',
                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefHechtsterkte.hechtsterkte',
                                          definition='Proef om de hechtsterkte van de laag te bepalen.')

    @property
    def hechtsterkte(self):
        """Proef om de hechtsterkte van de laag te bepalen."""
        return self._hechtsterkte.waarde

    @hechtsterkte.setter
    def hechtsterkte(self, value):
        self._hechtsterkte.set_waarde(value, owner=self)
