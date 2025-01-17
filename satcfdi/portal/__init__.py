import json
import pickle
from time import time

import requests
import urllib3
from requests.structures import CaseInsensitiveDict

from .utils import get_form, generate_token, request_ref_headers, request_verification_token, random_ajax_id
from ..models import Signer
from ..exceptions import ResponseError


class PortalManager(requests.Session):
    def __init__(self, signer: Signer):
        super().__init__()
        try:
            urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH'
        except:
            pass
        self.signer = signer

        self.headers = CaseInsensitiveDict(
            {
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                "Accept-Encoding": 'gzip, deflate, br',
                "Accept": 'text/html,application/xhtml+xml,application/xml',
                "Connection": "keep-alive",
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
            }
        )

    def save_session(self, target):
        pickle.dump(self.cookies, target)

    def load_session(self, source):
        self.cookies.update(pickle.load(source))

    def form(self, action, referer_url, data):
        res = self.post(
            url=action,
            headers=request_ref_headers(referer_url),
            data=data
        )
        assert res.status_code == 200
        return res

    def fiel_login(self, login_response):
        action, data = get_form(login_response, id='certform')
        return self.form(
            action,
            login_response.request.url,
            data | {
                'token': generate_token(self.signer, code=data['guid']),
                'fert': self.signer.certificate.get_notAfter()[2:].decode(),
            }
        )


class SATPortal(PortalManager):
    BASE_URL = 'https://loginda.siat.sat.gob.mx'

    def login(self):
        res = self.get(
            url=f'{self.BASE_URL}/nidp/app/login?id=fiel'
        )
        assert res.status_code == 200
        action, data = get_form(res)

        return self.fiel_login(
            login_response=self.form(action, res.request.url, data)
        )

    def home_page(self):
        return self.get(
            url=f'{self.BASE_URL}/nidp/app?sid=0'
        )

    def logout(self):
        return self.get(
            url=f'{self.BASE_URL}/nidp/app/logout',
            headers={
                'referer': f'{self.BASE_URL}/nidp/app?sid=0'
            },
            allow_redirects=False
        )

    def declaraciones_provisionales_login(self):
        res = self.get(
            url='https://ptscdecprov.clouda.sat.gob.mx',
            allow_redirects=True
        )
        assert res.status_code == 200

        action, data = get_form(res)
        res = self.form(action, res.request.url, data)
        return res


class SATFacturaElectronica(PortalManager):
    BASE_URL = 'https://portal.facturaelectronica.sat.gob.mx'
    REQUEST_CONTEXT = 'appId=cid-v1:20ff76f4-0bca-495f-b7fd-09ca520e39f7'

    def __init__(self, signer: Signer):
        super().__init__(signer)
        self._ajax_id = random_ajax_id()
        self._request_verification_token = None

    def login(self):
        res = self.get(
            url=self.BASE_URL
        )
        assert res.status_code == 200
        try:
            action, data = get_form(res)
        except IndexError as ex:
            raise ValueError("Login form not found, please try again") from ex

        if action.startswith('https://cfdiau.sat.gob.mx/'):
            assert 'nidp/wsfed/ep?id=SATUPCFDiCon' in action

            res = self.fiel_login(
                login_response=self.form(
                    action.replace('nidp/wsfed/ep?id=SATUPCFDiCon', 'nidp/app/login?id=SATx509Custom'),
                    res.request.url,
                    data
                )
            )

            action, data = get_form(res)
            res = self.form(action, res.request.url, data)

            action, data = get_form(res)

        res = self.form(action, res.request.url, data)

        self._request_verification_token = request_verification_token(res)
        self._ajax_id = random_ajax_id()
        return res

    def _reload_verification_token(self):
        res = self.get(
            url=f'{self.BASE_URL}/Factura/GeneraFactura',
            allow_redirects=False
        )
        if res.status_code == 200:
            self._request_verification_token = request_verification_token(res)
        else:
            raise ValueError('Please Login Again')

    def reactivate_session(self):
        res = self.post(
            url=f'{self.BASE_URL}/Home/ReActiveSession',
            headers={
                'Origin': self.BASE_URL,
                'Request-Context': self.REQUEST_CONTEXT,
                'Request-Id': f'|{self._ajax_id}.{random_ajax_id()}'
            },
            allow_redirects=False
        )
        return res

    def _request(self, method, path, data=None, params=None):
        if self._request_verification_token is None:
            self._reload_verification_token()

        res = self.request(
            method=method,
            url=f'{self.BASE_URL}/{path}',
            headers={
                'Origin': self.BASE_URL,
                'Authority': self.BASE_URL,
                'Request-Context': self.REQUEST_CONTEXT,
                '__RequestVerificationToken': self._request_verification_token,
                'Request-Id': f'|{self._ajax_id}.{random_ajax_id()}'  # |pR4Px.o0yAS
            },
            data=data,
            params=params,
            allow_redirects=False
        )
        if res.status_code == 200:
            return res.json()
        else:
            raise ResponseError(res)

    def legal_name_valid(self, rfc, legal_name):
        res = self._request(
            method='POST',
            path='Clientes/ValidaRazonSocialRFC',
            data={
                'rfcValidar': rfc.upper(),
                'razonSocial': legal_name.upper(),
            })
        if not res['exitoso']:
            raise ResponseError(res)
        return res['resultado']

    def rfc_valid(self, rfc):
        res = self._request(
            method='POST',
            path='Clientes/ExisteLrfc',
            data={
                'rfcValidar': rfc.upper()
            }
        )
        if not res['exitoso']:
            raise ResponseError(res)
        return res['resultado']

    def lco_details(self, rfc, apply_border_region=True):
        res = self._request(
            method='GET',
            path='Clientes/ValidaLco',
            params={
                'rfcValidar': rfc.upper(),
                'aplicaRegionFronteriza': apply_border_region,
                "_": int(time() * 1000)
            }
        )
        return json.loads(res)
