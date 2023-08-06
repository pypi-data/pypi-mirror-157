# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pecanhq import meta
from urllib import parse as p
import decimal
import typing
import uuid



class ArtifactUri:
    """A mutable intermediate form for a requested artifact context"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> typing.Dict:
        """Fetch information about an artifact.

        Returns:
            typing.Dict
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            claim_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'artifact/{}'.format(
            p.quote(str(claim_group)))


class ServiceUri:
    """A mutable intermediate form for a requested service context"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> typing.Dict:
        """Fetch information about a resource group.

        Returns:
            typing.Dict
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            claim_group: str,
            resource_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'service/{}/{}'.format(
            p.quote(str(claim_group)),
            p.quote(str(resource_group)))


class RoleUri:
    """A mutable intermediate form for a requested role context"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> typing.Dict:
        """Fetch details about a specific policy group.

        The role resource has 2 navigations
            - From / to the roles view
            - From / to the claims view

        Returns:
            typing.Dict
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            key: str,
            policy_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'role/{}/{}'.format(
            p.quote(str(key)),
            p.quote(str(policy_group)))


class ClaimUri:
    """A mutable intermediate form for a requested claim context"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> typing.Dict:
        """Fetch details about a security claim.

        Returns:
            typing.Dict
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            key: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'claim/{}'.format(
            p.quote(str(key)))


class ProviderUri:
    """A mutable intermediate form for a requested provider context"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> typing.Dict:
        """An authentication provider.

        The provider resource has 3 navigations
            - From / to the create role action
            - From / to the create claim action
            - From / to the role context

        Returns:
            typing.Dict
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            key: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'provider/{}'.format(
            p.quote(str(key)))


class AccountUri:
    """A mutable intermediate form for a requested account context"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> typing.Dict:
        """Fetch details about an individual account.

        The account resource has 3 navigations
            - From /identities/identifier to the set identity action
            - From /organization to the organization context
            - From /tenant to the account context

        Returns:
            typing.Dict
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            account_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'account/{}'.format(
            p.quote(str(account_id)))


class PolicyUri:
    """A mutable intermediate form for a requested policy context"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> typing.Dict:
        """Information about a user policy.

        Returns:
            typing.Dict
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            policy_group_id: uuid.UUID,
            account_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'policy/{}/{}'.format(
            p.quote(str(policy_group_id)),
            p.quote(str(account_id)))


class AssertionUri:
    """A mutable intermediate form for a requested assertion context"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> typing.Dict:
        """A specific asserted claim.

        Returns:
            typing.Dict
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            account_id: uuid.UUID,
            claim_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'assertion/{}/{}'.format(
            p.quote(str(account_id)),
            p.quote(str(claim_id)))


class OrganizationUri:
    """A mutable intermediate form for a requested organization context"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> typing.Dict:
        """Information about an organization.

        The organization resource has 1 navigation
            - From /tenant to the account context

        Returns:
            typing.Dict
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            organization_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'organization/{}'.format(
            p.quote(str(organization_id)))


class UserAssertionUri:
    """A mutable intermediate form for a requested user assertion view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        claim_id: uuid.UUID) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            claim_id: The claim identifier.
        """
        q = '&'.join(self.args(claim_id))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> typing.Dict:
        """
        An asserted claim for a user.
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            claim_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'user_assertion?{}'.format(
            '&'.join(UserAssertionUri.args(claim_id)))

    @staticmethod
    def args(
        claim_id: uuid.UUID) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        yield f'claim_id={p.quote(str(claim_id))}'


class ArtifactsUri:
    """A mutable intermediate form for a requested artifacts view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        List all available artifacts within the current issuer.

        The artifacts resource has 1 navigation
            - From /rows to the artifact context
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'artifacts'


class ServicesUri:
    """A mutable intermediate form for a requested services view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        A list of all available resource groups.

        The services resource has 1 navigation
            - From /rows to the service context
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            claim_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'artifact/{}/services'.format(
            p.quote(str(claim_group)))


class ResourcesUri:
    """A mutable intermediate form for a requested resources view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        List all available resources.
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            claim_group: str,
            resource_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'service/{}/{}/resources'.format(
            p.quote(str(claim_group)),
            p.quote(str(resource_group)))


