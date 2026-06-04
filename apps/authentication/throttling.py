from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = "anon"


class RegistrationRateThrottle(AnonRateThrottle):
    scope = "anon"


class AuthenticatedBurstRateThrottle(UserRateThrottle):
    scope = "user_burst"
