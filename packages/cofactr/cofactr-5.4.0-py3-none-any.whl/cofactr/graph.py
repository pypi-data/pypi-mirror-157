"""Cofactr graph API client."""
# pylint: disable=too-many-arguments
# Python Modules
import json
from typing import Dict, List, Literal, Optional

# 3rd Party Modules
import urllib3

# Local Modules
from cofactr.schema import (
    OfferSchemaName,
    OrgSchemaName,
    ProductSchemaName,
    SupplierSchemaName,
    schema_to_offer,
    schema_to_org,
    schema_to_product,
    schema_to_supplier,
)
from cofactr.schema.types import Completion

Protocol = Literal["http", "https"]


drop_none_values = lambda d: {k: v for k, v in d.items() if v is not None}


def get_products(
    http,
    url,
    client_id,
    api_key,
    query,
    fields,
    before,
    after,
    limit,
    external,
    force_refresh,
    schema,
    filtering,
):
    """Get products."""
    res = http.request(
        "GET",
        f"{url}/products",
        headers=drop_none_values(
            {
                "X-CLIENT-ID": client_id,
                "X-API-KEY": api_key,
            }
        ),
        fields=drop_none_values(
            {
                "q": query,
                "fields": fields,
                "before": before,
                "after": after,
                "limit": limit,
                "external": external,
                "force_refresh": force_refresh,
                "schema": schema,
                "filtering": json.dumps(filtering) if filtering else None,
            }
        ),
    )

    return json.loads(res.data.decode("utf-8"))


def get_orgs(
    http,
    url,
    client_id,
    api_key,
    query,
    before,
    after,
    limit,
    schema,
):
    """Get orgs."""
    res = http.request(
        "GET",
        f"{url}/orgs",
        headers=drop_none_values(
            {
                "X-CLIENT-ID": client_id,
                "X-API-KEY": api_key,
            }
        ),
        fields=drop_none_values(
            {
                "q": query,
                "before": before,
                "after": after,
                "limit": limit,
                "schema": schema,
            }
        ),
    )

    return json.loads(res.data.decode("utf-8"))


