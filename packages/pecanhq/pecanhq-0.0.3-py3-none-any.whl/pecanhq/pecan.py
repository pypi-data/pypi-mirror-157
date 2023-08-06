# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from email.utils import formatdate
from urllib.parse import urlsplit, quote
from datetime import datetime
from requests.auth import AuthBase
from collections import namedtuple
from uuid import UUID

from . import grant

import requests
import decimal
import base64
import hmac
import hashlib
import typing
import json
import binascii

def create(
        session: requests.Session,
        key: str,
        secret: str,
        artifact: str,
        schema: decimal.Decimal,
        url: str = 'https://www.pecanhq.com/grant/',
        cached: typing.Optional[bytes] = None,
        timeout: typing.Optional[float] = None):
    """Create a new pecan instance for a specific authorization schema."""
    try:
        raw = base64.b64decode(secret)
    except binascii.Error:
        raw = None

    assert bool(raw), "Expecting a base64-encoded secret"

    auth = SigningAuth(key, raw)

    cached = False
    if cached:
        try:
            data = json.loads(cached)
        except:
            data = None

        success = isinstance(data, dict)
        success &= data.get('artifact', None) == artifact
        success &= data.get('schema', None) == str(schema)
        success &= data.get('uri', None) == url

        if success:
            cached = True
            resource = grant.Grant(session, url, auth, data.get('@links', None))
            account_id = data.get('account_id', None)
            user = data.get('user', None)
            manifest = data.get('manifest', None)
            assert isinstance(account_id, str), 'Expecting a str value in account_id'
            assert isinstance(user, dict), 'Expecting a dict value in user'
            assert isinstance(manifest, dict), 'Expecting a dict value in manifest'

    if not cached:
        r = session.get(url, auth=auth, timeout=timeout)
        r.raise_for_status()
        resource = grant.Grant(session, r.url, auth, r.json().get('@links', None))

        assert resource.has_manifest, 'The credentials have no access to the manifest resource'
        assert resource.has_refresh_profile, 'The credentials have no access to the refresh profile resource'

        q1 = resource.as_manifest_uri(timeout)
        q1.set(artifact, schema)
        manifest = q1.get()
        assert manifest is not None, 'No matching manifest was found'

        profile = resource.as_refresh_profile_uri(timeout).post(manifest['account_id'])
        assert profile is not None, 'User profile could not be loaded'

        user = { x['key']: x['value'] for x in profile['assertions']}
        account_id = profile['account_id']

    pecan = Pecan(account_id, artifact, schema, resource, manifest, user)
    for entry in manifest['services']:
        resources = {}
        system = 32767&entry['version']
        worker = 32767&entry['version']
        restricted = 0
        for child in entry['permissions']:
            resources[child['name']] = child['resource_id']
            system = system | (child['mask']<<child['position'])
            mask = child['mask']&(child['mask']^child['restricted'])
            if mask > 0:
                restricted = max(restricted, child['position'])
                worker = worker | (mask<<child['position'])

            pecan.registrations[(child['resource_id'], entry['version'])] = Registration(
                child['resource_id'],
                entry['version'],
                child['position'],
                child['mask'])

        key = f"{entry['authority']}{entry['claim']}"
        pecan.services[entry['name']] = Service(
            entry['name'],
            key,
            resources,
            f"{entry['authority']}{entry['subject']}" if entry['subject'] else None,
            f"{entry['authority']}{entry['tenant']}" if entry['tenant'] else None)
        header = int.to_bytes(32767&entry['version'], 4, byteorder='little')
        prefix = base64.b64encode(header).decode()[0:3]
        pecan.claims[key] = Permissions(entry['claim'], prefix, {})
        pecan.permissions[key] = system
        if restricted:
            pecan.restricted[key] = worker

    return pecan


