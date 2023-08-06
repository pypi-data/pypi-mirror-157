from munzee.endpoint import _Endpoint


class Players(_Endpoint):
    """Endpoint class for players."""

    endpoint = "user"

    def get_current_player(self):
        """
        Get the user's profile.
        """
        return self.GET("current")
