from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class UserBurstRateThrottle(UserRateThrottle):
    scope = "user_burst"


class UserSustainedRateThrottle(UserRateThrottle):
    scope = "user_sustained"


class AnonymousRateThrottle(AnonRateThrottle):
    scope = "anon"
