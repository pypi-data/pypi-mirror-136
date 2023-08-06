# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Proef import Proef
from OTLMOW.OTLModel.Datatypes.DtcDocument import DtcDocument


# Generated with OTLClassCreator. To modify: extend, do not edit
class ProefWaterdichtheid(Proef):
    """Testen van het waterverlies van het beproefde leidingsvak."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefWaterdichtheid'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        super().__init__()

        self._waterdichtheid = OTLAttribuut(field=DtcDocument,
                                            naam='waterdichtheid',
                                            label='waterdichtheid',
                                            objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefWaterdichtheid.waterdichtheid',
                                            definition='Testresultaten van het opgemeten waterverlies van het beproefde leidingsvak.')

    @property
    def waterdichtheid(self):
        """Testresultaten van het opgemeten waterverlies van het beproefde leidingsvak."""
        return self._waterdichtheid.waarde

    @waterdichtheid.setter
    def waterdichtheid(self, value):
        self._waterdichtheid.set_waarde(value, owner=self)
