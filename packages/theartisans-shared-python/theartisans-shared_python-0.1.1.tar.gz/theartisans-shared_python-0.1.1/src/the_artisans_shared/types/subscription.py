import enum
from typing import Literal, get_args

class SubscriptionType(enum.Enum):
    BASIC = 'BASIC'
    PRO = 'PRO'
    PREMIUM = 'PREMIUM'

SubscriptionTypeValues = Literal['BASIC', 'PRO', 'PREMIUM']
assert set(get_args(SubscriptionTypeValues)) == {member.value for member in SubscriptionType}