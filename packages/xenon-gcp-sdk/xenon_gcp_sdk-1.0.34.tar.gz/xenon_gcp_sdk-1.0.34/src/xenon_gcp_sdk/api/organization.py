from typing import List
from dacite import from_dict
from dataclasses import dataclass

from xenon_gcp_sdk.api.base_event import BaseEvent


@dataclass
class User:
    email: str
    admin: bool

    def __init__(self, email, admin):
        self.email = email
        self.admin = admin


@dataclass
class Organization(BaseEvent):
    id: str
    name: str
    auth_type: str
    users: List[User]

    @classmethod
    def from_firestore_response(cls, doc):
        names = doc.to_dict()
        cls.id = doc.id
        cls.name = names['name']
        cls.auth_type = names['auth_type']
        cls.users = list(map(lambda user: from_dict(data_class=User, data=user), names['users']))
        return cls

    def __init__(self, org_id, name, auth_type, users):
        self.id = org_id
        self.name = name
        self.auth_type = auth_type
        self.users = users
