def humidity_from_dewpoint(fa, fdp):
    """Simple approximation of relative humidity formular

    Args:
        fa (float): The temperature of air in fahrenheit
        fdp (float): The temperature of dew point in fahrenheit

    Returns:
        float: The relative humidity
    """

    relative_humidity = 100 - 5 * (5 / 9) * (fa - fdp)
    return relative_humidity


def kelvin_from_fahrenheit(f):
    return (f + 459.67) * (5 / 9)


def fahrenheit_from_kelvin(k):
    return k * (9 / 5) - 459.67


def celsius_from_fahrenheit(f):
    return (5 / 9) * (f - 32)


def fahrenheit_from_celsius(c):
    return c * (9 / 5) + 32


def mps_to_kph(v):
    return v / (1000 / 3600)


def kph_to_mps(v):
    return v * (1000 / 3600)
