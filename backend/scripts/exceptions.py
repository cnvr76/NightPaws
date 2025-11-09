from fastapi import status


class CustomException(Exception):
    def __init__(self, detail: str, status_code: int):
        self.detail: str = detail
        self.status_code: int = status_code
        super().__init__(self.detail)


# --- AUTH exceptions ---
class UserAlreadyExists(CustomException):
    def __init__(self):
        self.detail = "User already exists"
        super().__init__(self.detail, status.HTTP_409_CONFLICT)

# so info can't be added for non-existing user (not signed-up one)
class UserDoesntExist(CustomException):
    def __init__(self):
        self.detail: str = "User needs to be signed-up to before creating data for him"
        super().__init__(self.detail, status.HTTP_404_NOT_FOUND)

class InvalidCredentials(CustomException):
    def __init__(self):
        self.detail: str = "Incorrect email or password"
        super().__init__(self.detail, status.HTTP_401_UNAUTHORIZED)
    
class RefreshTokenExpired(CustomException):
    def __init__(self):
        self.detail: str = "Refresh token expired or not found"
        super().__init__(self.detail, status.HTTP_401_UNAUTHORIZED)
    
class CredentialsValidationError(CustomException):
    def __init__(self):
        self.detail: str = "Could not validate credentials"
        super().__init__(self.detail, status.HTTP_401_UNAUTHORIZED)


# -- APPLICATION exceptions ---
class ApplicationAlreadyExists(CustomException):
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_403_FORBIDDEN)


# --- GMAIL exceptions ---
class GmailRefreshTokenMissing(CustomException):
    def __init__(self):
        self.detail: str = "User was not given a gmail refresh token"
        super().__init__(self.detail, status.HTTP_401_UNAUTHORIZED)

class UnableToDecryptGmailRefreshToken(CustomException):
    def __init__(self):
        self.detail: str = "Unable to decrypt gmail token"
        super().__init__(self.detail, status.HTTP_409_CONFLICT)


class InvalidCRONSecret(CustomException):
    def __init__(self):
        self.detail: str = "Invalid CRON secret"
        super().__init__(self.detail, status.HTTP_401_UNAUTHORIZED)