""""""

import time
from urllib.parse import urlencode

import requests

from mercadolibre.utils import wait_for_request

from .error import Error
from .exceptions import InvalidSite
from .response import Response


class MercadoLibre(object):
    """_summary_

    Raises:
        InvalidSite: _description_
        Error: _description_
    """
    auth_urls = {
        'MLA': "https://auth.mercadolibre.com.ar",  # Argentina
        'MLB': "https://auth.mercadolivre.com.br",  # Brasil
        'MCO': "https://auth.mercadolibre.com.co",  # Colombia
        'MCR': "https://auth.mercadolibre.com.cr",  # Costa Rica
        'MEC': "https://auth.mercadolibre.com.ec",  # Ecuador
        'MLC': "https://auth.mercadolibre.cl",  # Chile
        'MLM': "https://auth.mercadolibre.com.mx",  # Mexico
        'MLU': "https://auth.mercadolibre.com.uy",  # Uruguay
        'MLV': "https://auth.mercadolibre.com.ve",  # Venezuela
        'MPA': "https://auth.mercadolibre.com.pa",  # Panama
        'MPE': "https://auth.mercadolibre.com.pe",  # Peru
        'MPT': "https://auth.mercadolibre.com.pt",  # Prtugal
        'MRD': "https://auth.mercadolibre.com.do"  # Dominicana
    }

    def __init__(self, client_id, client_secret, site_id='MLA'):
        """
        """
        self.client_id = client_id if client_id else None
        self.client_secret = client_secret if client_secret else None
        self.site_id = site_id
        self.access_token = None
        self._refresh_token = None
        self.expires_in = None
        self.expires_at = None
        self.user_id = None
        self._session = requests.Session()
        self._base_url = 'https://api.mercadolibre.com'

    def authorization_url(self, redirect_uri: str):
        """_summary_

        Args:
            redirect_uri (str)

        Returns:
            str: url for code authentication
        """
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri
        }

        try:
            auth_url = self.auth_urls[self.site_id]
        except KeyError as err:
            raise InvalidSite(err) from None
        return auth_url + '/authorization?' + urlencode(params)

    def _set_token(self, response):
        data = response.data
        if 'expires_in' in data:
            expires_in = data['expires_in']
            expires_at = time.time() + int(expires_in)
            self.expires_in = expires_in
            self.expires_at = expires_at
            self.access_token = data['access_token']
            self.user_id = data['user_id']
            # self._refresh_token = data['refresh_token']
        return response

    def _get_access_token(self, redirect_uri):
        """Changing authorization code to access token."""

        response = requests.get(self.authorization_url(redirect_uri))
        code = wait_for_request(response.url)

        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }

        return self._post('/oauth/token', params=params)

    def authenticate(self, redirect_uri: str):
        """
        Authenticate from authentication url to
        obtain AUTH CODE and exchange to ACCESS_TOKEN

        Args:
            redirect_uri (str)

        Returns:
            Response
        """
        return self._set_token(self._get_access_token(redirect_uri))

    def refresh_token(self):
        """Request new access_token with refresh_token

        Returns:
            Response
        """
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token,
        }
        return self._set_token(self._post('/oauth/token', params=params))

    def _request(self, method, path, **kwargs):
        """
        Private function.
        Try to make request based on given parameters.
        Return Response object if success or throw an exception if error occur.

        Args:
            method (string): HTTP Method
            url (string): relative path to make request
        """

        if self.access_token:
            self._session.headers = {
                'x-format-new': 'true',
                'Authorization': f'Bearer {self.access_token}'
            }

        url = self._base_url + path
        try:
            res = self._session.request(method, url, **kwargs)
            res.raise_for_status()
        except (requests.ConnectionError, requests.HTTPError) as error:
            raise Error(error) from None

        return Response(res)

    def _get(self, path: str, **kwargs):
        return self._request('GET', path, **kwargs)

    def _post(self, path: str, **kwargs):
        return self._request('POST', path, **kwargs)

    def get_seller(self, seller_id):
        """Get seller based on seller id

        Args:
            seller_id (string)

        Returns:
            Response (object)
        """

        return self._get(f'/users/{seller_id}/')

    def get_seller_name(self, seller_id):
        """Get seller name based on seller id

        Args:
            seller_id (string)

        Returns:
            seller_name (string): seller name
        """

        res = self.get_seller(seller_id)
        data = res.data

        return data['nickname']

    def get_product(self, product_id):
        """Get product based on product id

        Args:
            product_id (string)

        Returns:
            Response (object)
        """

        return self._get(f'/items/{product_id}/')

    def search_items(self, params: dict):
        """Search items

        Args:
            params (dict): keys options are: category, q, nickname, seller_id
        Returns:
            Response: return items list by params
        """
        params_encoded = urlencode(params)
        return self._get(f'/sites/{self.site_id}/search?{params_encoded}')

    def search_items_by_seller_id(self, seller_id, *args):
        """Get product based on product id

        Args:
            seller_id (string)
        Returns:
            Response (object)
        """

        params = {
            'seller_id': seller_id
        }
        params.update(*args)
        return self.search_items(params)

    def search_items_by_query(self, query: str):
        """Get product based on product id

        Args:
            query (string)
        Returns:
            Response (object)
        """

        params = {
            'q': query
        }
        return self.search_items(params)

    def get_products_by_seller(self, seller_id):
        """Get products by given seller.

        Args:
            seller_id (string)
        """

        return self._get(f'/users/{seller_id}/items/search?catalog_listing=false')

    def get_shipment_by_shipment_id(self, shipment_id):
        """Get shipemnt by given shipment id.

        Args:
            shipment_id (string)
        """

        return self._get(f'/shipments/{shipment_id}')

    def get_shipment_costs(self, shipment_id):
        """Get shipemnt costs by given shipment id.

        Args:
            shipment_id (string)
        """

        return self._get(
            f'/shipments/{shipment_id}/costs',
            headers={"X-Costs-New": 'true'}
        )

    def get_orders_by_seller(self, seller_id):
        """Get orders by given seller.

        Args:
            seller_id (string)
        """

        return self._get(f'/orders/search?seller={seller_id}')

    def get_order(self, order_id):
        """Get order by given order id.

        Args:
            seller_id (string)
        """

        return self._get(f'/orders/{order_id}/')

    def get_pack(self, pack_id):
        """Get pack by given order id.

        Args:
            pack_id (string)
        """

        return self._get(f'/packs/{pack_id}/')
