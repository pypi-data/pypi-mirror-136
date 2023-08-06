# coding=utf-8
from OTLMOW.OTLModel.BaseClasses.OTLAttribuut import OTLAttribuut
from OTLMOW.OTLModel.Classes.Proef import Proef
from OTLMOW.OTLModel.Datatypes.KlLEACSchokindexMVP import KlLEACSchokindexMVP


# Generated with OTLClassCreator. To modify: extend, do not edit
class ProefSchokindexMVP(Proef):
    """Proef voor de bepaling van de schokindex parameter van de motorvangplank."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefSchokindexMVP'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    deprecated_version = '2.0.0'

    def __init__(self):
        super().__init__()

        self._schokindexMvp = OTLAttribuut(field=KlLEACSchokindexMVP,
                                           naam='schokindexMvp',
                                           label='schokindex mvp',
                                           objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#ProefSchokindexMVP.schokindexMvp',
                                           usagenote='Klasse uit gebruik sinds versie 2.0.0 ',
                                           deprecated_version='2.0.0',
                                           definition='Head Injury Criterium (HIC) van een motorvangplank.')

    @property
    def schokindexMvp(self):
        """Head Injury Criterium (HIC) van een motorvangplank."""
        return self._schokindexMvp.waarde

    @schokindexMvp.setter
    def schokindexMvp(self, value):
        self._schokindexMvp.set_waarde(value, owner=self)