class ReleasesUri:
    """A mutable intermediate form for a requested releases view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        artifact: str = None) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            artifact: The artifact name.
        """
        q = '&'.join(self.args(artifact))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        All released schemas.
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            artifact: str = None) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'releases?{}'.format(
            '&'.join(ReleasesUri.args(artifact)))

    @staticmethod
    def args(
        artifact: str = None) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        if artifact is not None:
            yield f'artifact={p.quote(str(artifact))}'


class PermissionsUri:
    """A mutable intermediate form for a requested permissions view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        claim: str,
        version: int) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            claim: The claim key.
            version: The claim version.
        """
        q = '&'.join(self.args(claim, version))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        List all permissions mappings for a claim.
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            claim: str,
            version: int) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'permissions?{}'.format(
            '&'.join(PermissionsUri.args(claim, version)))

    @staticmethod
    def args(
        claim: str,
        version: int) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        yield f'claim={p.quote(str(claim))}'
        yield f'version={p.quote(str(version))}'


class RolesUri:
    """A mutable intermediate form for a requested roles view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        policy_group: str = None) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            policy_group: The identifier for the parent policy group.
        """
        q = '&'.join(self.args(policy_group))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        All roles.

        The roles resource has 1 navigation
            - From /rows to the role context
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            key: str,
            policy_group: str = None) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'provider/{}/roles?{}'.format(
            p.quote(str(key)),
            '&'.join(RolesUri.args(policy_group)))

    @staticmethod
    def args(
        policy_group: str = None) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        if policy_group is not None:
            yield f'policy_group={p.quote(str(policy_group))}'


class ClaimsUri:
    """A mutable intermediate form for a requested claims view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        provider: str = None,
        policy_group: str = None) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            provider: The referenced provider key, or claims from all providers if omitted.
            policy_group: The referenced policy group, or claims from all policy groups if omitted.
        """
        q = '&'.join(self.args(provider, policy_group))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        All available claims.

        The claims resource has 2 navigations
            - From /rows to the claim context
            - From /rows to the update claim action
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            provider: str = None,
            policy_group: str = None) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'claims?{}'.format(
            '&'.join(ClaimsUri.args(provider, policy_group)))

    @staticmethod
    def args(
        provider: str = None,
        policy_group: str = None) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        if provider is not None:
            yield f'provider={p.quote(str(provider))}'
        if policy_group is not None:
            yield f'policy_group={p.quote(str(policy_group))}'


class AccountsUri:
    """A mutable intermediate form for a requested accounts view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        keys: typing.List[str],
        filter: str = None,
        claim: str = None,
        desc: bool = False,
        organization_id: uuid.UUID = None) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            keys: All claim keys to include in the profile.
            filter: Filter the account list with this value.
            claim: Apply the filter to assertions of this claim.
            desc: A flag indicating the list should be scrolled in descending order.
            organization_id: The tenant organization identifier.
        """
        q = '&'.join(self.args(keys, filter, claim, desc, organization_id))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        List all user accounts.

        The accounts resource has 1 navigation
            - From /rows to the account context
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            keys: typing.List[str],
            filter: str = None,
            claim: str = None,
            desc: bool = False,
            organization_id: uuid.UUID = None) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'accounts?{}'.format(
            '&'.join(AccountsUri.args(keys, filter, claim, desc, organization_id)))

    @staticmethod
    def args(
        keys: typing.List[str],
        filter: str = None,
        claim: str = None,
        desc: bool = False,
        organization_id: uuid.UUID = None) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        if keys:
            for i in keys:
                yield f'keys={ str(i) }'
        if filter is not None:
            yield f'filter={p.quote(str(filter))}'
        if claim is not None:
            yield f'claim={p.quote(str(claim))}'
        yield f'desc={p.quote(str(desc))}'
        if organization_id is not None:
            yield f'organization_id={p.quote(str(organization_id))}'


class PoliciesUri:
    """A mutable intermediate form for a requested policies view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        editing: bool = False) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            editing: A flag indicating the policy list is being edited and should return all policies where the calling account has rights.
        """
        q = '&'.join(self.args(editing))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        Fetch all policies that apply to the account.

        The policies resource has 2 navigations
            - From /rows to the policy context
            - From /rows to the set account access action
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            account_id: uuid.UUID,
            editing: bool = False) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'account/{}/policies?{}'.format(
            p.quote(str(account_id)),
            '&'.join(PoliciesUri.args(editing)))

    @staticmethod
    def args(
        editing: bool = False) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        yield f'editing={p.quote(str(editing))}'


