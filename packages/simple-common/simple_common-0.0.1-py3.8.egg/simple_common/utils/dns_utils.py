import dns.resolver


def dns_query(target):
    result = dns.resolver.resolve(target)
    return result.response.answer
