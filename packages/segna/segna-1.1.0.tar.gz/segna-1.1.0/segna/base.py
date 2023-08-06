BASE_URL = 'https://backend.segna.io/public/server-side'


class SegnaCredentials:
    def __init__(self):
        self.access_key = None
        self.secret_key = None

    def set_credentials(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key


SEGNA_CREDENTIALS = SegnaCredentials()


def init(access_key, secret_key):
    SEGNA_CREDENTIALS.set_credentials(access_key, secret_key)

