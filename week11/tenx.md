# 10x Traffic Limit

At 10x today's query volume, **Rate Limits** on our LLM provider will break first: we currently peak at 40 requests/minute, and 10x puts us at 400 requests/minute, instantly shattering our Tier 2 provider limit of 250 RPM.