class AssertionsUri:
    """A mutable intermediate form for a requested assertions view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        List all security assertions for an account.

        The assertions resource has 1 navigation
            - From /rows to the assertion context
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            account_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'account/{}/assertions'.format(
            p.quote(str(account_id)))


class ManifestUri:
    """A mutable intermediate form for a requested manifest view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        artifact: str,
        schema: decimal.Decimal = None) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            artifact: The artifact name.
            schema: The schema version. If omitted, the current (perhaps unreleased) schema will be fetched.
        """
        q = '&'.join(self.args(artifact, schema))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> typing.Dict:
        """
        A manifest containing the permissions schema for a released
        service.
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            artifact: str,
            schema: decimal.Decimal = None) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'manifest?{}'.format(
            '&'.join(ManifestUri.args(artifact, schema)))

    @staticmethod
    def args(
        artifact: str,
        schema: decimal.Decimal = None) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        yield f'artifact={p.quote(str(artifact))}'
        if schema is not None:
            yield f'schema={p.quote(str(schema))}'


class ProvidersUri:
    """A mutable intermediate form for a requested providers view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        A list of all available authentication providers.

        The providers resource has 1 navigation
            - From /rows to the provider context
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'providers'


class AvailableResourcesUri:
    """A mutable intermediate form for a requested available resources view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        editing: bool = False) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            editing: A flag indicating the user is editing the role and needs access to all available resources from the parent.
        """
        q = '&'.join(self.args(editing))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        Resources that are available to a role.
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            key: str,
            policy_group: str,
            editing: bool = False) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'role/{}/{}/available_resources?{}'.format(
            p.quote(str(key)),
            p.quote(str(policy_group)),
            '&'.join(AvailableResourcesUri.args(editing)))

    @staticmethod
    def args(
        editing: bool = False) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        yield f'editing={p.quote(str(editing))}'


class LookupAccountUri:
    """A mutable intermediate form for a requested lookup account view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        key: str,
        value: str,
        tenant: str = None) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            key: The claim key.
            value: The asserted claim value.
            tenant: The value of the associated tenant claim, if the key claim is associated with a multi-tenanted identity.
        """
        q = '&'.join(self.args(key, value, tenant))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> typing.Dict:
        """
        Look up an account by the value of a unique key.

        The lookup account resource has 2 navigations
            - From / to the account context
            - From / to the update identity action
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            key: str,
            value: str,
            tenant: str = None) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'lookup_account?{}'.format(
            '&'.join(LookupAccountUri.args(key, value, tenant)))

    @staticmethod
    def args(
        key: str,
        value: str,
        tenant: str = None) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        yield f'key={p.quote(str(key))}'
        yield f'value={p.quote(str(value))}'
        if tenant is not None:
            yield f'tenant={p.quote(str(tenant))}'


