import requests
from .response import APIResponse

class TwitterAPIRequests:
    def __init__(self, auth):
        self.auth = auth
        self.session = requests.Session()
        self.session.headers.update(self.auth.get_headers())
        self.timeout = 10
        self.BASE_URL = "https://api.twitterapi.io/"

    def request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> APIResponse:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return APIResponse.from_response(response.json(), endpoint)
        except requests.exceptions.RequestException as e:
            error_msg = f"خطا در درخواست {method} به {endpoint}: {str(e)}"
            if hasattr(e.response, "text"):
                error_msg += f" - پاسخ: {e.response.text}"
            raise Exception(error_msg) from e

    def get(self, endpoint: str, params: dict = None) -> APIResponse:
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: dict = None) -> APIResponse:
        return self.request("POST", endpoint, data=data)

    def delete(self, endpoint: str, data: dict = None) -> APIResponse:
        return self.request("DELETE", endpoint, data=data)

    def fetch_paginated(self, endpoint: str, params: dict, max_items: int, key: str = "items"):
        all_items = []
        while len(all_items) < max_items:
            response = self.get(endpoint, params)
            items = response.get_data()
            if not items:
                break
            remaining = max_items - len(all_items)
            all_items.extend(items[:remaining])
            if not response.has_next_page():
                break
            params["cursor"] = response.next_page
        return all_items

    def __del__(self):
        self.session.close()