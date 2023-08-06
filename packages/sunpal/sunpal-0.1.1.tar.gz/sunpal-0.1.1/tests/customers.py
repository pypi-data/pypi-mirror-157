import sunpal
import unittest

api_key = "test_f8b0be52de3b4e3887dda051f2e3280a"
site = "sunwise"
sunpal.configure(api_key, site)


class CustomersTestCase(unittest.TestCase):
    def test_create_customer(self):
        import random

        rfc = "".join(random.choice("0123456789ABCDEF") for i in range(13))
        item = sunpal.Customer.create(
            {
                "first_name": "Jason",
                "last_name": "Bates",
                "rfc": rfc,
                "email": "examplesw@yopmail.com",
            }
        )
        self.assertTrue(item, True)

    def test_get_customer(self):
        # Customers
        item = sunpal.Customer.retrieve("GACA910614A36")
        self.assertTrue(item, True)


if __name__ == "__main__":
    unittest.main()
