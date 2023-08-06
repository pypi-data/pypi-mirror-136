class Quality():
    def __init__(self, quality: dict) -> None:
        self.quality = quality.get('quality', None)
        self.latency = quality.get('latency', None)
        self.bandwidth = quality.get('bandwidth', None)


class Price():
    def __init__(self, price: dict) -> None:
        self.currency = price.get('currency', None)
        self.per_hour = price.get('per_hour', None)
        self.per_gib = price.get('per_gib', None)


class Location():
    def __init__(self, location: dict) -> None:
        self.continent = location.get('continent', None)
        self.country = location.get('country', None)
        self.city = location.get('city', None)
        self.asn = location.get('asn', None)
        self.isp = location.get('isp', None)
        self.ip_type = location.get('ip_type', None)


class Proposal:
    def __init__(self, proposal: dict) -> None:
        self.format = proposal.get('format', None)
        self.compatibility = proposal.get('compatibility', None)
        self.provider_id = proposal.get('provider_id', None)
        self.service_type = proposal.get('service_type', None)
        self.location = Location(proposal.get('location', {}))
        self.price = Price(proposal.get('price', {}))
        self.quality = Quality(proposal.get('quality', {}))


class Proposals():
    def __init__(self, proposals_json: dict) -> None:
        self.proposals = []
        for proposal in proposals_json['proposals']:
            self.proposals.append(Proposal(proposal))
    
    def filtered_by_country(self, country:str, proposals:list=None):
        filtered_proposals = list(filter(lambda proposal: self.__filter_by_country(proposal, country), proposals if proposals else self.proposals))
        return filtered_proposals
    
    def filtered_by_ip_type(self, ip_type:str, proposals:list=None):
        filtered_proposals = list(filter(lambda proposal: self.__filter_by_ip_type(proposal, ip_type), proposals if proposals else self.proposals))
        return filtered_proposals
        
    def __filter_by_country(self, proposal:Proposal, country:str):
        if proposal.location.country == country:
            return True
        else:
            return False
    
    def __filter_by_ip_type(self, proposal:Proposal, ip_type:str):
        if proposal.location.ip_type == ip_type:
            return True
        else:
            return False