from typing import Dict, List

import requests
from loguru import logger

API_URL = "https://my.accounting.pe/api/v1/company/{company_id}/"


class PeRestClient:
    """
    PE accounting REST client Python binding.
    <https://api-doc.accounting.pe>
    """

    def __init__(self, *, api_access_token: str, company_id: str):
        """[summary]

        Args:
            api_access_token (str): API access token received by PE Accounting.
        """
        logger.debug("Init RestClient")
        PeRestClient.headers: dict = {
            "X-Token": api_access_token,
            "User-Agent": "SDNit Python Automation",
            "Content-type": "application/json",
        }
        PeRestClient.url = API_URL.format(company_id=company_id)

    def company(self) -> dict:
        return self.http_request(verb="GET", path="info")

    def user_by_id(self, user_id: int):
        """Get user by PE id"""
        return self.http_request(verb="GET", path=f"user/{user_id}")

    def users(
        self, include_inactive: bool = False, as_dict: bool = False
    ) -> List[dict]:
        all_users = self.http_request(verb="GET", path=f"user")["users"]
        if include_inactive:
            return all_users
        return [user for user in all_users if user["active"]]

    def users_dict(self, include_inactive: bool = False) -> Dict[int, dict]:
        all_users = self.http_request(verb="GET", path=f"user")["users"]
        if include_inactive:
            return {user["email"]: user for user in all_users}
        return {user["email"]: user for user in all_users if user["active"]}

    def employment_contracts(self, *, as_dict: bool = False):
        all_contracts = self.http_request(verb="GET", path=f"payroll/user")[
            "payroll-user-readables"
        ]
        if as_dict:
            return {contract["user"]["id"]: contract for contract in all_contracts}
        return all_contracts

    @classmethod
    def http_request(cls, *, verb: str, path: str) -> dict:
        """Helper to do http requests.

        Args:
            verb (str): http verb
            path (str): url suffix, will be prepended to the base API url for this RestClient.
        """
        logger.debug(f"{verb} - {path}")
        url = cls.url + path
        return requests.request(verb, url, headers=cls.headers).json()
