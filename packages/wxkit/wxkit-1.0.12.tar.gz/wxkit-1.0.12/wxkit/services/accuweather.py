from collections import defaultdict
from itertools import repeat


from wxkit.services import WxService
from wxkit.models import ErrorModel, Wind, Temperature, Station, WeatherPoint

# from wxkit.utils.http_request import retry_request, urljoin, HTTP_METHOD
from wxkit.utils.httplib import retry_request, urljoin, HTTP_METHOD
from wxkit.utils.convertor import kph_to_mps


class PERIOD_UNIT:
    DAY = "day"
    HOUR = "hour"


def strip_data(obj):
    """
    For some data in current weather condition, eg. temperature, the data value includes
        unit in Metric and Imperial.
    In order to handle data simply, strip the data with the Metric keyword.
    """

    keyword = "Metric"
    if isinstance(obj, dict):
        try:
            obj.update(obj[keyword])
        except KeyError:
            pass

    return obj


class AccuweatherWxService(WxService):
    ENDPOINT = "http://dataservice.accuweather.com"
    FORECAST_SAMPLES = {
        PERIOD_UNIT.DAY: (1, 5, 10, 15),
        PERIOD_UNIT.HOUR: (1, 12, 24, 72, 120, 5, 10, 15),
    }

    def __init__(self, credential):
        super().__init__(credential)
        self.LOCATION_CACHE = defaultdict(dict)

    def auth_params(self, **params):
        p = dict(apikey=self.credential.apikey)
        p.update(params)
        return p

    def as_station(self, data):
        coord = data.get("GeoPosition", {})
        return Station(
            lat=coord.get("Latitude", 0),
            lon=coord.get("Longitude", 0),
            name=data.get("EnglishName", ""),
        )

    def _modelize(self, data, location):
        location_data = self.get_location(location)
        temp = data.get("Temperature", {}).get("Value", 0)
        temperature = Temperature(temp_avg=temp)
        speed = data.get("Wind", {}).get("Speed", {}).get("Value", 0)
        wind = Wind(
            speed=round(kph_to_mps(speed), 2),
            degree=data.get("Wind", {}).get("Direction", {}).get("Degrees", 0),
        )
        try:
            status = data.get("WeatherText", "") or data.get("IconPhrase", "")
            description = data.get("WeatherText", "") or data.get("IconPhrase", "")
            icon = data.get("WeatherIcon", "")
        except Exception:
            status = ""
            description = ""
            icon = ""

        pressure = data.get("Pressure", {}).get("Value", 0)
        humidity = data.get("RelativeHumidity", 0)
        rain = data.get("PrecipitationProbability", 0)
        snow = data.get("SnowProbability", 0)
        clouds = data.get("CloudCover", 0)
        time = data.get("EpochTime", 0) or data.get("EpochDateTime", 0)
        weather_point = WeatherPoint(
            station=self.as_station(location_data),
            status=status,
            description=description,
            icon=icon,
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
        return weather_point

    def get_location(self, location):
        if self.LOCATION_CACHE[location]:
            return self.LOCATION_CACHE[location]

        url = urljoin(
            self.ENDPOINT,
            "locations",
            "v1",
            "cities",
            "geoposition",
            "search",
        )
        params = self.auth_params(q=f"{location.lat},{location.lon}")
        try:
            resp_data = retry_request(HTTP_METHOD.GET, url, params=params)
            self.LOCATION_CACHE[location] = resp_data
        except Exception as e:
            return self.handle_error(e)

        return resp_data

    def get_current_weather_by_location(self, location):
        location_data = self.get_location(location)
        if isinstance(location_data, ErrorModel):
            return location_data

        url = urljoin(
            self.ENDPOINT,
            "currentconditions",
            "v1",
            location_data.get("Key", ""),
        )
        params = self.auth_params(details=True)
        try:
            resp_data = retry_request(
                HTTP_METHOD.GET, url, params=params, object_hook=strip_data
            )
        except Exception as e:
            return self.handle_error(e)
        wxs = list(map(self._modelize, resp_data, repeat(location)))
        return wxs[0]

    def get_forecast_weather_by_location(
        self, location, period=1, samples=12, unit=PERIOD_UNIT.HOUR
    ):
        if unit == PERIOD_UNIT.DAY:
            forecast_type = "daily"
        elif unit == PERIOD_UNIT.HOUR:
            forecast_type = "hourly"
        else:
            return self.handle_error(
                f"Invalid period unit, must in {PERIOD_UNIT.DAY}, {PERIOD_UNIT.HOUR}"
            )

        forecast_samples = period * samples
        if forecast_samples not in self.FORECAST_SAMPLES.get(unit):
            return self.handle_error(f"Missing weather forecast for {forecast_samples}")

        location_data = self.get_location(location)
        if isinstance(location_data, ErrorModel):
            return location_data

        url = urljoin(
            self.ENDPOINT,
            "forecasts",
            "v1",
            forecast_type,
            f"{forecast_samples}{unit}",
            location_data.get("Key", ""),
        )
        params = self.auth_params(details=True, metric=True)
        try:
            resp_data = retry_request(HTTP_METHOD.GET, url, params=params)
        except Exception as e:
            return self.handle_error(e)

        wxs = list(map(self._modelize, resp_data, repeat(location)))
        return wxs

    def handle_error(self, exception):
        error = ErrorModel()
        if getattr(exception, "response", None) is not None:
            try:
                # Get error context from HTTP error if response.
                response = exception.response.json()
                error.code = response["cod"]
                error.message = response["message"]
                error.raw_data = response
            except Exception:
                error.code = exception.response.status_code
                error.message = exception.response.text
        else:
            error.message = str(exception)

        return error
