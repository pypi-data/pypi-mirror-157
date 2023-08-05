import urllib.parse
from typing import AsyncIterator

from trinsic.proto.sdk.options.v1 import ServiceOptions
from trinsic.proto.services.trustregistry.v1 import (
    TrustRegistryStub,
    RemoveFrameworkResponse,
    SearchRegistryResponse,
    FetchDataResponse,
    AddFrameworkRequest,
    RemoveFrameworkRequest,
    SearchRegistryRequest,
    FetchDataRequest,
    AddFrameworkResponse,
    RegisterMemberRequest,
    RegisterMemberResponse,
    UnregisterMemberRequest,
    UnregisterMemberResponse,
    GetMembershipStatusRequest,
    GetMembershipStatusResponse,
)
from trinsic.service_base import ServiceBase


class TrustRegistryService(ServiceBase):
    """
    Wrapper for [Trust Registry Service](/reference/services/trust-registry/)
    """

    def __init__(
        self,
        *,
        server_config: ServiceOptions = None,
    ):
        super().__init__(server_config)
        self.client: TrustRegistryStub = self.stub_with_metadata(TrustRegistryStub)

    async def add_framework(
        self, *, request: AddFrameworkRequest
    ) -> AddFrameworkResponse:
        """
        [Create a governance framework](/reference/services/trust-registry/#create-a-ecosystem-governance-framework)
        Args:
        """
        governance_url = urllib.parse.urlsplit(
            request.governance_framework_uri, allow_fragments=False
        )
        # Verify complete url
        if governance_url.scheme and governance_url.netloc:
            return await self.client.add_framework(add_framework_request=request)
        else:
            raise ValueError(f"Invalid URI string={request.governance_framework_uri}")

    async def remove_framework(
        self, *, request: RemoveFrameworkRequest
    ) -> RemoveFrameworkResponse:
        return await self.client.remove_framework(remove_framework_request=request)

    async def register_member(
        self, *, request: RegisterMemberRequest
    ) -> RegisterMemberResponse:
        """
        [Register the issuer](/reference/services/trust-registry/#register-issuers-and-verifiers)
        Args:
        Raises:
            ValueError: if date ranges are not provided
        """
        return await self.client.register_member(register_member_request=request)

    async def unregister_member(
        self, *, request: UnregisterMemberRequest
    ) -> UnregisterMemberResponse:
        """
        [Unregister the issuer](/reference/services/trust-registry/#unregister-issuers-and-verifiers)
        Args:
        Raises:
            NotImplementedError: Unsupported call
        """
        return await self.client.unregister_member(unregister_member_request=request)

    async def get_membership_status(
        self, *, request: GetMembershipStatusRequest
    ) -> GetMembershipStatusResponse:
        """
        [Check for authoritative status](/reference/services/trust-registry/#check-authoritative-status)
        Args:
        Returns:
            [RegistrationStatus](/reference/proto/#checkissuerstatusresponse)
        """

        return await self.client.get_membership_status(
            get_membership_status_request=request
        )

    async def search_registry(
        self, *, request: SearchRegistryRequest = None
    ) -> SearchRegistryResponse:
        """
        [Search the registry](/reference/services/trust-registry/#search)
        Args:
        Returns:
            [SearchRegistryResponse](/reference/proto/#searchregistryresponse)
        """
        request = request or SearchRegistryRequest()
        request.query = request.query or "SELECT * FROM c OFFSET 0 LIMIT 100"
        return await self.client.search_registry(search_registry_request=request)

    async def fetch_data(
        self, *, request: FetchDataRequest
    ) -> AsyncIterator[FetchDataResponse]:
        return self.client.fetch_data(fetch_data_request=request)
