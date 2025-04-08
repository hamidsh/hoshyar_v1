class Auth:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key نمی‌تواند خالی باشد")
        self.api_key = api_key

    def get_headers(self) -> dict:
        return {"X-API-Key": self.api_key}