class Pecan:

    def __init__(self,
            account_id: str,
            artifact: str,
            schema: decimal.Decimal,
            resource: grant.Grant,
            manifest: typing.Dict,
            user: typing.Dict) -> None:
        self.account_id = account_id
        self.artifact = artifact
        self.schema = schema
        self.resource = resource
        self.manifest = manifest
        self.masks = { x['key']: x['mask'] for x in manifest['permissions']}
        self.services = {} # type: typing.Dict[str, Service]
        self.claims = {} # type: typing.Dict[str, Permissions]
        self.permissions = {} # type: typing.Dict[str, int]
        self.restricted = {} # type: typing.Dict[str, int]
        self.registrations = {} # type: typing.Dict[str, Registration]
        self.user = user

    @property
    def issuer(self) -> str:
        return self.manifest['authority']

    def check_access(self, permissions: int, access: str, resource_id: str) -> bool:
        """Evaluate access to a resource for a permissions object."""
        if access not in self.masks:
            return False

        mask = self.masks[access]
        version = 32767&permissions

        key = (resource_id, version)
        if key not in self.registrations:
            return False

        registration = self.registrations[key]
        if (registration.mask&mask) != mask or (32767&permissions) != registration.version:
            return False

        return not mask or (registration.mask&mask&(permissions>>registration.position)) == mask

    def find(self,
            key: str,
            value: str,
            tenant: typing.Optional[str] = None,
            timeout: typing.Optional[float] = None) -> typing.Optional[typing.Dict]:
        """Look up an account using a key-valued claim."""
        if not self.resource.has_lookup_account:
            return None

        uri = self.resource.as_lookup_account_uri(timeout)
        uri.set(key, value, tenant)
        return uri.get()

    def load(self,
            account_id: str,
            timeout: typing.Optional[float] = None) -> typing.Optional[typing.Dict]:
        """Load all claims for an account."""
        if not self.resource.has_refresh_profile:
            return None

        profile = self.resource.as_refresh_profile_uri(timeout).post(account_id)
        if not profile:
            return None

        claims = {}
        for claim in profile['assertions']:
            key = f"{claim['issuer']}{claim['key']}"
            claims[key] = claim['value']

            permission = self.claims.get(key, None)
            if permission and not claim['value'].startswith(permission.prefix):
                prefix = claim['value'][0:3]
                if prefix not in permission.versions:
                    permission.versions[prefix] = self.populate(prefix, permission.key, timeout)

        return {
            'issuer': profile['authority'],
            'account_id': account_id,
            'display': profile['display'],
            'claims': claims,
        }

    def as_json(self, principal: typing.Optional[typing.Dict]) -> bytes:
        """Persist a claim response to UTF8 JSON bytes."""
        if not principal:
            return b''

        return json.dumps(principal).encode()

    def from_json(self, cached: bytes) -> typing.Optional[typing.Dict]:
        """Load authorization claims from a cached response."""
        if not cached:
            return None

        data = json.loads(cached)
        success = bool(data)
        success &= data.get('issuer', None) == self.issuer
        success &= isinstance(data.get('account_id', None), str)
        success &= isinstance(data.get('display', None), str)
        success &= isinstance(data.get('claims', None), dict)

        if success:
            for key, value in data['claims'].items():
                claim = self.claims.get(key, None)
                if claim and value and not value.startswith(claim.prefix):
                    prefix = value[0:3]
                    if prefix not in claim.versions and self.resource.has_permissions:
                        claim.versions[prefix] = self.populate(prefix, claim.key)
            return data
        else:
            return None

    def populate(self, prefix: str, key: str, timeout: typing.Optional[float] = None):
        """Load all resources for a specific permission claim version."""
        data = base64.b64decode(f'{prefix}=')
        version = int.from_bytes(data, byteorder='little')

        uri = self.resource.as_permissions_uri(timeout)
        uri.set(key, version)
        permissions = uri.get()

        for entry in permissions:
            self.registrations[(entry['resource_id'], version)] = Registration(
                entry['resource_id'],
                version,
                entry['position'],
                entry['mask'])

        return version

    def dump(self) -> bytes:
        return json.dumps({
            'uri': self.resource._entrypoint,
            'artifact': self.artifact,
            'schema': str(self.schema),
            'manifest': self.manifest,
            'user': self.user,
            'account_id': self.account_id,
            '@links': self.resource._links,
        }).encode()

