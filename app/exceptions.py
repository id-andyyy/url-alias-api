class UserAlreadyExistsError(Exception):
    pass


class UserCreateError(Exception):
    pass


class ShortIdGenerationError(Exception):
    pass


class LinkCreateError(Exception):
    pass


class LinkNotFoundError(Exception):
    pass


class LinkUpdateError(Exception):
    pass


class ClickLogError(Exception):
    pass
