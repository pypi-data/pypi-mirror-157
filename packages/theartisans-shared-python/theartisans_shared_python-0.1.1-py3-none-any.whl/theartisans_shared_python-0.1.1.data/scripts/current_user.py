import os
from typing import Any, List, Optional, TypedDict, Callable
import jwt
from the_artisans_shared.types import UserRoleValues, SubscriptionTypeValues
from flask import request

class Subscription(TypedDict):
    id: str
    subscriptionType: SubscriptionTypeValues
    expiryDate: str

class UserPayload(TypedDict):
    id: str
    email: str
    roles: List[UserRoleValues]
    firstName: Optional[str]
    lastName: Optional[str]
    active: bool
    banned: bool
    subscription: Optional[Subscription]
    billingId: Optional[str]
    mobileNumber: Optional[str]
    loginCount: int
    lastLogin: str
    profileImageUrl: Optional[str]

def current_user():    
    try:
        userJWT = request.environ['session']['jwt']
        current_user = jwt.decode(userJWT, os.environ.get('JWT_KEY'), ['HS256']) 
    except:
        current_user = None
    setattr(request, 'current_user', current_user)
        