class GraphAPI:  # pylint: disable=too-many-instance-attributes
    """A client-side representation of the Cofactr graph API."""

    PROTOCOL: Protocol = "https"
    HOST = "graph.cofactr.com"

    def __init__(
        self,
        protocol: Optional[Protocol] = PROTOCOL,
        host: Optional[str] = HOST,
        default_product_schema: ProductSchemaName = ProductSchemaName.FLAGSHIP,
        default_org_schema: OrgSchemaName = OrgSchemaName.FLAGSHIP,
        default_offer_schema: OfferSchemaName = OfferSchemaName.FLAGSHIP,
        default_supplier_schema: SupplierSchemaName = SupplierSchemaName.FLAGSHIP,
        client_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):

        self.url = f"{protocol}://{host}"
        self.http = urllib3.PoolManager()
        self.default_product_schema = default_product_schema
        self.default_org_schema = default_org_schema
        self.default_offer_schema = default_offer_schema
        self.default_supplier_schema = default_supplier_schema
        self.client_id = client_id
        self.api_key = api_key

    def check_health(self):
        """Check the operational status of the service."""

        res = self.http.request("GET", self.url)

        return json.loads(res.data.decode("utf-8"))

    def get_products(
        self,
        query: Optional[str] = None,
        fields: Optional[str] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[int] = None,
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[ProductSchemaName] = None,
        filtering: Optional[List[Dict]] = None,
    ):
        """Get products.

        Args:
            query: Search query.
            fields: Used to filter properties that the response should contain. A field can be a
                concrete property like "mpn" or an abstract group of properties like "assembly".
                Example: `"id,aliases,labels,statements{spec,assembly},offers"`.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of documents.
            external: Whether to query external sources.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            filtering: Filter products.
                Example: `[{"field":"id","operator":"IN","value":["CCCQSA3G9SMR","CCV1F7A8UIYH"]}]`.
        """
        if not schema:
            schema = self.default_product_schema

        res = get_products(
            http=self.http,
            url=self.url,
            client_id=self.client_id,
            api_key=self.api_key,
            query=query,
            fields=fields,
            external=external,
            force_refresh=force_refresh,
            before=before,
            after=after,
            limit=limit,
            schema=schema.value,
            filtering=filtering,
        )

        Product = schema_to_product[schema]  # pylint: disable=invalid-name

        res["data"] = [Product(**data) for data in res["data"]]

        return res

    def get_products_by_ids(
        self,
        ids: List[str],
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[ProductSchemaName] = None,
    ):
        """Get a batch of products.

        Note:
            A maximum of 500 IDs can be provided. Any more than that, and the server will return
            a 422 error. Consider breaking the request into batches.

        Args:
            ids: Cofactr product IDs to match on.
            external: Whether to query external sources in order to refresh data if applicable.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
        """
        if not schema:
            schema = self.default_product_schema

        extracted_products = self.get_products(
            external=external,
            force_refresh=force_refresh,
            schema=schema,
            filtering=[{"field": "id", "operator": "IN", "value": ids}],
            limit=len(ids),
        )["data"]

        extracted_product_map = {p.id: p for p in extracted_products}

        products = {id_: extracted_product_map[id_] for id_ in ids}

        return products

    def get_orgs(
        self,
        query: Optional[str] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[int] = None,
        schema: Optional[OrgSchemaName] = None,
    ):
        """Get organizations.

        Args:
            query: Search query.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of documents.
            schema: Response schema.
        """
        if not schema:
            schema = self.default_org_schema

        res = get_orgs(
            http=self.http,
            url=self.url,
            client_id=self.client_id,
            api_key=self.api_key,
            query=query,
            before=before,
            after=after,
            limit=limit,
            schema=schema.value,
        )

        Org = schema_to_org[schema]  # pylint: disable=invalid-name

        res["data"] = [Org(**data) for data in res["data"]]

        return res

    def get_suppliers(
        self,
        query: Optional[str] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[int] = None,
        schema: Optional[OrgSchemaName] = None,
    ):
        """Get suppliers.

        Args:
            query: Search query.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of documents.
            schema: Response schema.
        """
        if not schema:
            schema = self.default_org_schema

        res = get_orgs(
            http=self.http,
            url=self.url,
            client_id=self.client_id,
            api_key=self.api_key,
            query=query,
            before=before,
            after=after,
            limit=limit,
            schema=schema.value,
        )

        Org = schema_to_org[schema]  # pylint: disable=invalid-name

        res["data"] = [Org(**data) for data in res["data"]]

        return res

    def autocomplete_orgs(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        types: Optional[str] = None,
    ) -> Dict[Literal["data"], Completion]:
        """Autocomplete organizations.

        Args:
            query: Search query.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of
                documents.
            types: Filter for types of organizations.
                Example: "supplier" filters to suppliers.
                Example: "supplier|manufacturer" filters to orgs that are a
                    supplier or a manufacturer.
        """

        res = self.http.request(
            "GET",
            f"{self.url}/orgs/autocomplete",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            fields=drop_none_values(
                {
                    "q": query,
                    "limit": limit,
                    "types": types,
                }
            ),
        )

        return json.loads(res.data.decode("utf-8"))

    def get_product(
        self,
        id: str,
        fields: Optional[str] = None,
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[ProductSchemaName] = None,
    ):
        """Get product.

        Args:
            fields: Used to filter properties that the response should contain. A field can be a
                concrete property like "mpn" or an abstract group of properties like "assembly".
                Example: "id,aliases,labels,statements{spec,assembly},offers"
            external: Whether to query external sources in order to update information for the
                given product.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
        """
        if not schema:
            schema = self.default_product_schema

        res = json.loads(
            self.http.request(
                "GET",
                f"{self.url}/products/{id}",
                headers=drop_none_values(
                    {
                        "X-CLIENT-ID": self.client_id,
                        "X-API-KEY": self.api_key,
                    }
                ),
                fields=drop_none_values(
                    {
                        "fields": fields,
                        "external": external,
                        "force_refresh": force_refresh,
                        "schema": schema.value,
                    }
                ),
            ).data.decode("utf-8")
        )

        Product = schema_to_product[schema]  # pylint: disable=invalid-name

        res["data"] = Product(**res["data"]) if (res and res.get("data")) else None

        return res

    def get_offers(
        self,
        product_id: str,
        fields: Optional[str] = None,
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[OfferSchemaName] = None,
    ):
        """Get product.

        Args:
            product_id: ID of the product to get offers for.
            fields: Used to filter properties that the response should contain.
            external: Whether to query external sources in order to update information.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
        """
        if not schema:
            schema = self.default_offer_schema

        res = json.loads(
            self.http.request(
                "GET",
                f"{self.url}/products/{product_id}/offers",
                headers=drop_none_values(
                    {
                        "X-CLIENT-ID": self.client_id,
                        "X-API-KEY": self.api_key,
                    }
                ),
                fields=drop_none_values(
                    {
                        "fields": fields,
                        "external": external,
                        "force_refresh": force_refresh,
                        "schema": schema.value,
                    }
                ),
            ).data.decode("utf-8")
        )

        Offer = schema_to_offer[schema]  # pylint: disable=invalid-name

        res["data"] = [Offer(**data) for data in res["data"]]

        return res

    def get_org(
        self,
        id: str,
        schema: Optional[OrgSchemaName] = None,
    ):
        """Get organization."""
        if not schema:
            schema = self.default_org_schema

        res = json.loads(
            self.http.request(
                "GET",
                f"{self.url}/orgs/{id}",
                headers=drop_none_values(
                    {
                        "X-CLIENT-ID": self.client_id,
                        "X-API-KEY": self.api_key,
                    }
                ),
                fields=drop_none_values({"schema": schema.value}),
            ).data.decode("utf-8")
        )

        Org = schema_to_org[schema]  # pylint: disable=invalid-name

        res["data"] = Org(**res["data"]) if (res and res.get("data")) else None

        return res

    def get_supplier(
        self,
        id: str,
        schema: Optional[SupplierSchemaName] = None,
    ):
        """Get supplier."""
        if not schema:
            schema = self.default_supplier_schema

        res = json.loads(
            self.http.request(
                "GET",
                f"{self.url}/orgs/{id}",
                headers=drop_none_values(
                    {
                        "X-CLIENT-ID": self.client_id,
                        "X-API-KEY": self.api_key,
                    }
                ),
                fields=drop_none_values({"schema": schema.value}),
            ).data.decode("utf-8")
        )

        Supplier = schema_to_supplier[schema]  # pylint: disable=invalid-name

        res["data"] = Supplier(**res["data"]) if (res and res.get("data")) else None

        return res
