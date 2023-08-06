# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Proef import Proef
from OTLMOW.OTLModel.Datatypes.DtcDocument import DtcDocument


# Generated with OTLClassCreator. To modify: extend, do not edit
class ProefDruksterkte(Proef):
    """De spanning waarbij het materiaal van de laag onder invloed van (druk)belasting bezwijkt."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefDruksterkte'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        super().__init__()

        self._druksterkte = OTLAttribuut(field=DtcDocument,
                                         naam='druksterkte',
                                         label='druksterkte',
                                         objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefDruksterkte.druksterkte',
                                         definition='Proefresultaten van de druksterkte van de laag.')

    @property
    def druksterkte(self):
        """Proefresultaten van de druksterkte van de laag."""
        return self._druksterkte.waarde

    @druksterkte.setter
    def druksterkte(self, value):
        self._druksterkte.set_waarde(value, owner=self)
