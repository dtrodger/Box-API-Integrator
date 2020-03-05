class PrometheusException(Exception):
    pass


class PrometheusTypeError(TypeError):
    pass


class PrometheusValueError(ValueError):
    pass


class PrometheusInvalidHTTPMethodError(PrometheusValueError):
    pass


class PrometheusFileError(PrometheusException):
    pass
