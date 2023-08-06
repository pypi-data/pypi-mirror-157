"""Funpinpin cli app open."""


class Open(object):
    """Open Module."""

    def __init__(self, proj):
        """Init."""
        self.proj = proj

    def run(self):
        """Run function."""
        env_file = self.proj.env
        host = env_file.HOST
        shop = env_file.SHOP
        return shop, host
