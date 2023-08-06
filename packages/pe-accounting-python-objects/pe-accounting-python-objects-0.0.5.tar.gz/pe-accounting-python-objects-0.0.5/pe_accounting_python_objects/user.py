#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from pprint import pprint
from typing import List, Optional

from dateutil.relativedelta import relativedelta
from loguru import logger
from pe_accounting_python_api import PeRestClient
from pydantic import BaseModel, Field


class PeCredentials(BaseModel):
    company_id: str
    api_access_token: str


class EmploymentContract(BaseModel):
    class Config:
        extra = "allow"

    user: dict
    ssn: str
    monthly_salary: int = Field(..., alias="monthly-salary")
    employment_start_date: date = Field(..., alias="employment-start-date")
    manager_user: dict = Field(None, alias="manager-user")
    monthly_salary_start_date: date = Field(None, alias="monthly-salary-start-date")
    vacation_entitlements: dict = Field(None, alias="vacation-entitlements")


class PeUser(BaseModel):

    """Represents a user in PE Accounting."""

    class Config:
        arbitrary_types_allowed = True

    _pe_rest_client: Optional[PeRestClient] = None
    pe_credentials: Optional[PeCredentials] = None

    index: int = 1
    active: bool
    contract: EmploymentContract
    dimension_entry: dict = Field(..., alias="dimension-entry")
    dimensions: dict
    email: str
    id: int
    internal_id: int = Field(..., alias="internal-id")
    name: str

    @classmethod
    def pe_rest_client(cls) -> Optional[PeRestClient]:
        """Lazy create PeRestClient. Store in class attrib."""
        if not hasattr(cls, "pe_credentials"):
            raise Exception("self.pe_credentials has to be set before using this class.")
        if not cls._pe_rest_client and cls.pe_credentials:
            cls._pe_rest_client = PeRestClient(**cls.pe_credentials.dict())
        return cls._pe_rest_client

    @property
    def manager(self):
        if self.contract.manager_user:
            return self.users_dict[self.contract.manager_user["id"]]

    @property
    def years_employed(self) -> str:
        delta = relativedelta(date.today(), self.contract.employment_start_date)
        return f"{delta.years} år, {delta.months} mån"

    @property
    def days_to_birthday(self) -> int:
        return (self.next_birthday - date.today()).days

    @property
    def next_birthday(self) -> date:
        now = date.today()
        next_birthday = datetime.strptime(self.contract.ssn.split("-")[0], "%Y%m%d").replace(year=now.year).date()
        days_remaining = (next_birthday - now).days
        if days_remaining < 0:
            next_birthday = next_birthday.replace(year=now.year + 1)
        return next_birthday

    @property
    def years_next_birthday(self) -> int:
        return self.next_birthday.year - datetime.strptime(self.contract.ssn.split("-")[0], "%Y%m%d").year

    @property
    def latest_salary_revision(self) -> date:
        return self.contract.monthly_salary_start_date

    @property
    def vacation_entitlement(self) -> List[dict]:
        return self.contract.vacation_entitlements["vacation-entitlements"]

    @property
    def future_vacation_entitlement_change(self) -> Optional[date]:
        """Is there any configured future vacation entitlement change."""
        last = self.vacation_entitlement[-1]
        change_date = date.fromisoformat(last["start-date"])
        if date.today() < change_date:
            return change_date
        return None

    def __str__(self):
        return f"{self.name} ({self.email})"

    @classmethod
    def users_on_manager(cls, sort_key="name"):
        manager_dict = defaultdict(list)
        for user in cls.users_dict.values():
            if user.manager is None:
                continue
            manager_dict[user.manager.name].append(user)
        manager_dict = dict(sorted(manager_dict.items()))
        for k, v in manager_dict.items():
            manager_dict[k] = sorted(v, key=lambda user: getattr(user.contract, sort_key))
        return manager_dict

    @classmethod
    def all_users(cls, sort_key="employment_start_date") -> List[PeUser]:
        """
        Get all users, returns list of `PeUser`.

        Note:
          * We want users to have employment contract, fetch contracts and match to users.
          * After sorting, add an index, its nice to have.
          * Also store a dict on the class, so we can fetch all the users without HTTP roundtrip.
        """
        users_dicts = cls.pe_rest_client().users()
        contracts_dict: dict = cls.pe_rest_client().employment_contracts(as_dict=True)

        users = []
        for user in users_dicts:
            if user["id"] in contracts_dict:
                user["contract"] = contracts_dict[user["id"]]
                u = cls(**user)
                users.append(u)
                logger.debug(f"User created {u.name}")
            else:
                pass
                logger.warning(f"User withough employment contract {user['name']}")

        users = sorted(users, key=lambda user: (getattr(user.contract, sort_key), user.name))
        cls.add_index(users)
        cls.users_dict: dict[int, User] = {user.id: user for user in users}
        return users

    @staticmethod
    def add_index(iterable):
        i = 1
        for item in iterable:
            item.index = i
            i += 1


if __name__ == "__main__":
    import os

    credentials = PeCredentials(company_id=os.getenv("COMPANY"), api_access_token=os.getenv("API"))
    PeUser.pe_credentials = credentials
    for user in PeUser.all_users():
        print(user)
