class MystAPIError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TopUpError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InternalServerError(MystAPIError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class BadRequestError(MystAPIError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ParameterValidationError(MystAPIError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
class RegistrationAlreadyInProgressError(MystAPIError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ServiceUnavailableError(MystAPIError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MinimumAmountError(TopUpError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)