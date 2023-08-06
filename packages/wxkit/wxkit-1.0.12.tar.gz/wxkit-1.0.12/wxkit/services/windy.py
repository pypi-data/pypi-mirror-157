from wxkit.services import WxService
from wxkit.models import ErrorModel, Wind, Temperature, Station, WeatherPoint
from wxkit.utils.httplib import retry_request, HTTP_METHOD
from wxkit.utils.mathlibs import Vector
from wxkit.utils.convertor import (
    fahrenheit_from_kelvin,
    celsius_from_fahrenheit,
)


class ForecastModel:
    AROME = "arome"
    ICONEU = "iconEu"
    GFS = "gfs"
    WAVEWATCH = "wavewatch"
    NAMCONUS = "namConus"
    NAMHAWAII = "namHawaii"
    NAMALASKA = "namAlaska"
    GEOS5 = "geos5"


class ForecastParameters:
    AROME = [
        "temp",
        "dewpoint",
        "precip",
        "convPrecip",
        "wind",
        "windGust",
        "cape",
        "ptype",
        "lclouds",
        "mclouds",
        "hclouds",
        "rh",
    ]
    ICONEU = [
        "temp",
        "dewpoint",
        "precip",
        "convPrecip",
        "snowPrecip",
        "wind",
        "windGust",
        "cape",
        "ptype",
        "lclouds",
        "mclouds",
        "hclouds",
        "rh",
        "gh",
        "pressure",
    ]
    GFS = [
        "temp",
        "dewpoint",
        "precip",
        "convPrecip",
        "snowPrecip",
        "wind",
        "windGust",
        "cape",
        "ptype",
        "lclouds",
        "mclouds",
        "hclouds",
        "rh",
        "gh",
        "pressure",
    ]
    WAVEWATCH = ["waves", "windWaves", "swell1", "swell2"]
    NAMCONUS = [
        "temp",
        "dewpoint",
        "precip",
        "convPrecip",
        "snowPrecip",
        "wind",
        "windGust",
        "cape",
        "ptype",
        "lclouds",
        "mclouds",
        "hclouds",
        "rh",
        "pressure",
    ]
    NAMHAWAII = [
        "temp",
        "dewpoint",
        "precip",
        "convPrecip",
        "snowPrecip",
        "wind",
        "windGust",
        "cape",
        "ptype",
        "lclouds",
        "mclouds",
        "hclouds",
        "rh",
        "pressure",
    ]
    NAMALASKA = [
        "temp",
        "dewpoint",
        "precip",
        "convPrecip",
        "snowPrecip",
        "wind",
        "windGust",
        "cape",
        "ptype",
        "lclouds",
        "mclouds",
        "hclouds",
        "rh",
        "pressure",
    ]
    GEOS5 = ["so2sm", "dustsm", "cosc"]


ForecastLevels = [
    "surface",
    "1000h",
    "950h",
    "925h",
    "900h",
    "850h",
    "800h",
    "700h",
    "600h",
    "500h",
    "400h",
    "300h",
    "200h",
    "150h",
]


class WindyWxService(WxService):
    ENDPOINT = "https://api.windy.com/api/point-forecast/v2"

    def __init__(self, credential):
        super().__init__(credential)

    def auth_payload(self, **kwargs):
        p = dict(key=self.credential.key)
        p.update(kwargs)
        return p

    def _modelize(self, data, location, level):
        wxs = []
        for idx, time in enumerate(data["ts"]):
            temp_k = data[f"temp-{level}"][idx]
            temp_f = fahrenheit_from_kelvin(temp_k)
            temp_c = celsius_from_fahrenheit(temp_f)
            temperature = Temperature(temp_avg=round(temp_c, 2))
            wind_x = data[f"wind_u-{level}"][idx]
            wind_y = data[f"wind_v-{level}"][idx]
            wind_vector = Vector(wind_x, wind_y)
            wind = Wind(
                speed=round(wind_vector.magnitude(), 2),
                degree=wind_vector.degree(),
            )
            pressure = round(data["pressure-surface"][idx] / 100, 2)
            humidity = round(data["rh-surface"][idx], 2)
            clouds = (
                data["lclouds-surface"][idx]
                if pressure >= 800.0
                else data["mclouds-surface"][idx]
                if 800.0 > pressure >= 450.0
                else data["hclouds-surface"][idx]
            ) / 100
            clouds = round(clouds, 2)
            snow = round(data["past3hsnowprecip-surface"][idx], 2)
            rain = round(data["past3hconvprecip-surface"][idx], 2)
            weather_point = WeatherPoint(
                station=Station(lat=location.lat, lon=location.lon, name=""),
                status="",
                description="",
                icon="",
                temp=temperature,
                pressure=pressure,
                humidity=humidity,
                rain=rain,
                wind=wind,
                clouds=clouds,
                snow=snow,
                time=time,
                raw_data=data,
            )
            wxs.append(weather_point)
        return wxs

    def get_forecast(self, location):
        model = ForecastModel.GFS
        level = ForecastLevels[0]
        payload = self.auth_payload(
            lat=location.lat,
            lon=location.lon,
            model=model,
            levels=[level],
            parameters=getattr(ForecastParameters, model.upper()),
        )
        try:
            resp_data = retry_request(HTTP_METHOD.POST, self.ENDPOINT, json=payload)
        except Exception as e:
            return self.handle_error(e)

        wxs = self._modelize(resp_data, location, level)
        return wxs

    def get_current_weather_by_location(self, location):
        wxs = self.get_forecast(location)
        if isinstance(wxs, ErrorModel):
            return wxs

        return wxs[0]

    def get_forecast_weather_by_location(self, location, period=3):
        return self.get_forecast(location)

    def handle_error(self, exception):
        error = ErrorModel()
        if getattr(exception, "response", None) is not None:
            error.code = exception.response.status_code
            error.message = exception.response.text
        else:
            error.message = str(exception)

        return error
