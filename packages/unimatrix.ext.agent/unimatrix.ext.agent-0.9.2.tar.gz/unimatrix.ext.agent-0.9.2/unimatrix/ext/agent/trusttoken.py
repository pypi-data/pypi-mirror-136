"""Declares :class:`TrustToken`."""
import urllib.parse

from unimatrix.lib import timezone


class TrustToken:
    """Represents a token that is used in an exchange with the Security Token
    Service (STS). A :class:`TrustToken` can be self-signed (the issuer must
    be preregistered at the STS) or delegated (with a self-signed actor token).
    """

    @staticmethod
    def parse_audience(exchange_url: str) -> str:
        """Parse the audience from the OAuth 2.0 Token Exchange URL."""
        p = urllib.parse.urlparse(exchange_url)
        return f'{p.scheme}://{p.netloc}'

    @classmethod
    async def generate(cls, issuer: str, audience: str, **claims):
        """Generate a new :class:`TrustToken` using the signing key defined by
        the :envvar:`OAUTH2_ACTOR_KEY` environment variable.

        If not provided, the claims ``iat``, ``exp`` and ``nbf`` are added
        to the claims.
        """
        now = timezone.now()
        claims.setdefault('exp', now + 120)
        claims.setdefault('iat', now)
        claims.setdefault('nbf', now)

    def __init__(self, issuer: str, exchange_url: str):
        """Instantiate a new :class:`TrustToken`.

        Args:
            issuer (str): the issuer that signs the :class:`TrustToken`. The
                Security Token Service (STS) will use this URL to discover the
                public signing keys.
            exchange_url (str): the URL at which the OAuth 2.0 Token Exchange
                is performed.
            **claims: additional claims to add to the token.
        """
        self.audience = self.parse_audience(exchange_url)
        self.issuer = issuer
        self.exchange_url = exchange_url
