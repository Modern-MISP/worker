import dns
from dns.resolver import LifetimeTimeout, NXDOMAIN, YXDOMAIN, NoNameservers

from mmisp.worker.exceptions.plugin_exceptions import PluginExecutionException
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPluginType, PluginIO, \
    EnrichmentPluginInfo
from mmisp.worker.plugins.factory import PluginFactory
from mmisp.worker.plugins.plugin import PluginType


class DNSResolverPlugin:
    """
    This plugin resolves domain name and hostname attributes to IP addresses.

    Implementation inspired by the MISP-Plugin 'DNS' from Alexandre Dulaunoy.
    https://github.com/MISP/misp-modules/blob/main/misp_modules/modules/expansion/dns.py
    """

    PLUGIN_INFO: EnrichmentPluginInfo = (
        EnrichmentPluginInfo(NAME="DNS Resolver",
                             PLUGIN_TYPE=PluginType.ENRICHMENT,
                             DESCRIPTION="This plugin resolves domain name and hostname attributes to IP addresses.",
                             AUTHOR="Amadeus Haessler", VERSION="1.0",
                             ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION, EnrichmentPluginType.HOVER},
                             MISP_ATTRIBUTES=PluginIO(INPUT=['hostname', 'domain', 'domain|ip'],
                                                      OUTPUT=['ip-src', 'ip-dst'])))

    NAMESERVERS: list[str] = ['1.1.1.1', '8.8.8.8']
    """List of nameservers to use for DNS resolution."""

    def __init__(self, misp_attribute: MispEventAttribute):
        if not misp_attribute:
            raise ValueError("MISP Event-Attribute is required but was None.")
        elif misp_attribute.type not in self.PLUGIN_INFO.MISP_ATTRIBUTES.INPUT:
            raise ValueError(f"Invalid attribute type '{misp_attribute.type}' for DNS Resolver Plugin.")
        else:
            self.__misp_attribute = misp_attribute

    def run(self) -> EnrichAttributeResult:
        dns_name: str

        if self.__misp_attribute.type == 'domain|ip':
            dns_name = self.__misp_attribute.value.split('|')[0]
        else:
            dns_name = self.__misp_attribute.value

        ip_address: str = str(self.__resolve_dns_name(dns_name))
        result: EnrichAttributeResult = EnrichAttributeResult()

        if ip_address:
            result.attributes.append(MispEventAttribute(event_id=self.__misp_attribute.event_id,
                                                        object_id=self.__misp_attribute.object_id,
                                                        category=self.__misp_attribute.category,
                                                        type='ip-src',
                                                        to_ids=False,
                                                        distribution=self.__misp_attribute.distribution,
                                                        value=ip_address,
                                                        event_uuid=self.__misp_attribute.event_uuid))

        return result

    def __resolve_dns_name(self, dns_name: str) -> str:
        dns_resolver: dns.resolver.Resolver = dns.resolver.Resolver()
        dns_resolver.nameservers = self.NAMESERVERS
        dns_resolver.timeout = 2
        dns_resolver.lifetime = 2

        answer: dns.resolver.Answer
        try:
            answer = dns_resolver.resolve(dns_name, 'A', raise_on_no_answer=False)
        except LifetimeTimeout as timeout_exception:
            raise PluginExecutionException(f"'{self.PLUGIN_INFO.NAME}'-Plugin: Nameservers not reachable.")
        except NXDOMAIN as nxdomain_exception:
            raise PluginExecutionException(f"'{self.PLUGIN_INFO.NAME}'-Plugin: Timeout: DNS server didn't respond.")
        except YXDOMAIN as yxdomain_exception:
            raise PluginExecutionException(f"'{self.PLUGIN_INFO.NAME}'-Plugin: "
                                           f"The name '{dns_name}' could not be resolved: {yxdomain_exception}")
        except NoNameservers as no_nameservers_exception:
            raise PluginExecutionException(f"'{self.PLUGIN_INFO.NAME}'-Plugin: Nameservers not reachable.")

        if answer:
            return answer[0]
        else:
            return ""


def register(factory: PluginFactory):
    factory.register(DNSResolverPlugin)
