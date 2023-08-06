# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with self
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import typing

from urllib.parse import urljoin

from . import resources

class Grant:
    """
    Authentication and authorization API.
    """

    def __init__(self, handler, entrypoint, auth, links):
        self._handler = handler
        self._entrypoint = entrypoint
        self._auth = auth
        self._links = links

    @property
    def has_artifact(self) -> bool:
        """A flag indicating the artifact resource is available."""
        return self._links and 'artifact' in self._links and self._links['artifact'].startswith(self._entrypoint)

    def as_artifact_uri(self, timeout: typing.Any = None) -> resources.ArtifactUri:
        """ Start building an API request from the artifact resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ArtifactUri
        """
        if self.has_artifact:
            return resources.ArtifactUri(self._links['artifact'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.artifact')

    def to_artifact_uri(self, uri: str, timeout: typing.Any = None) -> resources.ArtifactUri:
        """Create a re-entrant request to the artifact resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ArtifactUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ArtifactUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_service(self) -> bool:
        """A flag indicating the service resource is available."""
        return self._links and 'service' in self._links and self._links['service'].startswith(self._entrypoint)

    def as_service_uri(self, timeout: typing.Any = None) -> resources.ServiceUri:
        """ Start building an API request from the service resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ServiceUri
        """
        if self.has_service:
            return resources.ServiceUri(self._links['service'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.service')

    def to_service_uri(self, uri: str, timeout: typing.Any = None) -> resources.ServiceUri:
        """Create a re-entrant request to the service resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ServiceUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ServiceUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_role(self) -> bool:
        """A flag indicating the role resource is available."""
        return self._links and 'role' in self._links and self._links['role'].startswith(self._entrypoint)

    def as_role_uri(self, timeout: typing.Any = None) -> resources.RoleUri:
        """ Start building an API request from the role resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The role resource has 2 navigations:
            - From / to the roles view
            - From / to the claims view

        Returns:
            resources.RoleUri
        """
        if self.has_role:
            return resources.RoleUri(self._links['role'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.role')

    def to_role_uri(self, uri: str, timeout: typing.Any = None) -> resources.RoleUri:
        """Create a re-entrant request to the role resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The role resource has 2 navigations:
            - From / to the roles view
            - From / to the claims view

        Returns:
            resources.RoleUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.RoleUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_claim(self) -> bool:
        """A flag indicating the claim resource is available."""
        return self._links and 'claim' in self._links and self._links['claim'].startswith(self._entrypoint)

    def as_claim_uri(self, timeout: typing.Any = None) -> resources.ClaimUri:
        """ Start building an API request from the claim resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ClaimUri
        """
        if self.has_claim:
            return resources.ClaimUri(self._links['claim'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.claim')

    def to_claim_uri(self, uri: str, timeout: typing.Any = None) -> resources.ClaimUri:
        """Create a re-entrant request to the claim resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ClaimUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ClaimUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_provider(self) -> bool:
        """A flag indicating the provider resource is available."""
        return self._links and 'provider' in self._links and self._links['provider'].startswith(self._entrypoint)

    def as_provider_uri(self, timeout: typing.Any = None) -> resources.ProviderUri:
        """ Start building an API request from the provider resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The provider resource has 3 navigations:
            - From / to the create role action
            - From / to the create claim action
            - From / to the role context

        Returns:
            resources.ProviderUri
        """
        if self.has_provider:
            return resources.ProviderUri(self._links['provider'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.provider')

    def to_provider_uri(self, uri: str, timeout: typing.Any = None) -> resources.ProviderUri:
        """Create a re-entrant request to the provider resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The provider resource has 3 navigations:
            - From / to the create role action
            - From / to the create claim action
            - From / to the role context

        Returns:
            resources.ProviderUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ProviderUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_account(self) -> bool:
        """A flag indicating the account resource is available."""
        return self._links and 'account' in self._links and self._links['account'].startswith(self._entrypoint)

    def as_account_uri(self, timeout: typing.Any = None) -> resources.AccountUri:
        """ Start building an API request from the account resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The account resource has 3 navigations:
            - From /identities/identifier to the set identity action
            - From /organization to the organization context
            - From /tenant to the account context

        Returns:
            resources.AccountUri
        """
        if self.has_account:
            return resources.AccountUri(self._links['account'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.account')

    def to_account_uri(self, uri: str, timeout: typing.Any = None) -> resources.AccountUri:
        """Create a re-entrant request to the account resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The account resource has 3 navigations:
            - From /identities/identifier to the set identity action
            - From /organization to the organization context
            - From /tenant to the account context

        Returns:
            resources.AccountUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.AccountUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_policy(self) -> bool:
        """A flag indicating the policy resource is available."""
        return self._links and 'policy' in self._links and self._links['policy'].startswith(self._entrypoint)

    def as_policy_uri(self, timeout: typing.Any = None) -> resources.PolicyUri:
        """ Start building an API request from the policy resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.PolicyUri
        """
        if self.has_policy:
            return resources.PolicyUri(self._links['policy'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.policy')

    def to_policy_uri(self, uri: str, timeout: typing.Any = None) -> resources.PolicyUri:
        """Create a re-entrant request to the policy resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.PolicyUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.PolicyUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_assertion(self) -> bool:
        """A flag indicating the assertion resource is available."""
        return self._links and 'assertion' in self._links and self._links['assertion'].startswith(self._entrypoint)

    def as_assertion_uri(self, timeout: typing.Any = None) -> resources.AssertionUri:
        """ Start building an API request from the assertion resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.AssertionUri
        """
        if self.has_assertion:
            return resources.AssertionUri(self._links['assertion'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.assertion')

    def to_assertion_uri(self, uri: str, timeout: typing.Any = None) -> resources.AssertionUri:
        """Create a re-entrant request to the assertion resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.AssertionUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.AssertionUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_organization(self) -> bool:
        """A flag indicating the organization resource is available."""
        return self._links and 'organization' in self._links and self._links['organization'].startswith(self._entrypoint)

    def as_organization_uri(self, timeout: typing.Any = None) -> resources.OrganizationUri:
        """ Start building an API request from the organization resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The organization resource has 1 navigation:
            - From /tenant to the account context

        Returns:
            resources.OrganizationUri
        """
        if self.has_organization:
            return resources.OrganizationUri(self._links['organization'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.organization')

    def to_organization_uri(self, uri: str, timeout: typing.Any = None) -> resources.OrganizationUri:
        """Create a re-entrant request to the organization resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The organization resource has 1 navigation:
            - From /tenant to the account context

        Returns:
            resources.OrganizationUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.OrganizationUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_user_assertion(self) -> bool:
        """A flag indicating the user assertion resource is available."""
        return self._links and 'user_assertion' in self._links and self._links['user_assertion'].startswith(self._entrypoint)

    def as_user_assertion_uri(self, timeout: typing.Any = None) -> resources.UserAssertionUri:
        """ Start building an API request from the user assertion resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UserAssertionUri
        """
        if self.has_user_assertion:
            return resources.UserAssertionUri(self._links['user_assertion'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.user_assertion')

    def to_user_assertion_uri(self, uri: str, timeout: typing.Any = None) -> resources.UserAssertionUri:
        """Create a re-entrant request to the user assertion resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UserAssertionUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.UserAssertionUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_artifacts(self) -> bool:
        """A flag indicating the artifacts resource is available."""
        return self._links and 'artifacts' in self._links and self._links['artifacts'].startswith(self._entrypoint)

    def as_artifacts_uri(self, timeout: typing.Any = None) -> resources.ArtifactsUri:
        """ Start building an API request from the artifacts resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The artifacts resource has 1 navigation:
            - From /rows to the artifact context

        Returns:
            resources.ArtifactsUri
        """
        if self.has_artifacts:
            return resources.ArtifactsUri(self._links['artifacts'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.artifacts')

    def to_artifacts_uri(self, uri: str, timeout: typing.Any = None) -> resources.ArtifactsUri:
        """Create a re-entrant request to the artifacts resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The artifacts resource has 1 navigation:
            - From /rows to the artifact context

        Returns:
            resources.ArtifactsUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ArtifactsUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_services(self) -> bool:
        """A flag indicating the services resource is available."""
        return self._links and 'services' in self._links and self._links['services'].startswith(self._entrypoint)

    def as_services_uri(self, timeout: typing.Any = None) -> resources.ServicesUri:
        """ Start building an API request from the services resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The services resource has 1 navigation:
            - From /rows to the service context

        Returns:
            resources.ServicesUri
        """
        if self.has_services:
            return resources.ServicesUri(self._links['services'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.services')

    def to_services_uri(self, uri: str, timeout: typing.Any = None) -> resources.ServicesUri:
        """Create a re-entrant request to the services resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The services resource has 1 navigation:
            - From /rows to the service context

        Returns:
            resources.ServicesUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ServicesUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_resources(self) -> bool:
        """A flag indicating the resources resource is available."""
        return self._links and 'resources' in self._links and self._links['resources'].startswith(self._entrypoint)

    def as_resources_uri(self, timeout: typing.Any = None) -> resources.ResourcesUri:
        """ Start building an API request from the resources resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ResourcesUri
        """
        if self.has_resources:
            return resources.ResourcesUri(self._links['resources'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.resources')

    def to_resources_uri(self, uri: str, timeout: typing.Any = None) -> resources.ResourcesUri:
        """Create a re-entrant request to the resources resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ResourcesUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ResourcesUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_releases(self) -> bool:
        """A flag indicating the releases resource is available."""
        return self._links and 'releases' in self._links and self._links['releases'].startswith(self._entrypoint)

    def as_releases_uri(self, timeout: typing.Any = None) -> resources.ReleasesUri:
        """ Start building an API request from the releases resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ReleasesUri
        """
        if self.has_releases:
            return resources.ReleasesUri(self._links['releases'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.releases')

    def to_releases_uri(self, uri: str, timeout: typing.Any = None) -> resources.ReleasesUri:
        """Create a re-entrant request to the releases resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ReleasesUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ReleasesUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_permissions(self) -> bool:
        """A flag indicating the permissions resource is available."""
        return self._links and 'permissions' in self._links and self._links['permissions'].startswith(self._entrypoint)

    def as_permissions_uri(self, timeout: typing.Any = None) -> resources.PermissionsUri:
        """ Start building an API request from the permissions resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.PermissionsUri
        """
        if self.has_permissions:
            return resources.PermissionsUri(self._links['permissions'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.permissions')

    def to_permissions_uri(self, uri: str, timeout: typing.Any = None) -> resources.PermissionsUri:
        """Create a re-entrant request to the permissions resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.PermissionsUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.PermissionsUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_roles(self) -> bool:
        """A flag indicating the roles resource is available."""
        return self._links and 'roles' in self._links and self._links['roles'].startswith(self._entrypoint)

    def as_roles_uri(self, timeout: typing.Any = None) -> resources.RolesUri:
        """ Start building an API request from the roles resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The roles resource has 1 navigation:
            - From /rows to the role context

        Returns:
            resources.RolesUri
        """
        if self.has_roles:
            return resources.RolesUri(self._links['roles'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.roles')

    def to_roles_uri(self, uri: str, timeout: typing.Any = None) -> resources.RolesUri:
        """Create a re-entrant request to the roles resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The roles resource has 1 navigation:
            - From /rows to the role context

        Returns:
            resources.RolesUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.RolesUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_claims(self) -> bool:
        """A flag indicating the claims resource is available."""
        return self._links and 'claims' in self._links and self._links['claims'].startswith(self._entrypoint)

    def as_claims_uri(self, timeout: typing.Any = None) -> resources.ClaimsUri:
        """ Start building an API request from the claims resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The claims resource has 2 navigations:
            - From /rows to the claim context
            - From /rows to the update claim action

        Returns:
            resources.ClaimsUri
        """
        if self.has_claims:
            return resources.ClaimsUri(self._links['claims'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.claims')

    def to_claims_uri(self, uri: str, timeout: typing.Any = None) -> resources.ClaimsUri:
        """Create a re-entrant request to the claims resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The claims resource has 2 navigations:
            - From /rows to the claim context
            - From /rows to the update claim action

        Returns:
            resources.ClaimsUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ClaimsUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_accounts(self) -> bool:
        """A flag indicating the accounts resource is available."""
        return self._links and 'accounts' in self._links and self._links['accounts'].startswith(self._entrypoint)

    def as_accounts_uri(self, timeout: typing.Any = None) -> resources.AccountsUri:
        """ Start building an API request from the accounts resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The accounts resource has 1 navigation:
            - From /rows to the account context

        Returns:
            resources.AccountsUri
        """
        if self.has_accounts:
            return resources.AccountsUri(self._links['accounts'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.accounts')

    def to_accounts_uri(self, uri: str, timeout: typing.Any = None) -> resources.AccountsUri:
        """Create a re-entrant request to the accounts resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The accounts resource has 1 navigation:
            - From /rows to the account context

        Returns:
            resources.AccountsUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.AccountsUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_policies(self) -> bool:
        """A flag indicating the policies resource is available."""
        return self._links and 'policies' in self._links and self._links['policies'].startswith(self._entrypoint)

    def as_policies_uri(self, timeout: typing.Any = None) -> resources.PoliciesUri:
        """ Start building an API request from the policies resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The policies resource has 2 navigations:
            - From /rows to the policy context
            - From /rows to the set account access action

        Returns:
            resources.PoliciesUri
        """
        if self.has_policies:
            return resources.PoliciesUri(self._links['policies'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.policies')

    def to_policies_uri(self, uri: str, timeout: typing.Any = None) -> resources.PoliciesUri:
        """Create a re-entrant request to the policies resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The policies resource has 2 navigations:
            - From /rows to the policy context
            - From /rows to the set account access action

        Returns:
            resources.PoliciesUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.PoliciesUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_assertions(self) -> bool:
        """A flag indicating the assertions resource is available."""
        return self._links and 'assertions' in self._links and self._links['assertions'].startswith(self._entrypoint)

    def as_assertions_uri(self, timeout: typing.Any = None) -> resources.AssertionsUri:
        """ Start building an API request from the assertions resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The assertions resource has 1 navigation:
            - From /rows to the assertion context

        Returns:
            resources.AssertionsUri
        """
        if self.has_assertions:
            return resources.AssertionsUri(self._links['assertions'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.assertions')

    def to_assertions_uri(self, uri: str, timeout: typing.Any = None) -> resources.AssertionsUri:
        """Create a re-entrant request to the assertions resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The assertions resource has 1 navigation:
            - From /rows to the assertion context

        Returns:
            resources.AssertionsUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.AssertionsUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_manifest(self) -> bool:
        """A flag indicating the manifest resource is available."""
        return self._links and 'manifest' in self._links and self._links['manifest'].startswith(self._entrypoint)

    def as_manifest_uri(self, timeout: typing.Any = None) -> resources.ManifestUri:
        """ Start building an API request from the manifest resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ManifestUri
        """
        if self.has_manifest:
            return resources.ManifestUri(self._links['manifest'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.manifest')

    def to_manifest_uri(self, uri: str, timeout: typing.Any = None) -> resources.ManifestUri:
        """Create a re-entrant request to the manifest resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ManifestUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ManifestUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_providers(self) -> bool:
        """A flag indicating the providers resource is available."""
        return self._links and 'providers' in self._links and self._links['providers'].startswith(self._entrypoint)

    def as_providers_uri(self, timeout: typing.Any = None) -> resources.ProvidersUri:
        """ Start building an API request from the providers resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The providers resource has 1 navigation:
            - From /rows to the provider context

        Returns:
            resources.ProvidersUri
        """
        if self.has_providers:
            return resources.ProvidersUri(self._links['providers'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.providers')

    def to_providers_uri(self, uri: str, timeout: typing.Any = None) -> resources.ProvidersUri:
        """Create a re-entrant request to the providers resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The providers resource has 1 navigation:
            - From /rows to the provider context

        Returns:
            resources.ProvidersUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ProvidersUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_available_resources(self) -> bool:
        """A flag indicating the available resources resource is available."""
        return self._links and 'available_resources' in self._links and self._links['available_resources'].startswith(self._entrypoint)

    def as_available_resources_uri(self, timeout: typing.Any = None) -> resources.AvailableResourcesUri:
        """ Start building an API request from the available resources resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.AvailableResourcesUri
        """
        if self.has_available_resources:
            return resources.AvailableResourcesUri(self._links['available_resources'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.available_resources')

    def to_available_resources_uri(self, uri: str, timeout: typing.Any = None) -> resources.AvailableResourcesUri:
        """Create a re-entrant request to the available resources resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.AvailableResourcesUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.AvailableResourcesUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_lookup_account(self) -> bool:
        """A flag indicating the lookup account resource is available."""
        return self._links and 'lookup_account' in self._links and self._links['lookup_account'].startswith(self._entrypoint)

    def as_lookup_account_uri(self, timeout: typing.Any = None) -> resources.LookupAccountUri:
        """ Start building an API request from the lookup account resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The lookup account resource has 2 navigations:
            - From / to the account context
            - From / to the update identity action

        Returns:
            resources.LookupAccountUri
        """
        if self.has_lookup_account:
            return resources.LookupAccountUri(self._links['lookup_account'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.lookup_account')

    def to_lookup_account_uri(self, uri: str, timeout: typing.Any = None) -> resources.LookupAccountUri:
        """Create a re-entrant request to the lookup account resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The lookup account resource has 2 navigations:
            - From / to the account context
            - From / to the update identity action

        Returns:
            resources.LookupAccountUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.LookupAccountUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_available_policies(self) -> bool:
        """A flag indicating the available policies resource is available."""
        return self._links and 'available_policies' in self._links and self._links['available_policies'].startswith(self._entrypoint)

    def as_available_policies_uri(self, timeout: typing.Any = None) -> resources.AvailablePoliciesUri:
        """ Start building an API request from the available policies resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.AvailablePoliciesUri
        """
        if self.has_available_policies:
            return resources.AvailablePoliciesUri(self._links['available_policies'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.available_policies')

    def to_available_policies_uri(self, uri: str, timeout: typing.Any = None) -> resources.AvailablePoliciesUri:
        """Create a re-entrant request to the available policies resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.AvailablePoliciesUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.AvailablePoliciesUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_organizations(self) -> bool:
        """A flag indicating the organizations resource is available."""
        return self._links and 'organizations' in self._links and self._links['organizations'].startswith(self._entrypoint)

    def as_organizations_uri(self, timeout: typing.Any = None) -> resources.OrganizationsUri:
        """ Start building an API request from the organizations resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.OrganizationsUri
        """
        if self.has_organizations:
            return resources.OrganizationsUri(self._links['organizations'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.organizations')

    def to_organizations_uri(self, uri: str, timeout: typing.Any = None) -> resources.OrganizationsUri:
        """Create a re-entrant request to the organizations resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.OrganizationsUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.OrganizationsUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_status(self) -> bool:
        """A flag indicating the status resource is available."""
        return self._links and 'status' in self._links and self._links['status'].startswith(self._entrypoint)

    def as_status_uri(self, timeout: typing.Any = None) -> resources.StatusUri:
        """ Start building an API request from the status resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The status resource has 1 navigation:
            - From /artifact to the artifact context

        Returns:
            resources.StatusUri
        """
        if self.has_status:
            return resources.StatusUri(self._links['status'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.status')

    def to_status_uri(self, uri: str, timeout: typing.Any = None) -> resources.StatusUri:
        """Create a re-entrant request to the status resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The status resource has 1 navigation:
            - From /artifact to the artifact context

        Returns:
            resources.StatusUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.StatusUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_refresh(self) -> bool:
        """A flag indicating the refresh resource is available."""
        return self._links and 'refresh' in self._links and self._links['refresh'].startswith(self._entrypoint)

    def as_refresh_uri(self, timeout: typing.Any = None) -> resources.RefreshUri:
        """ Start building an API request from the refresh resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The refresh resource has 3 navigations:
            - From / to the account context
            - From /tenant to the account context
            - From /assertions to the user assertion view

        Returns:
            resources.RefreshUri
        """
        if self.has_refresh:
            return resources.RefreshUri(self._links['refresh'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.refresh')

    def to_refresh_uri(self, uri: str, timeout: typing.Any = None) -> resources.RefreshUri:
        """Create a re-entrant request to the refresh resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The refresh resource has 3 navigations:
            - From / to the account context
            - From /tenant to the account context
            - From /assertions to the user assertion view

        Returns:
            resources.RefreshUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.RefreshUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_release(self) -> bool:
        """A flag indicating the release resource is available."""
        return self._links and 'release' in self._links and self._links['release'].startswith(self._entrypoint)

    def as_release_uri(self, timeout: typing.Any = None) -> resources.ReleaseUri:
        """ Start building an API request from the release resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ReleaseUri
        """
        if self.has_release:
            return resources.ReleaseUri(self._links['release'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.release')

    def to_release_uri(self, uri: str, timeout: typing.Any = None) -> resources.ReleaseUri:
        """Create a re-entrant request to the release resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ReleaseUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ReleaseUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_update_artifact(self) -> bool:
        """A flag indicating the update artifact resource is available."""
        return self._links and 'update_artifact' in self._links and self._links['update_artifact'].startswith(self._entrypoint)

    def as_update_artifact_uri(self, timeout: typing.Any = None) -> resources.UpdateArtifactUri:
        """ Start building an API request from the update artifact resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateArtifactUri
        """
        if self.has_update_artifact:
            return resources.UpdateArtifactUri(self._links['update_artifact'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.update_artifact')

    def to_update_artifact_uri(self, uri: str, timeout: typing.Any = None) -> resources.UpdateArtifactUri:
        """Create a re-entrant request to the update artifact resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateArtifactUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.UpdateArtifactUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_create_service(self) -> bool:
        """A flag indicating the create service resource is available."""
        return self._links and 'create_service' in self._links and self._links['create_service'].startswith(self._entrypoint)

    def as_create_service_uri(self, timeout: typing.Any = None) -> resources.CreateServiceUri:
        """ Start building an API request from the create service resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The create service resource has 7 navigations:
            - From / to the service context
            - From / to the update service action
            - From / to the create resource action
            - From / to the update resource action
            - From / to the reset action
            - From / to the set service status action
            - From / to the resources view

        Returns:
            resources.CreateServiceUri
        """
        if self.has_create_service:
            return resources.CreateServiceUri(self._links['create_service'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.create_service')

    def to_create_service_uri(self, uri: str, timeout: typing.Any = None) -> resources.CreateServiceUri:
        """Create a re-entrant request to the create service resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The create service resource has 7 navigations:
            - From / to the service context
            - From / to the update service action
            - From / to the create resource action
            - From / to the update resource action
            - From / to the reset action
            - From / to the set service status action
            - From / to the resources view

        Returns:
            resources.CreateServiceUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.CreateServiceUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_update_service(self) -> bool:
        """A flag indicating the update service resource is available."""
        return self._links and 'update_service' in self._links and self._links['update_service'].startswith(self._entrypoint)

    def as_update_service_uri(self, timeout: typing.Any = None) -> resources.UpdateServiceUri:
        """ Start building an API request from the update service resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateServiceUri
        """
        if self.has_update_service:
            return resources.UpdateServiceUri(self._links['update_service'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.update_service')

    def to_update_service_uri(self, uri: str, timeout: typing.Any = None) -> resources.UpdateServiceUri:
        """Create a re-entrant request to the update service resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateServiceUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.UpdateServiceUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_create_resource(self) -> bool:
        """A flag indicating the create resource resource is available."""
        return self._links and 'create_resource' in self._links and self._links['create_resource'].startswith(self._entrypoint)

    def as_create_resource_uri(self, timeout: typing.Any = None) -> resources.CreateResourceUri:
        """ Start building an API request from the create resource resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.CreateResourceUri
        """
        if self.has_create_resource:
            return resources.CreateResourceUri(self._links['create_resource'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.create_resource')

    def to_create_resource_uri(self, uri: str, timeout: typing.Any = None) -> resources.CreateResourceUri:
        """Create a re-entrant request to the create resource resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.CreateResourceUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.CreateResourceUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_update_resource(self) -> bool:
        """A flag indicating the update resource resource is available."""
        return self._links and 'update_resource' in self._links and self._links['update_resource'].startswith(self._entrypoint)

    def as_update_resource_uri(self, timeout: typing.Any = None) -> resources.UpdateResourceUri:
        """ Start building an API request from the update resource resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateResourceUri
        """
        if self.has_update_resource:
            return resources.UpdateResourceUri(self._links['update_resource'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.update_resource')

    def to_update_resource_uri(self, uri: str, timeout: typing.Any = None) -> resources.UpdateResourceUri:
        """Create a re-entrant request to the update resource resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateResourceUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.UpdateResourceUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_create_role(self) -> bool:
        """A flag indicating the create role resource is available."""
        return self._links and 'create_role' in self._links and self._links['create_role'].startswith(self._entrypoint)

    def as_create_role_uri(self, timeout: typing.Any = None) -> resources.CreateRoleUri:
        """ Start building an API request from the create role resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The create role resource has 7 navigations:
            - From / to the role context
            - From / to the create role action
            - From / to the create claim action
            - From / to the set general access action
            - From / to the update role action
            - From / to the set resource access action
            - From / to the available resources view

        Returns:
            resources.CreateRoleUri
        """
        if self.has_create_role:
            return resources.CreateRoleUri(self._links['create_role'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.create_role')

    def to_create_role_uri(self, uri: str, timeout: typing.Any = None) -> resources.CreateRoleUri:
        """Create a re-entrant request to the create role resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The create role resource has 7 navigations:
            - From / to the role context
            - From / to the create role action
            - From / to the create claim action
            - From / to the set general access action
            - From / to the update role action
            - From / to the set resource access action
            - From / to the available resources view

        Returns:
            resources.CreateRoleUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.CreateRoleUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_create_claim(self) -> bool:
        """A flag indicating the create claim resource is available."""
        return self._links and 'create_claim' in self._links and self._links['create_claim'].startswith(self._entrypoint)

    def as_create_claim_uri(self, timeout: typing.Any = None) -> resources.CreateClaimUri:
        """ Start building an API request from the create claim resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The create claim resource has 2 navigations:
            - From / to the claim context
            - From / to the update claim action

        Returns:
            resources.CreateClaimUri
        """
        if self.has_create_claim:
            return resources.CreateClaimUri(self._links['create_claim'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.create_claim')

    def to_create_claim_uri(self, uri: str, timeout: typing.Any = None) -> resources.CreateClaimUri:
        """Create a re-entrant request to the create claim resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The create claim resource has 2 navigations:
            - From / to the claim context
            - From / to the update claim action

        Returns:
            resources.CreateClaimUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.CreateClaimUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_update_claim(self) -> bool:
        """A flag indicating the update claim resource is available."""
        return self._links and 'update_claim' in self._links and self._links['update_claim'].startswith(self._entrypoint)

    def as_update_claim_uri(self, timeout: typing.Any = None) -> resources.UpdateClaimUri:
        """ Start building an API request from the update claim resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateClaimUri
        """
        if self.has_update_claim:
            return resources.UpdateClaimUri(self._links['update_claim'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.update_claim')

    def to_update_claim_uri(self, uri: str, timeout: typing.Any = None) -> resources.UpdateClaimUri:
        """Create a re-entrant request to the update claim resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateClaimUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.UpdateClaimUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_set_account_access(self) -> bool:
        """A flag indicating the set account access resource is available."""
        return self._links and 'set_account_access' in self._links and self._links['set_account_access'].startswith(self._entrypoint)

    def as_set_account_access_uri(self, timeout: typing.Any = None) -> resources.SetAccountAccessUri:
        """ Start building an API request from the set account access resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetAccountAccessUri
        """
        if self.has_set_account_access:
            return resources.SetAccountAccessUri(self._links['set_account_access'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.set_account_access')

    def to_set_account_access_uri(self, uri: str, timeout: typing.Any = None) -> resources.SetAccountAccessUri:
        """Create a re-entrant request to the set account access resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetAccountAccessUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.SetAccountAccessUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_create_account(self) -> bool:
        """A flag indicating the create account resource is available."""
        return self._links and 'create_account' in self._links and self._links['create_account'].startswith(self._entrypoint)

    def as_create_account_uri(self, timeout: typing.Any = None) -> resources.CreateAccountUri:
        """ Start building an API request from the create account resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The create account resource has 8 navigations:
            - From / to the account context
            - From / to the update account action
            - From / to the set identity action
            - From / to the update identity action
            - From / to the set account status action
            - From / to the send invitation action
            - From / to the policies view
            - From / to the assertions view

        Returns:
            resources.CreateAccountUri
        """
        if self.has_create_account:
            return resources.CreateAccountUri(self._links['create_account'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.create_account')

    def to_create_account_uri(self, uri: str, timeout: typing.Any = None) -> resources.CreateAccountUri:
        """Create a re-entrant request to the create account resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The create account resource has 8 navigations:
            - From / to the account context
            - From / to the update account action
            - From / to the set identity action
            - From / to the update identity action
            - From / to the set account status action
            - From / to the send invitation action
            - From / to the policies view
            - From / to the assertions view

        Returns:
            resources.CreateAccountUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.CreateAccountUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_create_artifact(self) -> bool:
        """A flag indicating the create artifact resource is available."""
        return self._links and 'create_artifact' in self._links and self._links['create_artifact'].startswith(self._entrypoint)

    def as_create_artifact_uri(self, timeout: typing.Any = None) -> resources.CreateArtifactUri:
        """ Start building an API request from the create artifact resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The create artifact resource has 6 navigations:
            - From / to the artifact context
            - From / to the release action
            - From / to the update artifact action
            - From / to the create service action
            - From / to the set artifact status action
            - From / to the services view

        Returns:
            resources.CreateArtifactUri
        """
        if self.has_create_artifact:
            return resources.CreateArtifactUri(self._links['create_artifact'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.create_artifact')

    def to_create_artifact_uri(self, uri: str, timeout: typing.Any = None) -> resources.CreateArtifactUri:
        """Create a re-entrant request to the create artifact resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The create artifact resource has 6 navigations:
            - From / to the artifact context
            - From / to the release action
            - From / to the update artifact action
            - From / to the create service action
            - From / to the set artifact status action
            - From / to the services view

        Returns:
            resources.CreateArtifactUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.CreateArtifactUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_set_general_access(self) -> bool:
        """A flag indicating the set general access resource is available."""
        return self._links and 'set_general_access' in self._links and self._links['set_general_access'].startswith(self._entrypoint)

    def as_set_general_access_uri(self, timeout: typing.Any = None) -> resources.SetGeneralAccessUri:
        """ Start building an API request from the set general access resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetGeneralAccessUri
        """
        if self.has_set_general_access:
            return resources.SetGeneralAccessUri(self._links['set_general_access'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.set_general_access')

    def to_set_general_access_uri(self, uri: str, timeout: typing.Any = None) -> resources.SetGeneralAccessUri:
        """Create a re-entrant request to the set general access resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetGeneralAccessUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.SetGeneralAccessUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_update_account(self) -> bool:
        """A flag indicating the update account resource is available."""
        return self._links and 'update_account' in self._links and self._links['update_account'].startswith(self._entrypoint)

    def as_update_account_uri(self, timeout: typing.Any = None) -> resources.UpdateAccountUri:
        """ Start building an API request from the update account resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateAccountUri
        """
        if self.has_update_account:
            return resources.UpdateAccountUri(self._links['update_account'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.update_account')

    def to_update_account_uri(self, uri: str, timeout: typing.Any = None) -> resources.UpdateAccountUri:
        """Create a re-entrant request to the update account resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateAccountUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.UpdateAccountUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_update_role(self) -> bool:
        """A flag indicating the update role resource is available."""
        return self._links and 'update_role' in self._links and self._links['update_role'].startswith(self._entrypoint)

    def as_update_role_uri(self, timeout: typing.Any = None) -> resources.UpdateRoleUri:
        """ Start building an API request from the update role resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateRoleUri
        """
        if self.has_update_role:
            return resources.UpdateRoleUri(self._links['update_role'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.update_role')

    def to_update_role_uri(self, uri: str, timeout: typing.Any = None) -> resources.UpdateRoleUri:
        """Create a re-entrant request to the update role resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateRoleUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.UpdateRoleUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_register(self) -> bool:
        """A flag indicating the register resource is available."""
        return self._links and 'register' in self._links and self._links['register'].startswith(self._entrypoint)

    def as_register_uri(self, timeout: typing.Any = None) -> resources.RegisterUri:
        """ Start building an API request from the register resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The register resource has 6 navigations:
            - From / to the artifact context
            - From / to the release action
            - From / to the update artifact action
            - From / to the create service action
            - From / to the set artifact status action
            - From / to the services view

        Returns:
            resources.RegisterUri
        """
        if self.has_register:
            return resources.RegisterUri(self._links['register'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.register')

    def to_register_uri(self, uri: str, timeout: typing.Any = None) -> resources.RegisterUri:
        """Create a re-entrant request to the register resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The register resource has 6 navigations:
            - From / to the artifact context
            - From / to the release action
            - From / to the update artifact action
            - From / to the create service action
            - From / to the set artifact status action
            - From / to the services view

        Returns:
            resources.RegisterUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.RegisterUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_create_provider(self) -> bool:
        """A flag indicating the create provider resource is available."""
        return self._links and 'create_provider' in self._links and self._links['create_provider'].startswith(self._entrypoint)

    def as_create_provider_uri(self, timeout: typing.Any = None) -> resources.CreateProviderUri:
        """ Start building an API request from the create provider resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The create provider resource has 3 navigations:
            - From / to the provider context
            - From / to the update provider action
            - From / to the roles view

        Returns:
            resources.CreateProviderUri
        """
        if self.has_create_provider:
            return resources.CreateProviderUri(self._links['create_provider'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.create_provider')

    def to_create_provider_uri(self, uri: str, timeout: typing.Any = None) -> resources.CreateProviderUri:
        """Create a re-entrant request to the create provider resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The create provider resource has 3 navigations:
            - From / to the provider context
            - From / to the update provider action
            - From / to the roles view

        Returns:
            resources.CreateProviderUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.CreateProviderUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_update_provider(self) -> bool:
        """A flag indicating the update provider resource is available."""
        return self._links and 'update_provider' in self._links and self._links['update_provider'].startswith(self._entrypoint)

    def as_update_provider_uri(self, timeout: typing.Any = None) -> resources.UpdateProviderUri:
        """ Start building an API request from the update provider resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateProviderUri
        """
        if self.has_update_provider:
            return resources.UpdateProviderUri(self._links['update_provider'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.update_provider')

    def to_update_provider_uri(self, uri: str, timeout: typing.Any = None) -> resources.UpdateProviderUri:
        """Create a re-entrant request to the update provider resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateProviderUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.UpdateProviderUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_set_resource_access(self) -> bool:
        """A flag indicating the set resource access resource is available."""
        return self._links and 'set_resource_access' in self._links and self._links['set_resource_access'].startswith(self._entrypoint)

    def as_set_resource_access_uri(self, timeout: typing.Any = None) -> resources.SetResourceAccessUri:
        """ Start building an API request from the set resource access resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetResourceAccessUri
        """
        if self.has_set_resource_access:
            return resources.SetResourceAccessUri(self._links['set_resource_access'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.set_resource_access')

    def to_set_resource_access_uri(self, uri: str, timeout: typing.Any = None) -> resources.SetResourceAccessUri:
        """Create a re-entrant request to the set resource access resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetResourceAccessUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.SetResourceAccessUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_create_tenant(self) -> bool:
        """A flag indicating the create tenant resource is available."""
        return self._links and 'create_tenant' in self._links and self._links['create_tenant'].startswith(self._entrypoint)

    def as_create_tenant_uri(self, timeout: typing.Any = None) -> resources.CreateTenantUri:
        """ Start building an API request from the create tenant resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The create tenant resource has 8 navigations:
            - From / to the account context
            - From / to the update account action
            - From / to the set identity action
            - From / to the update identity action
            - From / to the set account status action
            - From / to the send invitation action
            - From / to the policies view
            - From / to the assertions view

        Returns:
            resources.CreateTenantUri
        """
        if self.has_create_tenant:
            return resources.CreateTenantUri(self._links['create_tenant'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.create_tenant')

    def to_create_tenant_uri(self, uri: str, timeout: typing.Any = None) -> resources.CreateTenantUri:
        """Create a re-entrant request to the create tenant resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The create tenant resource has 8 navigations:
            - From / to the account context
            - From / to the update account action
            - From / to the set identity action
            - From / to the update identity action
            - From / to the set account status action
            - From / to the send invitation action
            - From / to the policies view
            - From / to the assertions view

        Returns:
            resources.CreateTenantUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.CreateTenantUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_set_identity(self) -> bool:
        """A flag indicating the set identity resource is available."""
        return self._links and 'set_identity' in self._links and self._links['set_identity'].startswith(self._entrypoint)

    def as_set_identity_uri(self, timeout: typing.Any = None) -> resources.SetIdentityUri:
        """ Start building an API request from the set identity resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetIdentityUri
        """
        if self.has_set_identity:
            return resources.SetIdentityUri(self._links['set_identity'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.set_identity')

    def to_set_identity_uri(self, uri: str, timeout: typing.Any = None) -> resources.SetIdentityUri:
        """Create a re-entrant request to the set identity resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetIdentityUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.SetIdentityUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_update_identity(self) -> bool:
        """A flag indicating the update identity resource is available."""
        return self._links and 'update_identity' in self._links and self._links['update_identity'].startswith(self._entrypoint)

    def as_update_identity_uri(self, timeout: typing.Any = None) -> resources.UpdateIdentityUri:
        """ Start building an API request from the update identity resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateIdentityUri
        """
        if self.has_update_identity:
            return resources.UpdateIdentityUri(self._links['update_identity'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.update_identity')

    def to_update_identity_uri(self, uri: str, timeout: typing.Any = None) -> resources.UpdateIdentityUri:
        """Create a re-entrant request to the update identity resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateIdentityUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.UpdateIdentityUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_reset(self) -> bool:
        """A flag indicating the reset resource is available."""
        return self._links and 'reset' in self._links and self._links['reset'].startswith(self._entrypoint)

    def as_reset_uri(self, timeout: typing.Any = None) -> resources.ResetUri:
        """ Start building an API request from the reset resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ResetUri
        """
        if self.has_reset:
            return resources.ResetUri(self._links['reset'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.reset')

    def to_reset_uri(self, uri: str, timeout: typing.Any = None) -> resources.ResetUri:
        """Create a re-entrant request to the reset resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ResetUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ResetUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_set_service_status(self) -> bool:
        """A flag indicating the set service status resource is available."""
        return self._links and 'set_service_status' in self._links and self._links['set_service_status'].startswith(self._entrypoint)

    def as_set_service_status_uri(self, timeout: typing.Any = None) -> resources.SetServiceStatusUri:
        """ Start building an API request from the set service status resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetServiceStatusUri
        """
        if self.has_set_service_status:
            return resources.SetServiceStatusUri(self._links['set_service_status'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.set_service_status')

    def to_set_service_status_uri(self, uri: str, timeout: typing.Any = None) -> resources.SetServiceStatusUri:
        """Create a re-entrant request to the set service status resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetServiceStatusUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.SetServiceStatusUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_set_artifact_status(self) -> bool:
        """A flag indicating the set artifact status resource is available."""
        return self._links and 'set_artifact_status' in self._links and self._links['set_artifact_status'].startswith(self._entrypoint)

    def as_set_artifact_status_uri(self, timeout: typing.Any = None) -> resources.SetArtifactStatusUri:
        """ Start building an API request from the set artifact status resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetArtifactStatusUri
        """
        if self.has_set_artifact_status:
            return resources.SetArtifactStatusUri(self._links['set_artifact_status'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.set_artifact_status')

    def to_set_artifact_status_uri(self, uri: str, timeout: typing.Any = None) -> resources.SetArtifactStatusUri:
        """Create a re-entrant request to the set artifact status resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetArtifactStatusUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.SetArtifactStatusUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_set_account_status(self) -> bool:
        """A flag indicating the set account status resource is available."""
        return self._links and 'set_account_status' in self._links and self._links['set_account_status'].startswith(self._entrypoint)

    def as_set_account_status_uri(self, timeout: typing.Any = None) -> resources.SetAccountStatusUri:
        """ Start building an API request from the set account status resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetAccountStatusUri
        """
        if self.has_set_account_status:
            return resources.SetAccountStatusUri(self._links['set_account_status'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.set_account_status')

    def to_set_account_status_uri(self, uri: str, timeout: typing.Any = None) -> resources.SetAccountStatusUri:
        """Create a re-entrant request to the set account status resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetAccountStatusUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.SetAccountStatusUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_set_release_status(self) -> bool:
        """A flag indicating the set release status resource is available."""
        return self._links and 'set_release_status' in self._links and self._links['set_release_status'].startswith(self._entrypoint)

    def as_set_release_status_uri(self, timeout: typing.Any = None) -> resources.SetReleaseStatusUri:
        """ Start building an API request from the set release status resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetReleaseStatusUri
        """
        if self.has_set_release_status:
            return resources.SetReleaseStatusUri(self._links['set_release_status'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.set_release_status')

    def to_set_release_status_uri(self, uri: str, timeout: typing.Any = None) -> resources.SetReleaseStatusUri:
        """Create a re-entrant request to the set release status resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetReleaseStatusUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.SetReleaseStatusUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_refresh_profile(self) -> bool:
        """A flag indicating the refresh profile resource is available."""
        return self._links and 'refresh_profile' in self._links and self._links['refresh_profile'].startswith(self._entrypoint)

    def as_refresh_profile_uri(self, timeout: typing.Any = None) -> resources.RefreshProfileUri:
        """ Start building an API request from the refresh profile resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.RefreshProfileUri
        """
        if self.has_refresh_profile:
            return resources.RefreshProfileUri(self._links['refresh_profile'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.refresh_profile')

    def to_refresh_profile_uri(self, uri: str, timeout: typing.Any = None) -> resources.RefreshProfileUri:
        """Create a re-entrant request to the refresh profile resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.RefreshProfileUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.RefreshProfileUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_register_app(self) -> bool:
        """A flag indicating the register app resource is available."""
        return self._links and 'register_app' in self._links and self._links['register_app'].startswith(self._entrypoint)

    def as_register_app_uri(self, timeout: typing.Any = None) -> resources.RegisterAppUri:
        """ Start building an API request from the register app resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        The register app resource has 1 navigation:
            - From / to the account context

        Returns:
            resources.RegisterAppUri
        """
        if self.has_register_app:
            return resources.RegisterAppUri(self._links['register_app'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.register_app')

    def to_register_app_uri(self, uri: str, timeout: typing.Any = None) -> resources.RegisterAppUri:
        """Create a re-entrant request to the register app resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        The register app resource has 1 navigation:
            - From / to the account context

        Returns:
            resources.RegisterAppUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.RegisterAppUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_override_account_access(self) -> bool:
        """A flag indicating the override account access resource is available."""
        return self._links and 'override_account_access' in self._links and self._links['override_account_access'].startswith(self._entrypoint)

    def as_override_account_access_uri(self, timeout: typing.Any = None) -> resources.OverrideAccountAccessUri:
        """ Start building an API request from the override account access resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.OverrideAccountAccessUri
        """
        if self.has_override_account_access:
            return resources.OverrideAccountAccessUri(self._links['override_account_access'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.override_account_access')

    def to_override_account_access_uri(self, uri: str, timeout: typing.Any = None) -> resources.OverrideAccountAccessUri:
        """Create a re-entrant request to the override account access resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.OverrideAccountAccessUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.OverrideAccountAccessUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_override_account(self) -> bool:
        """A flag indicating the override account resource is available."""
        return self._links and 'override_account' in self._links and self._links['override_account'].startswith(self._entrypoint)

    def as_override_account_uri(self, timeout: typing.Any = None) -> resources.OverrideAccountUri:
        """ Start building an API request from the override account resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.OverrideAccountUri
        """
        if self.has_override_account:
            return resources.OverrideAccountUri(self._links['override_account'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.override_account')

    def to_override_account_uri(self, uri: str, timeout: typing.Any = None) -> resources.OverrideAccountUri:
        """Create a re-entrant request to the override account resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.OverrideAccountUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.OverrideAccountUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_assign_identity(self) -> bool:
        """A flag indicating the assign identity resource is available."""
        return self._links and 'assign_identity' in self._links and self._links['assign_identity'].startswith(self._entrypoint)

    def as_assign_identity_uri(self, timeout: typing.Any = None) -> resources.AssignIdentityUri:
        """ Start building an API request from the assign identity resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.AssignIdentityUri
        """
        if self.has_assign_identity:
            return resources.AssignIdentityUri(self._links['assign_identity'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.assign_identity')

    def to_assign_identity_uri(self, uri: str, timeout: typing.Any = None) -> resources.AssignIdentityUri:
        """Create a re-entrant request to the assign identity resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.AssignIdentityUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.AssignIdentityUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_update_organization(self) -> bool:
        """A flag indicating the update organization resource is available."""
        return self._links and 'update_organization' in self._links and self._links['update_organization'].startswith(self._entrypoint)

    def as_update_organization_uri(self, timeout: typing.Any = None) -> resources.UpdateOrganizationUri:
        """ Start building an API request from the update organization resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateOrganizationUri
        """
        if self.has_update_organization:
            return resources.UpdateOrganizationUri(self._links['update_organization'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.update_organization')

    def to_update_organization_uri(self, uri: str, timeout: typing.Any = None) -> resources.UpdateOrganizationUri:
        """Create a re-entrant request to the update organization resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.UpdateOrganizationUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.UpdateOrganizationUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_send_invitation(self) -> bool:
        """A flag indicating the send invitation resource is available."""
        return self._links and 'send_invitation' in self._links and self._links['send_invitation'].startswith(self._entrypoint)

    def as_send_invitation_uri(self, timeout: typing.Any = None) -> resources.SendInvitationUri:
        """ Start building an API request from the send invitation resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SendInvitationUri
        """
        if self.has_send_invitation:
            return resources.SendInvitationUri(self._links['send_invitation'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.send_invitation')

    def to_send_invitation_uri(self, uri: str, timeout: typing.Any = None) -> resources.SendInvitationUri:
        """Create a re-entrant request to the send invitation resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SendInvitationUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.SendInvitationUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_setup(self) -> bool:
        """A flag indicating the setup resource is available."""
        return self._links and 'setup' in self._links and self._links['setup'].startswith(self._entrypoint)

    def as_setup_uri(self, timeout: typing.Any = None) -> resources.SetupUri:
        """ Start building an API request from the setup resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetupUri
        """
        if self.has_setup:
            return resources.SetupUri(self._links['setup'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.setup')

    def to_setup_uri(self, uri: str, timeout: typing.Any = None) -> resources.SetupUri:
        """Create a re-entrant request to the setup resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.SetupUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.SetupUri(combined, self._handler, self._entrypoint, self._auth, timeout)

    @property
    def has_configure(self) -> bool:
        """A flag indicating the configure resource is available."""
        return self._links and 'configure' in self._links and self._links['configure'].startswith(self._entrypoint)

    def as_configure_uri(self, timeout: typing.Any = None) -> resources.ConfigureUri:
        """ Start building an API request from the configure resource url.

        Args:
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ConfigureUri
        """
        if self.has_configure:
            return resources.ConfigureUri(self._links['configure'], self._handler, self._entrypoint, self._auth, timeout)
        else:
            raise KeyError('grant.configure')

    def to_configure_uri(self, uri: str, timeout: typing.Any = None) -> resources.ConfigureUri:
        """Create a re-entrant request to the configure resource url.

        Args:
            uri: A url fragment for the request
            timeout: The timeout to be applied to any subsequent requests

        Returns:
            resources.ConfigureUri
        """
        combined = urljoin(self._entrypoint, uri)
        return resources.ConfigureUri(combined, self._handler, self._entrypoint, self._auth, timeout)