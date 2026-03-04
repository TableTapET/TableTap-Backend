class BaseService:
    """
    All services inherit from this. Enforces that services are
    instantiated with the request user for audit/scoping purposes.
    """

    def __init__(self, user):
        self.user = user
