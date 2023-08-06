from wxkit.services.openweather import OpenweatherWxService
from wxkit.services.windy import WindyWxService
from wxkit.services.accuweather import AccuweatherWxService
from wxkit import models


def test_init():
    c = models.Credential(credential={"appid": "*****"})
    s = OpenweatherWxService(c)
    assert s
    c = models.Credential(credential={"key": "*****"})
    s = WindyWxService(c)
    assert s
    c = models.Credential(credential={"apikey": "*****"})
    s = AccuweatherWxService(c)
    assert s
