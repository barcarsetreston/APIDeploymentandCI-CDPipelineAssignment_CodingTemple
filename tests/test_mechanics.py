import unittest

from application import create_app
from application.extensions import db


class TestMechanicRoutes(unittest.TestCase):
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

    def _create_mechanic(
        self,
        name="Sam Wrench",
        email="sam@shop.com",
        phone="555-987-6543",
        address="123 Garage Ave",
        salary=55000.00,
    ):
        return self.client.post(
            "/mechanics",
            json={
                "name": name,
                "email": email,
                "phone": phone,
                "address": address,
                "salary": salary,
            },
        )

    # ---- Positive tests ----

    def test_create_mechanic(self):
        response = self._create_mechanic()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["name"], "Sam Wrench")
        self.assertEqual(data["salary"], 55000.00)
        self.assertIn("id", data)

    def test_get_all_mechanics(self):
        self._create_mechanic()
        self._create_mechanic(name="Alex Torque", email="alex@shop.com")
        response = self.client.get("/mechanics")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    def test_get_single_mechanic(self):
        created = self._create_mechanic().get_json()
        response = self.client.get(f"/mechanics/{created['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["email"], "sam@shop.com")

    def test_update_mechanic(self):
        created = self._create_mechanic().get_json()
        response = self.client.put(f"/mechanics/{created['id']}", json={"salary": 60000.00})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["salary"], 60000.00)

    def test_delete_mechanic(self):
        created = self._create_mechanic().get_json()
        response = self.client.delete(f"/mechanics/{created['id']}")
        self.assertEqual(response.status_code, 200)
        follow_up = self.client.get(f"/mechanics/{created['id']}")
        self.assertEqual(follow_up.status_code, 404)

    # ---- Negative tests ----

    def test_create_mechanic_missing_fields(self):
        response = self.client.post("/mechanics", json={"name": "No Email"})
        self.assertEqual(response.status_code, 400)

    def test_create_mechanic_duplicate_email(self):
        self._create_mechanic()
        response = self._create_mechanic(name="Different Name")
        self.assertEqual(response.status_code, 400)

    def test_get_nonexistent_mechanic(self):
        response = self.client.get("/mechanics/9999")
        self.assertEqual(response.status_code, 404)

    def test_update_nonexistent_mechanic(self):
        response = self.client.put("/mechanics/9999", json={"name": "Ghost"})
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_mechanic(self):
        response = self.client.delete("/mechanics/9999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
