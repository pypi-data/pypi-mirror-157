from sunpal.model import Model
from sunpal import request


class Customer(Model):
    fields = [
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "company",
    ]

    @staticmethod
    def create(params=None, env=None, headers=None):
        return request.send(
            "post", request.uri_path("accounts/register-customer"), params, env, headers
        )

    @staticmethod
    def list(params=None, env=None, headers=None):
        return request.send_list_request(
            "get", request.uri_path("customers/customer/"), params, env, headers
        )

    @staticmethod
    def retrieve(id, env=None, headers=None):
        return request.send(
            "get", request.uri_path("accounts/customer", id), None, env, headers
        )

    @staticmethod
    def update(id, params=None, env=None, headers=None):
        return request.send(
            "post", request.uri_path("customers", id), params, env, headers
        )
