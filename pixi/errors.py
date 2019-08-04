class PixiError(Exception):
    pass


class GoAuthenticate(PixiError):
    pass


class InvalidConfig(PixiError):
    pass


class InvalidURL(PixiError):
    pass


class DownloadFailed(PixiError):
    pass


class DuplicateImage(PixiError):
    pass