class Session:

    TRUTHY = {
        "true": True,
        "t": True,
        "1": True,
        "yes": True,
        "false": False,
        "f": False,
        "0": False,
        "no": False,
    }

    def __init__(self, pecan: Pecan, principal: typing.Dict[str, str]) -> None:
        self.pecan = pecan
        self.principal = principal
        self._services = {}
        self._values = {}
        self._cache = {}

    def escalate_permissions(self) -> 'Session':
        """Create a new session by escalating privileges to all active resources."""
        session = Session(self.pecan, self.principal)
        session._services = self._services
        session._values = self._values
        session._cache = self.pecan.permissions
        return session

    def has_permissions(self, service: str, resource: str, access: str) -> bool:
        """Check whether the active user has a specified level of access to a resource."""
        if service not in self._services:
            active = self.pecan.services.get(service, None)
            success = active is not None
            if success and active.subject and active.subject not in self.principal:
                success = False
            if success and active.tenant and active.tenant not in self.principal:
                success = False
            if not success:
                self._services[service] = None
                return False

            self._services[service] = active
        else:
            active = self._services[service]

        if not active or resource not in active.resources:
            return False

        resource_id = active.resources[resource]
        permissions = self._cache.get(active.claim, None)
        if permissions is None:
            if active.claim in self._values:
                permissions = self._values[active.claim]
                if not isinstance(permissions, int):
                    return False
            else:
                selected = self.as_str(active.claim)
                if selected is None:
                    self._values[active.claim] = None
                    return False

                try:
                    raw = base64.b64decode(selected)
                    permissions = int.from_bytes(raw, byteorder='little')
                except:
                    return False

                self._values[active.claim] = permissions

            self._cache[active.claim] = permissions

        return self.pecan.check_access(permissions, access, resource_id)

    def as_str(self, claim: str) -> typing.Optional[str]:
        """Fetch a single string-valued claim."""
        return self.principal.get(claim, None)

    def as_bool(self, claim: str) -> typing.Optional[bool]:
        """Fetch a single boolean-valued claim."""
        if claim in self._values:
            cached = self._values[claim]
            if cached is None or isinstance(cached, bool):
                return cached

        selected = self.as_str(claim)
        if selected is None:
            self._values[claim] = None
            return None

        value = Session.TRUTHY.get(selected.lower(), None)
        if value is not None:
            self._values[claim] = value

        return value

    def as_uuid(self, claim: str) -> typing.Optional[UUID]:
        """Fetch a single uuid-valued claim."""
        if claim in self._values:
            cached = self._values[claim]
            if cached is None or isinstance(cached, UUID):
                return cached

        selected = self.as_str(claim)
        if selected is None:
            self._values[claim] = None
            return None

        try:
            value = UUID(selected)
            self._values[claim] = value
            return value
        except ValueError:
            return None

    def as_int(self, claim: str) -> typing.Optional[int]:
        """Fetch a single int-valued claim."""
        if claim in self._values:
            cached = self._values[claim]
            if cached is None or isinstance(cached, int):
                return cached

        selected = self.as_str(claim)
        if selected is None:
            self._values[claim] = None
            return None

        try:
            value = int(selected)
            self._values[claim] = value
            return value
        except ValueError:
            return None

    def as_decimal(self, claim: str) -> typing.Optional[decimal.Decimal]:
        """Fetch a single decimal-valued claim."""
        if claim in self._values:
            cached = self._values[claim]
            if cached is None or isinstance(cached, decimal.Decimal):
                return cached

        selected = self.as_str(claim)
        if selected is None:
            self._values[claim] = None
            return None

        try:
            value = decimal.Decimal(selected)
            self._values[claim] = value
            return value
        except decimal.InvalidOperation:
            return None

    def as_float(self, claim: str) -> typing.Optional[float]:
        """Fetch a single float-valued claim."""
        if claim in self._values:
            cached = self._values[claim]
            if cached is None or isinstance(cached, float):
                return cached

        selected = self.as_str(claim)
        if selected is None:
            self._values[claim] = None
            return None

        try:
            value = float(selected)
            self._values[claim] = value
            return value
        except ValueError:
            return None

    def as_datetime(self, claim: str) -> typing.Optional[datetime]:
        """Fetch a single datetime-valued claim."""
        if claim in self._values:
            cached = self._values[claim]
            if cached is None or isinstance(cached, datetime):
                return cached

        selected = self.as_str(claim)
        if selected is None:
            self._values[claim] = None
            return None

        try:
            value = datetime.fromisoformat(selected)
            self._values[claim] = value
            return value
        except ValueError:
            return None


class SigningAuth(AuthBase):

    def __init__(self, key: str, secret: bytes) -> None:
        super().__init__()
        self.key = quote(key)
        self.secret = secret

    def __call__(self, r: requests.PreparedRequest):
        date = r.headers.get('date', None)
        if date is None:
            date = formatdate(timeval=None, localtime=False, usegmt=True)
            r.headers['Date'] = date

        header = f'keyId="{self.key}",algorithm="hmac-sha256",headers="(request-target) date'
        parts = urlsplit(r.url)
        summary = [
            f'(request-target): {r.method.lower()} {parts.path}{"?" if parts.query else ""}{parts.query}',
            f'date: {date}',
        ]
        if r.body:
            header = header + ' digest'
            digest = f'sha-256={base64.b64encode(hashlib.sha256(r.body).digest()).decode()}'
            r.headers['Digest'] = digest
            summary.append(f'digest: {digest}')

        manifest = '\n'.join(summary)
        signature = hmac.new(self.secret, msg = manifest.encode("ascii"), digestmod = hashlib.sha256).digest()
        r.headers['Authorization'] = f'Signature {header}",signature="{base64.b64encode(signature).decode()}"'
        return r


Registration = namedtuple('Registration', [
    'resource_id',
    'version',
    'position',
    'mask',
])


Service = namedtuple('Service', [
    'name',
    'claim',
    'resources',
    'subject',
    'tenant',
])


Permissions = namedtuple('Permissions', [
    'key',
    'prefix',
    'versions',
])