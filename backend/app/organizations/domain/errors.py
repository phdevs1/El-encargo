class OrganizationsDomainError(Exception):
    pass


class LocationNotFound(OrganizationsDomainError):
    def __init__(self, slug: str):
        self.slug = slug
        super().__init__(f"Location not found: {slug!r}")