class AvailablePoliciesUri:
    """A mutable intermediate form for a requested available policies view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def set(self,
        account_id: uuid.UUID,
        administrator_id: uuid.UUID) -> None:
        """
        Mutate the request, replacing all query parameters.

        Args:
            account_id: The account identifier.
            administrator_id: The administrator account being analysed.
        """
        q = '&'.join(self.args(account_id, administrator_id))
        r = p.urlsplit(self.uri)
        self.uri = p.urlunsplit((r.scheme, r.netloc, r.path, q, r.fragment))

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        Review available policies for an account.
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            account_id: uuid.UUID,
            administrator_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'available_policies?{}'.format(
            '&'.join(AvailablePoliciesUri.args(account_id, administrator_id)))

    @staticmethod
    def args(
        account_id: uuid.UUID,
        administrator_id: uuid.UUID) -> typing.Generator[str, None, None]:
        """Emit all arguments as individual query parameters"""
        yield f'account_id={p.quote(str(account_id))}'
        yield f'administrator_id={p.quote(str(administrator_id))}'


class OrganizationsUri:
    """A mutable intermediate form for a requested organizations view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> meta.ResultSet[typing.Dict]:
        """
        List all organization managed by the current account.
        """
        return meta.ResultSet(self.uri, self.fetch)

    def fetch(self, uri: str) -> typing.Dict:
        r = self._handler.get(uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'organizations'


class StatusUri:
    """A mutable intermediate form for a requested status view"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def get(self) -> typing.Dict:
        """
        Status information for the current account.

        The status resource has 1 navigation
            - From /artifact to the artifact context
        """
        r = self._handler.get(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'status'


class RefreshUri:
    """A mutable intermediate form for a requested refresh action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        session: str = None) -> typing.Dict:
        """
        Refresh the user's session.

        Args:
            session: The specific session.

        The refresh resource has 3 navigations
            -From / to the account context
            -From /tenant to the account context
            -From /assertions to the user assertion view
        """
        r = self._handler.post(
            self.uri,
            json={
                'session': session
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "refresh";


class ReleaseUri:
    """A mutable intermediate form for a requested release action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self):
        """
        Release the current state of the artifact as a new version.
        """
        r = self._handler.post(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            claim_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'artifact/{}/release'.format(
            p.quote(str(claim_group)))


class UpdateArtifactUri:
    """A mutable intermediate form for a requested update artifact action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        description: str):
        """
        Update artifact metadata.

        Args:
            description: Full-text information about the artifact.
        """
        r = self._handler.post(
            self.uri,
            json={
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            claim_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'artifact/{}/update_artifact'.format(
            p.quote(str(claim_group)))


class CreateServiceUri:
    """A mutable intermediate form for a requested create service action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        name: str,
        claim: str,
        description: str,
        provider: str,
        openapi: meta.Attachment = None) -> typing.Dict:
        """
        Create a new service.

        Args:
            name: The resource group name.
            claim: The permissions claim key.
            description: Full-text information about the resource group.
            provider: The provider name.
            openapi: An OpenAPI specification.

        The create service resource has 7 navigations
            -From / to the service context
            -From / to the update service action
            -From / to the create resource action
            -From / to the update resource action
            -From / to the reset action
            -From / to the set service status action
            -From / to the resources view
        """
        r = self._handler.post(
            self.uri,
            data={
                'name': name,
                'claim': claim,
                'description': description,
                'provider': provider
            },
            files={
                'openapi': openapi
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            claim_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'artifact/{}/create_service'.format(
            p.quote(str(claim_group)))


class UpdateServiceUri:
    """A mutable intermediate form for a requested update service action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        description: str):
        """
        Update an existing resource group.

        Args:
            description: Full-text information about the resource group.
        """
        r = self._handler.post(
            self.uri,
            json={
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            claim_group: str,
            resource_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'service/{}/{}/update_service'.format(
            p.quote(str(claim_group)),
            p.quote(str(resource_group)))


class CreateResourceUri:
    """A mutable intermediate form for a requested create resource action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        name: str,
        mask: int,
        restricted: int,
        description: str) -> typing.Dict:
        """
        Create a new resource.

        Args:
            name: The name of this resource.
            mask: The unix permissions associated with this resource (7:rwx, 6:rw-, 5:r-x, 4:r--, 3:-wx, 2:-w-, 1:--x).
            restricted: The restriction applied to the mask for normal user accounts. System accountabilities have full access to the unmodified mask.
            description: A human-readable description of the resource.
        """
        r = self._handler.post(
            self.uri,
            json={
                'name': name,
                'mask': mask,
                'restricted': restricted,
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            claim_group: str,
            resource_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'service/{}/{}/create_resource'.format(
            p.quote(str(claim_group)),
            p.quote(str(resource_group)))


class UpdateResourceUri:
    """A mutable intermediate form for a requested update resource action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        resource_id: uuid.UUID,
        name: str,
        mask: int,
        restricted: int,
        description: str,
        archived: bool):
        """
        Update a resource.

        Args:
            resource_id: The resource identifier.
            name: The name of this resource.
            mask: The unix permissions associated with this resource (7:rwx, 6:rw-, 5:r-x, 4:r--, 3:-wx, 2:-w-, 1:--x).
            restricted: The restriction applied to the mask for normal user accounts. System accountabilities have full access to the unmodified mask.
            description: A human-readable description of the resource.
            archived: A flag indicating the resource should currently be archived.
        """
        r = self._handler.post(
            self.uri,
            json={
                'resource_id': resource_id,
                'name': name,
                'mask': mask,
                'restricted': restricted,
                'description': description,
                'archived': archived
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            claim_group: str,
            resource_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'service/{}/{}/update_resource'.format(
            p.quote(str(claim_group)),
            p.quote(str(resource_group)))


class CreateRoleUri:
    """A mutable intermediate form for a requested create role action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        name: str,
        description: str,
        mask: int = None,
        scope: str = None) -> typing.Dict:
        """
        Create a child policy group.

        Args:
            name: The name of this policy group.
            description: A description of the semantic meaning of this policy group.
            mask: The maximum permissions that can be granted within this group.
            scope: The name of the externally managed scope for the policy group, used by the authentication provider to expand access tokens.

        The create role resource has 7 navigations
            -From / to the role context
            -From / to the create role action
            -From / to the create claim action
            -From / to the set general access action
            -From / to the update role action
            -From / to the set resource access action
            -From / to the available resources view
        """
        r = self._handler.post(
            self.uri,
            json={
                'name': name,
                'description': description,
                'mask': mask,
                'scope': scope
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            key: str,
            policy_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'role/{}/{}/create_role'.format(
            p.quote(str(key)),
            p.quote(str(policy_group)))


class CreateClaimUri:
    """A mutable intermediate form for a requested create claim action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        claim: str,
        description: str,
        unique: bool) -> typing.Dict:
        """
        Create a new security claim.

        Args:
            claim: The claim key.
            description: A description of the semantic meaning of this claim.
            unique: A flag indicating the claim is a unique key for an account.

        The create claim resource has 2 navigations
            -From / to the claim context
            -From / to the update claim action
        """
        r = self._handler.post(
            self.uri,
            json={
                'claim': claim,
                'description': description,
                'unique': unique
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri(
            key: str,
            policy_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'role/{}/{}/create_claim'.format(
            p.quote(str(key)),
            p.quote(str(policy_group)))


class UpdateClaimUri:
    """A mutable intermediate form for a requested update claim action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        description: str):
        """
        Update a security claim.

        Args:
            description: A description of the semantic meaning of this claim.
        """
        r = self._handler.post(
            self.uri,
            json={
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            key: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'claim/{}/update_claim'.format(
            p.quote(str(key)))


class SetAccountAccessUri:
    """A mutable intermediate form for a requested set account access action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        claims: typing.List[typing.Dict],
        mask: int = None):
        """
        Configure an access policy for an account.

        Args:
            claims: All claim values to be modified.
            mask: The permissions granted to the user for this group.
        """
        r = self._handler.post(
            self.uri,
            json={
                'claims': claims,
                'mask': mask
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            policy_group_id: uuid.UUID,
            account_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'policy/{}/{}/set_account_access'.format(
            p.quote(str(policy_group_id)),
            p.quote(str(account_id)))


class CreateAccountUri:
    """A mutable intermediate form for a requested create account action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        display: str,
        claims: typing.List[typing.Dict],
        description: str = None,
        organization_id: uuid.UUID = None) -> typing.Dict:
        """
        Create a new account.

        Args:
            display: The display name for the account.
            claims: All claims associated with the account.
            description: A description of the account.
            organization_id: The tenant organization account, if a multi-tenanted account.

        The create account resource has 8 navigations
            -From / to the account context
            -From / to the update account action
            -From / to the set identity action
            -From / to the update identity action
            -From / to the set account status action
            -From / to the send invitation action
            -From / to the policies view
            -From / to the assertions view
        """
        r = self._handler.post(
            self.uri,
            json={
                'display': display,
                'claims': claims,
                'description': description,
                'organization_id': organization_id
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "create_account";


class CreateArtifactUri:
    """A mutable intermediate form for a requested create artifact action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        name: str,
        description: str) -> typing.Dict:
        """
        Create a new  artifact.

        Args:
            name: The artifact name.
            description: Full-text information about the artifact.

        The create artifact resource has 6 navigations
            -From / to the artifact context
            -From / to the release action
            -From / to the update artifact action
            -From / to the create service action
            -From / to the set artifact status action
            -From / to the services view
        """
        r = self._handler.post(
            self.uri,
            json={
                'name': name,
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "create_artifact";


class SetGeneralAccessUri:
    """A mutable intermediate form for a requested set general access action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        enabled: bool):
        """
        Mark a policy group with general access status.

        Args:
            enabled: A flag indicating the policy group should be made general access.
        """
        r = self._handler.post(
            self.uri,
            json={
                'enabled': enabled
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            key: str,
            policy_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'role/{}/{}/set_general_access'.format(
            p.quote(str(key)),
            p.quote(str(policy_group)))


class UpdateAccountUri:
    """A mutable intermediate form for a requested update account action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        display: str,
        description: str = None):
        """
        Update an account's metadata.

        Args:
            display: The display name for the account.
            description: A description of the account.
        """
        r = self._handler.post(
            self.uri,
            json={
                'display': display,
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            account_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'account/{}/update_account'.format(
            p.quote(str(account_id)))


class UpdateRoleUri:
    """A mutable intermediate form for a requested update role action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        description: str):
        """
        Update an existing policy group.

        Args:
            description: Full-text information about the policy group.
        """
        r = self._handler.post(
            self.uri,
            json={
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            key: str,
            policy_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'role/{}/{}/update_role'.format(
            p.quote(str(key)),
            p.quote(str(policy_group)))


class RegisterUri:
    """A mutable intermediate form for a requested register action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        manifest: meta.Attachment) -> typing.Dict:
        """
        Register an artifact from an application manifest.

        Args:
            manifest: The application manifest.

        The register resource has 6 navigations
            -From / to the artifact context
            -From / to the release action
            -From / to the update artifact action
            -From / to the create service action
            -From / to the set artifact status action
            -From / to the services view
        """
        r = self._handler.post(
            self.uri,
            data={
            },
            files={
                'manifest': manifest
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "register";


class CreateProviderUri:
    """A mutable intermediate form for a requested create provider action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        name: str,
        description: str,
        subject: str = None,
        tenant: str = None) -> typing.Dict:
        """
        Create a new authentication provider.

        Args:
            name: The provider name.
            description: Full-text information about the provider.
            subject: The subject identifier claim key.
            tenant: The tenant identifier claim key, if multi-tenanted.

        The create provider resource has 3 navigations
            -From / to the provider context
            -From / to the update provider action
            -From / to the roles view
        """
        r = self._handler.post(
            self.uri,
            json={
                'name': name,
                'description': description,
                'subject': subject,
                'tenant': tenant
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "create_provider";


class UpdateProviderUri:
    """A mutable intermediate form for a requested update provider action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        description: str):
        """
        Update provider metadata.

        Args:
            description: Full-text information about the provider.
        """
        r = self._handler.post(
            self.uri,
            json={
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            key: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'provider/{}/update_provider'.format(
            p.quote(str(key)))


class SetResourceAccessUri:
    """A mutable intermediate form for a requested set resource access action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        enabled: typing.List[uuid.UUID],
        disabled: typing.List[uuid.UUID]):
        """
        Update the active status for a resource.

        Args:
            enabled: The resource identifiers to enable.
            disabled: The resource identifiers to disable.
        """
        r = self._handler.post(
            self.uri,
            json={
                'enabled': enabled,
                'disabled': disabled
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            key: str,
            policy_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'role/{}/{}/set_resource_access'.format(
            p.quote(str(key)),
            p.quote(str(policy_group)))


class CreateTenantUri:
    """A mutable intermediate form for a requested create tenant action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        name: str,
        claims: typing.List[typing.Dict],
        description: str = None,
        organization_id: uuid.UUID = None) -> typing.Dict:
        """
        Register a system tenant.

        Args:
            name: The organization's display name.
            claims: All claims associated with the account.
            description: A description of the organization.
            organization_id: The tenant organization account, if a multi-tenanted account.

        The create tenant resource has 8 navigations
            -From / to the account context
            -From / to the update account action
            -From / to the set identity action
            -From / to the update identity action
            -From / to the set account status action
            -From / to the send invitation action
            -From / to the policies view
            -From / to the assertions view
        """
        r = self._handler.post(
            self.uri,
            json={
                'name': name,
                'claims': claims,
                'description': description,
                'organization_id': organization_id
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "create_tenant";


class SetIdentityUri:
    """A mutable intermediate form for a requested set identity action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        key: str,
        value: str = None):
        """
        Set the identity for a account within a provider.

        Args:
            key: The claim key for the identity claim.
            value: The identifier value, if the account should be granted access.
        """
        r = self._handler.post(
            self.uri,
            json={
                'key': key,
                'value': value
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            account_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'account/{}/set_identity'.format(
            p.quote(str(account_id)))


class UpdateIdentityUri:
    """A mutable intermediate form for a requested update identity action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        key: str,
        secret: bytes = None):
        """
        Update an identity claim with a secret value.

        Args:
            key: The claim key for the identity claim.
            secret: The secret value for the identity claim.
        """
        r = self._handler.post(
            self.uri,
            json={
                'key': key,
                'secret': secret
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            account_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'account/{}/update_identity'.format(
            p.quote(str(account_id)))


class ResetUri:
    """A mutable intermediate form for a requested reset action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self):
        """
        Reset all pending changes for a service.
        """
        r = self._handler.post(self.uri, auth=self._auth, timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            claim_group: str,
            resource_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'service/{}/{}/reset'.format(
            p.quote(str(claim_group)),
            p.quote(str(resource_group)))


class SetServiceStatusUri:
    """A mutable intermediate form for a requested set service status action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        archived: bool):
        """
        Update the service status.

        Args:
            archived: A flag indicating the service should be archived.
        """
        r = self._handler.post(
            self.uri,
            json={
                'archived': archived
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            claim_group: str,
            resource_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'service/{}/{}/set_service_status'.format(
            p.quote(str(claim_group)),
            p.quote(str(resource_group)))


class SetArtifactStatusUri:
    """A mutable intermediate form for a requested set artifact status action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        archived: bool):
        """
        A flag indicating the artifact should be archived.

        Args:
            archived: A flag indicating the resource group should currently be archived.
        """
        r = self._handler.post(
            self.uri,
            json={
                'archived': archived
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            claim_group: str) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'artifact/{}/set_artifact_status'.format(
            p.quote(str(claim_group)))


class SetAccountStatusUri:
    """A mutable intermediate form for a requested set account status action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        archived: bool):
        """
        Update the account status.

        Args:
            archived: A flag indicating the account should be archived.
        """
        r = self._handler.post(
            self.uri,
            json={
                'archived': archived
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            account_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'account/{}/set_account_status'.format(
            p.quote(str(account_id)))


class SetReleaseStatusUri:
    """A mutable intermediate form for a requested set release status action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        artifact: str,
        schema: decimal.Decimal,
        published: bool,
        description: str = None):
        """
        Activate a specific artifact version.

        Args:
            artifact: The name of this artifact.
            schema: The artifact schema version string.
            published: A flag indicating whether the artifact should be the currently published version of the schema.
            description: Optionally override the description.
        """
        r = self._handler.post(
            self.uri,
            json={
                'artifact': artifact,
                'schema': schema,
                'published': published,
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "set_release_status";


class RefreshProfileUri:
    """A mutable intermediate form for a requested refresh profile action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        account_id: uuid.UUID) -> typing.Dict:
        """
        Refresh all profile assertions.

        Args:
            account_id: The account identifier.
        """
        r = self._handler.post(
            self.uri,
            json={
                'account_id': account_id
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "refresh_profile";


class RegisterAppUri:
    """A mutable intermediate form for a requested register app action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        display: str,
        description: str = None) -> typing.Dict:
        """
        Register a new application identity.

        Args:
            display: The display name for the account.
            description: A description of the account.

        The register app resource has 1 navigation
            -From / to the account context
        """
        r = self._handler.post(
            self.uri,
            json={
                'display': display,
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "register_app";


class OverrideAccountAccessUri:
    """A mutable intermediate form for a requested override account access action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        policy_group_id: uuid.UUID,
        account_id: uuid.UUID,
        administrator_id: uuid.UUID,
        claims: typing.List[typing.Dict],
        mask: int = None):
        """
        Use delegated authority to override the account access level
        for a policy.

        Args:
            policy_group_id: The policy group name for this role.
            account_id: The account identifier.
            administrator_id: The administrator account controlling the action.
            claims: All claim values to be modified.
            mask: The permissions granted to the user for this group.
        """
        r = self._handler.post(
            self.uri,
            json={
                'policy_group_id': policy_group_id,
                'account_id': account_id,
                'administrator_id': administrator_id,
                'claims': claims,
                'mask': mask
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "override_account_access";


class OverrideAccountUri:
    """A mutable intermediate form for a requested override account action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        account_id: uuid.UUID,
        administrator_id: uuid.UUID,
        display: str,
        claims: typing.List[typing.Dict],
        description: str = None):
        """
        Override account metadata.

        Args:
            account_id: The account identifier.
            administrator_id: The administrator account controlling the action.
            display: The display name for the account.
            claims: All claim values to be modified.
            description: A description of the account.
        """
        r = self._handler.post(
            self.uri,
            json={
                'account_id': account_id,
                'administrator_id': administrator_id,
                'display': display,
                'claims': claims,
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "override_account";


class AssignIdentityUri:
    """A mutable intermediate form for a requested assign identity action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        key: str,
        value: str,
        scopes: typing.List[str],
        secret: bytes = None,
        tenant: str = None,
        display: str = None) -> typing.Dict:
        """
        Assign an externally managed identity, optionally creating
        the profile if it does not exist.

        Args:
            key: The claim key for the identity claim.
            value: The asserted claim value.
            scopes: All external scopes assigned to this user. Any existing roles belonging to a scope not in this collection will be disabled.
            secret: The secret value for the identity claim.
            tenant: The value of the associated tenant claim, if the key claim is associated with a multi-tenanted identity.
            display: The display name for the account, if it should be overwritten.
        """
        r = self._handler.post(
            self.uri,
            json={
                'key': key,
                'value': value,
                'scopes': scopes,
                'secret': secret,
                'tenant': tenant,
                'display': display
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "assign_identity";


class UpdateOrganizationUri:
    """A mutable intermediate form for a requested update organization action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        name: str,
        description: str = None):
        """
        Update organization details.

        Args:
            name: The organization name.
            description: A description of the organization.
        """
        r = self._handler.post(
            self.uri,
            json={
                'name': name,
                'description': description
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            organization_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'organization/{}/update_organization'.format(
            p.quote(str(organization_id)))


class SendInvitationUri:
    """A mutable intermediate form for a requested send invitation action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        email: str):
        """
        Send an invitation for a user to take ownership of an
        account.

        Args:
            email: The user's email address.
        """
        r = self._handler.post(
            self.uri,
            json={
                'email': email
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri(
            account_id: uuid.UUID) -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return 'account/{}/send_invitation'.format(
            p.quote(str(account_id)))


class SetupUri:
    """A mutable intermediate form for a requested setup action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        name: str,
        version: decimal.Decimal,
        claim: str,
        description: str,
        idp: str,
        subject: str = None,
        tenant: str = None,
        openapi: meta.Attachment = None):
        """
        Perform initial setup actions for an account.

        Args:
            name: The application name.
            version: The schema version.
            claim: The permissions claims.
            description: A description of the application.
            idp: The identity provider name.
            subject: The user id claim, if relevant for the identity provider.
            tenant: The tenant id claim, if relevant for the identity provider.
            openapi: The OpenAPI document for the application.
        """
        r = self._handler.post(
            self.uri,
            data={
                'name': name,
                'version': version,
                'claim': claim,
                'description': description,
                'idp': idp,
                'subject': subject,
                'tenant': tenant
            },
            files={
                'openapi': openapi
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "setup";


class ConfigureUri:
    """A mutable intermediate form for a requested configure action"""

    def __init__(self, uri, handler, entrypoint, auth, timeout):
        self.uri = uri
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._timeout = timeout

    def as_relative_uri(self, path: typing.Optional[str] = None) -> str:
        """Create a relative uri with a specified prefix

        Args:
            path: The base path for the uri.

        Returns:
            A relative uri string
        """
        return (path or "/") + self.uri.replace(self._entrypoint, '')

    def post(self,
        permissions: typing.List[typing.Dict]):
        """
        Perform manual configuration of the account.

        Args:
            permissions: All permissions associated with the issuer.
        """
        r = self._handler.post(
            self.uri,
            json={
                'permissions': permissions
            },
            auth=self._auth,
            timeout=self._timeout)
        r.raise_for_status()

    @staticmethod
    def create_relative_uri() -> str:
        """A utility method for constructing relative URI paths to this resource

        Returns:
            A relative uri string
        """
        return "configure";