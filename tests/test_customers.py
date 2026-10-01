import unittest

from application import create_app
from application.extensions import db


class TestCustomerRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_customer(self, name="Jane Doe", email="jane@example.com", phone="555-123-4567"):
        return self.client.post(
            "/customers",
            json={"name": name, "email": email, "phone": phone},
        )

    # ---- Positive tests ----

    def test_create_customer(self):
        response = self._create_customer()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["name"], "Jane Doe")
        self.assertEqual(data["email"], "jane@example.com")
        self.assertIn("id", data)

    def test_get_all_customers(self):
        self._create_customer()
        self._create_customer(name="John Smith", email="john@example.com")
        response = self.client.get("/customers")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    def test_get_single_customer(self):
        created = self._create_customer().get_json()
        response = self.client.get(f"/customers/{created['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["email"], "jane@example.com")

    def test_update_customer(self):
        created = self._create_customer().get_json()
        response = self.client.put(f"/customers/{created['id']}", json={"phone": "555-999-0000"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["phone"], "555-999-0000")

    def test_delete_customer(self):
        created = self._create_customer().get_json()
        response = self.client.delete(f"/customers/{created['id']}")
        self.assertEqual(response.status_code, 200)
        follow_up = self.client.get(f"/customers/{created['id']}")
        self.assertEqual(follow_up.status_code, 404)

    # ---- Negative tests ----

    def test_create_customer_missing_fields(self):
        response = self.client.post("/customers", json={"name": "No Email"})
        self.assertEqual(response.status_code, 400)

    def test_create_customer_duplicate_email(self):
        self._create_customer()
        response = self._create_customer(name="Different Name")
        self.assertEqual(response.status_code, 400)

    def test_update_customer_duplicate_email(self):
        self._create_customer()
        other = self._create_customer(name="Other Person", email="other@example.com").get_json()
        response = self.client.put(f"/customers/{other['id']}", json={"email": "jane@example.com"})
        self.assertEqual(response.status_code, 400)

    def test_get_nonexistent_customer(self):
        response = self.client.get("/customers/9999")
        self.assertEqual(response.status_code, 404)

    def test_update_nonexistent_customer(self):
        response = self.client.put("/customers/9999", json={"name": "Ghost"})
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_customer(self):
        response = self.client.delete("/customers/9999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
