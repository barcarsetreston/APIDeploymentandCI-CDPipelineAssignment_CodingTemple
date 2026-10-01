import unittest

from application import create_app
from application.extensions import db


class TestServiceTicketRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        customer_resp = self.client.post(
            "/customers",
            json={"name": "Jane Doe", "email": "jane@example.com", "phone": "555-123-4567"},
        )
        self.customer_id = customer_resp.get_json()["id"]

        mechanic_resp = self.client.post(
            "/mechanics",
            json={
                "name": "Sam Wrench",
                "email": "sam@shop.com",
                "phone": "555-987-6543",
                "address": "123 Garage Ave",
                "salary": 55000.00,
            },
        )
        self.mechanic_id = mechanic_resp.get_json()["id"]

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_ticket(self, **overrides):
        payload = {
            "VIN": "1HGCM82633A004352",
            "service_date": "2026-09-16",
            "service_desc": "Oil change and tire rotation",
            "customer_id": self.customer_id,
        }
        payload.update(overrides)
        return self.client.post("/service-tickets", json=payload)

    # ---- Positive tests ----

    def test_create_service_ticket(self):
        response = self._create_ticket()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["VIN"], "1HGCM82633A004352")
        self.assertEqual(data["customer"]["id"], self.customer_id)
        self.assertEqual(data["mechanics"], [])

    def test_create_service_ticket_with_mechanics(self):
        response = self._create_ticket(mechanic_ids=[self.mechanic_id])
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(len(data["mechanics"]), 1)
        self.assertEqual(data["mechanics"][0]["id"], self.mechanic_id)

    def test_get_all_service_tickets(self):
        self._create_ticket()
        response = self.client.get("/service-tickets")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_get_single_service_ticket(self):
        created = self._create_ticket().get_json()
        response = self.client.get(f"/service-tickets/{created['id']}")
        self.assertEqual(response.status_code, 200)

    def test_update_service_ticket(self):
        created = self._create_ticket().get_json()
        response = self.client.put(
            f"/service-tickets/{created['id']}", json={"service_desc": "Brake replacement"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["service_desc"], "Brake replacement")

    def test_delete_service_ticket(self):
        created = self._create_ticket().get_json()
        response = self.client.delete(f"/service-tickets/{created['id']}")
        self.assertEqual(response.status_code, 200)
        follow_up = self.client.get(f"/service-tickets/{created['id']}")
        self.assertEqual(follow_up.status_code, 404)

    def test_assign_mechanic_to_ticket(self):
        created = self._create_ticket().get_json()
        response = self.client.put(
            f"/service-tickets/{created['id']}/assign-mechanic/{self.mechanic_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["mechanics"]), 1)

    def test_remove_mechanic_from_ticket(self):
        created = self._create_ticket(mechanic_ids=[self.mechanic_id]).get_json()
        response = self.client.put(
            f"/service-tickets/{created['id']}/remove-mechanic/{self.mechanic_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["mechanics"]), 0)

    # ---- Negative tests ----

    def test_create_service_ticket_missing_fields(self):
        response = self.client.post("/service-tickets", json={"VIN": "12345"})
        self.assertEqual(response.status_code, 400)

    def test_create_service_ticket_invalid_customer(self):
        response = self._create_ticket(customer_id=9999)
        self.assertEqual(response.status_code, 404)

    def test_create_service_ticket_invalid_mechanic(self):
        response = self._create_ticket(mechanic_ids=[9999])
        self.assertEqual(response.status_code, 404)

    def test_get_nonexistent_service_ticket(self):
        response = self.client.get("/service-tickets/9999")
        self.assertEqual(response.status_code, 404)

    def test_update_nonexistent_service_ticket(self):
        response = self.client.put("/service-tickets/9999", json={"service_desc": "Ghost"})
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_service_ticket(self):
        response = self.client.delete("/service-tickets/9999")
        self.assertEqual(response.status_code, 404)

    def test_assign_mechanic_already_assigned(self):
        created = self._create_ticket(mechanic_ids=[self.mechanic_id]).get_json()
        response = self.client.put(
            f"/service-tickets/{created['id']}/assign-mechanic/{self.mechanic_id}"
        )
        self.assertEqual(response.status_code, 400)

    def test_assign_nonexistent_mechanic(self):
        created = self._create_ticket().get_json()
        response = self.client.put(f"/service-tickets/{created['id']}/assign-mechanic/9999")
        self.assertEqual(response.status_code, 404)

    def test_remove_mechanic_not_assigned(self):
        created = self._create_ticket().get_json()
        response = self.client.put(
            f"/service-tickets/{created['id']}/remove-mechanic/{self.mechanic_id}"
        )
        self.assertEqual(response.status_code, 400)

    def test_assign_mechanic_nonexistent_ticket(self):
        response = self.client.put(f"/service-tickets/9999/assign-mechanic/{self.mechanic_id}")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
