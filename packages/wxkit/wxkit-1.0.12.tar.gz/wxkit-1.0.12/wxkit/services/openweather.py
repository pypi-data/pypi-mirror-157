import statistics
from copy import deepcopy

from wxkit.services import WxService
from wxkit.models import ErrorModel, Wind, Temperature, Station, WeatherPoint
from wxkit.utils.httplib import retry_request, urljoin, HTTP_METHOD


def strip_data(obj):
    """
    For some data, eg. rain, snow and clouds, the data structure of forecast weather is
    different from current weather.
    In order unified the difference, strip the data without the redundant key.
    """

    keywords = ("1h", "3h")
    if isinstance(obj, dict):
        for kw in keywords:
            try:
                val = obj[kw]
                return val
            except KeyError:
                pass

    return obj


class OpenweatherWxService(WxService):
    _CREDENTIAL_KEY = "appid"
    ENDPOINT = "https://api.openweathermap.org/data/2.5"
    PATH_CURRENT_WEATHER = ("weather",)
    PATH_FORECAST_3_HOURLY = ("forecast",)
    PATH_FORECAST_HOURLY = ("forecast", "hourly")
    FORECAST_PERIOD = (1, 3, 24)

    def __init__(self, credential):
        super().__init__(credential)

    def auth_params(self, **params):
        p = dict(appid=self.credential.appid)
        p.update(params)
        return p

    def _modelize(self, data):
        coord = data.get("coord", {})
        name = data.get("name", "")
        station = Station(lat=coord.get("lat", 0), lon=coord.get("lon", 0), name=name)
        temperature = Temperature(
            temp_avg=data.get("main", {}).get("temp", 0),
            temp_min=data.get("main", {}).get("temp_min", 0),
            temp_max=data.get("main", {}).get("temp_max", 0),
        )
        wind = Wind(
            speed=data.get("wind", {}).get("speed", 0),
            degree=data.get("wind", {}).get("deg", 0),
        )
        try:
            wx = data["weather"][0]
            status = wx.get("main", "")
            description = wx.get("description", "")
            icon = wx.get("icon", "")
        except Exception:
            status = ""
            description = ""
            icon = ""

        pressure = data.get("main", {}).get("pressure", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        rain = data.get("rain", 0)
        clouds = data.get("clouds", {}).get("all", 0)
        snow = data.get("snow", 0)
        time = data.get("dt", 0)
        weather_point = WeatherPoint(
            station=station,
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

    def get_current_weather_by_location(self, location):
        url = urljoin(self.ENDPOINT, *self.PATH_CURRENT_WEATHER)
        params = self.auth_params(lat=location.lat, lon=location.lon, units="metric")
        try:
            resp_data = retry_request(
                HTTP_METHOD.GET, url, params=params, object_hook=strip_data
            )
        except Exception as e:
            return self.handle_error(e)
        return self._modelize(resp_data)

    def get_forecast_weather_by_location(self, location, period=3):
        if period not in self.FORECAST_PERIOD:
            return self.handle_error(f"Missing weather forecast per {period} hours")

        period_alias = (
            self.PATH_FORECAST_HOURLY if period == 1 else self.PATH_FORECAST_3_HOURLY
        )
        url = urljoin(self.ENDPOINT, *period_alias)
        params = self.auth_params(lat=location.lat, lon=location.lon, units="metric")
        try:
            resp_data = retry_request(
                HTTP_METHOD.GET, url, params=params, object_hook=strip_data
            )
        except Exception as e:
            return self.handle_error(e)

        coord = resp_data.get("city", {}).get("coord", {})
        name = resp_data.get("city", {}).get("name", "")
        data_collection = []
        for data in resp_data.get("list"):
            data.update(coord=coord, name=name)
            data_collection.append(self._modelize(data))

        # NOTE: Resampling daily weather forecast from per 3 hours.
        if period == 24:
            data_collection = self.resample_daily_wxs(data_collection)

        return data_collection

    def resample_daily_wxs(self, wxs):
        ONE_DAY_HOUR = 24
        delta_hour = (wxs[1].time - wxs[0].time) / 3600
        samples = int(ONE_DAY_HOUR / delta_hour)
        r_wxs = []
        for i in range(0, len(wxs), samples):
            temp_avg = []
            temp_min = []
            temp_max = []
            for wx in wxs[slice(i, (i + 1) * samples)]:
                temp_avg.append(wx.temp.temp_avg)
                temp_min.append(wx.temp.temp_min)
                temp_max.append(wx.temp.temp_max)

            r_wx = deepcopy(wxs[i])
            r_wx.temp.temp_avg = round(statistics.mean(temp_avg), 2)
            r_wx.temp.temp_min = round(statistics.mean(temp_min), 2)
            r_wx.temp.temp_max = round(statistics.mean(temp_max), 2)
            r_wxs.append(r_wx)

        return r_wxs

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
