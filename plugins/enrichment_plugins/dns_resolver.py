from collections.abc import Iterable
from typing import Self

import dns
from dns.resolver import NXDOMAIN, YXDOMAIN, LifetimeTimeout, NoNameservers
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.db.models.attribute import Attribute
from mmisp.plugins import factory
from mmisp.plugins.enrichment.data import EnrichAttributeResult, NewAttribute
from mmisp.plugins.exceptions import PluginExecutionException
from mmisp.plugins.types import EnrichmentPluginType, PluginType


class DNSResolverPlugin:
    """
    This plugin resolves domain name and hostname attributes to IP addresses.

    Implementation inspired by the MISP-Plugin 'DNS' from Alexandre Dulaunoy.
    https://github.com/MISP/misp-modules/blob/main/misp_modules/modules/expansion/dns.py
    """

    NAME: str = "DNS Resolver"
    PLUGIN_TYPE: PluginType = PluginType.ENRICHMENT
    DESCRIPTION: str = "This plugin resolves domain name and hostname attributes to IP addresses."
    AUTHOR: str = "Amadeus Haessler"
    VERSION: str = "1.0"
    ENRICHMENT_TYPE: Iterable[EnrichmentPluginType] = frozenset(
        {EnrichmentPluginType.EXPANSION, EnrichmentPluginType.HOVER}
    )
    ATTRIBUTE_TYPES_INPUT = ["hostname", "domain", "domain|ip"]
    ATTRIBUTE_TYPES_OUTPUT = ["ip-src", "ip-dst"]

    NAMESERVERS: list[str] = ["1.1.1.1", "8.8.8.8"]
    """List of nameservers to use for DNS resolution."""

    async def run(self: Self, db: AsyncSession, attribute: Attribute) -> EnrichAttributeResult:
        misp_attribute = attribute

        if not misp_attribute:
            raise ValueError("MISP Event-Attribute is required but was None.")
        elif misp_attribute.type not in self.ATTRIBUTE_TYPES_INPUT:
            raise ValueError(f"Invalid attribute type '{misp_attribute.type}' for DNS Resolver Plugin.")
        else:
            self.__misp_attribute = misp_attribute
        dns_name: str

        if self.__misp_attribute.type == "domain|ip":
            dns_name = self.__misp_attribute.value.split("|")[0]
        else:
            dns_name = self.__misp_attribute.value

        ip_address: str = str(self.__resolve_dns_name(dns_name))
        result: EnrichAttributeResult = EnrichAttributeResult()

        if ip_address:
            result.attributes.append(
                NewAttribute(
                    attribute=AddAttributeBody(
                        event_id=self.__misp_attribute.event_id,
                        object_id=self.__misp_attribute.object_id,
                        category=self.__misp_attribute.category,
                        type="ip-src",
                        to_ids=False,
                        distribution=self.__misp_attribute.distribution,
                        value=ip_address,
                        event_uuid=self.__misp_attribute.event_uuid,
                    )
                )
            )

        return result

    def __resolve_dns_name(self: Self, dns_name: str) -> str:
        dns_resolver: dns.resolver.Resolver = dns.resolver.Resolver()
        dns_resolver.nameservers = self.NAMESERVERS
        dns_resolver.timeout = 2
        dns_resolver.lifetime = 2

        answer: dns.resolver.Answer
        try:
            answer = dns_resolver.resolve(dns_name, "A", raise_on_no_answer=False)
        except LifetimeTimeout:
            raise PluginExecutionException(f"'{self.PLUGIN_INFO.NAME}'-Plugin: Nameservers not reachable.")
        except NXDOMAIN:
            raise PluginExecutionException(f"'{self.PLUGIN_INFO.NAME}'-Plugin: Timeout: DNS server didn't respond.")
        except YXDOMAIN as yxdomain_exception:
            raise PluginExecutionException(
                f"'{self.PLUGIN_INFO.NAME}'-Plugin: The name '{dns_name}' could not be resolved: {yxdomain_exception}"
            )
        except NoNameservers:
            raise PluginExecutionException(f"'{self.PLUGIN_INFO.NAME}'-Plugin: Nameservers not reachable.")

        if answer:
            return answer[0]
        else:
            return ""


factory.register(DNSResolverPlugin())
