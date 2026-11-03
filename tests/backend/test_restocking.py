"""
Tests for restock order API endpoints.
"""
from datetime import datetime, timedelta

import pytest

import mock_data


@pytest.fixture(autouse=True)
def clear_restock_orders():
    """Restock orders live in a module-level list; reset it so tests stay independent."""
    mock_data.restock_orders.clear()
    yield
    mock_data.restock_orders.clear()


def forecast_for(client, sku):
    """Look up the server's forecast record for a SKU."""
    forecasts = client.get("/api/demand").json()
    return next(f for f in forecasts if f["item_sku"] == sku)


class TestRestockOrderEndpoints:
    """Test suite for restock order endpoints."""

    def test_get_restock_orders_empty(self, client):
        """Test that no restock orders exist before any are submitted."""
        response = client.get("/api/restock-orders")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_restock_order(self, client):
        """Test submitting a valid restock order."""
        response = client.post("/api/restock-orders", json={
            "budget": 5000,
            "items": [{"item_sku": "WDG-001", "quantity": 10}],
        })
        assert response.status_code == 201

        order = response.json()
        for field in ["id", "order_number", "items", "total_cost", "budget",
                      "lead_time_days", "status", "submitted_date", "expected_delivery"]:
            assert field in order

        assert order["order_number"] == "RST-0001"
        assert order["status"] == "Submitted"
        assert order["budget"] == 5000

        item = order["items"][0]
        assert item["item_sku"] == "WDG-001"
        assert item["item_name"] == "Industrial Widget Type A"
        assert item["quantity"] == 10

    def test_restock_order_uses_server_pricing(self, client):
        """Test that a unit_cost sent by the client is ignored."""
        forecast = forecast_for(client, "WDG-001")

        response = client.post("/api/restock-orders", json={
            "budget": 5000,
            "items": [{"item_sku": "WDG-001", "quantity": 10, "unit_cost": 0.01}],
        })
        assert response.status_code == 201

        order = response.json()
        assert order["items"][0]["unit_cost"] == forecast["unit_cost"]
        assert abs(order["total_cost"] - 10 * forecast["unit_cost"]) < 0.01

    def test_restock_order_total_cost_calculation(self, client):
        """Test that line totals and the order total add up."""
        response = client.post("/api/restock-orders", json={
            "budget": 10000,
            "items": [
                {"item_sku": "WDG-001", "quantity": 5},
                {"item_sku": "GSK-203", "quantity": 40},
            ],
        })
        assert response.status_code == 201

        order = response.json()
        for item in order["items"]:
            assert abs(item["line_total"] - item["quantity"] * item["unit_cost"]) < 0.01
        assert abs(order["total_cost"] - sum(i["line_total"] for i in order["items"])) < 0.01

    def test_restock_order_lead_time_calculation(self, client):
        """Test that lead time is the slowest item and sets the expected delivery."""
        slow = forecast_for(client, "MTR-304")
        fast = forecast_for(client, "GSK-203")
        assert slow["lead_time_days"] > fast["lead_time_days"]

        response = client.post("/api/restock-orders", json={
            "budget": 10000,
            "items": [
                {"item_sku": "GSK-203", "quantity": 1},
                {"item_sku": "MTR-304", "quantity": 1},
            ],
        })
        assert response.status_code == 201

        order = response.json()
        assert order["lead_time_days"] == slow["lead_time_days"]

        submitted = datetime.fromisoformat(order["submitted_date"])
        expected = datetime.fromisoformat(order["expected_delivery"])
        assert expected - submitted == timedelta(days=slow["lead_time_days"])

    def test_restock_order_exactly_at_budget(self, client):
        """Test that a total equal to the budget is accepted (4 x $3.25 = $13.00)."""
        response = client.post("/api/restock-orders", json={
            "budget": 13.00,
            "items": [{"item_sku": "GSK-203", "quantity": 4}],
        })
        assert response.status_code == 201
        assert response.json()["total_cost"] == 13.00

    def test_restock_order_one_cent_over_budget(self, client):
        """Test that a total one cent over the budget is rejected."""
        response = client.post("/api/restock-orders", json={
            "budget": 12.99,
            "items": [{"item_sku": "GSK-203", "quantity": 4}],
        })
        assert response.status_code == 400

    def test_restock_order_multi_line_cents(self, client):
        """Test exact cent totals across lines (3 x $18.99 + 7 x $3.25 = $79.72)."""
        response = client.post("/api/restock-orders", json={
            "budget": 79.72,
            "items": [
                {"item_sku": "PSU-501", "quantity": 3},
                {"item_sku": "GSK-203", "quantity": 7},
            ],
        })
        assert response.status_code == 201

        order = response.json()
        assert [i["line_total"] for i in order["items"]] == [56.97, 22.75]
        assert order["total_cost"] == 79.72

    def test_restock_order_over_budget(self, client):
        """Test that an order costing more than the budget is rejected."""
        response = client.post("/api/restock-orders", json={
            "budget": 10,
            "items": [{"item_sku": "WDG-001", "quantity": 1}],
        })
        assert response.status_code == 400
        assert "exceeds budget" in response.json()["detail"]
        assert client.get("/api/restock-orders").json() == []

    def test_restock_order_unknown_sku(self, client):
        """Test that a SKU without a demand forecast is rejected."""
        response = client.post("/api/restock-orders", json={
            "budget": 1000,
            "items": [{"item_sku": "NOPE-999", "quantity": 1}],
        })
        assert response.status_code == 400
        assert "NOPE-999" in response.json()["detail"]

    def test_restock_order_duplicate_sku(self, client):
        """Test that the same SKU twice in one order is rejected."""
        response = client.post("/api/restock-orders", json={
            "budget": 1000,
            "items": [
                {"item_sku": "GSK-203", "quantity": 1},
                {"item_sku": "GSK-203", "quantity": 2},
            ],
        })
        assert response.status_code == 400
        assert "duplicate" in response.json()["detail"].lower()

    def test_restock_order_empty_items(self, client):
        """Test that an order with no items fails validation."""
        response = client.post("/api/restock-orders", json={"budget": 1000, "items": []})
        assert response.status_code == 422

    def test_restock_order_zero_quantity(self, client):
        """Test that a zero quantity fails validation."""
        response = client.post("/api/restock-orders", json={
            "budget": 1000,
            "items": [{"item_sku": "GSK-203", "quantity": 0}],
        })
        assert response.status_code == 422

    def test_restock_order_negative_budget(self, client):
        """Test that a negative budget fails validation."""
        response = client.post("/api/restock-orders", json={
            "budget": -1,
            "items": [{"item_sku": "GSK-203", "quantity": 1}],
        })
        assert response.status_code == 422

    def test_get_restock_orders_newest_first(self, client):
        """Test that submitted orders are listed newest first."""
        for _ in range(2):
            response = client.post("/api/restock-orders", json={
                "budget": 1000,
                "items": [{"item_sku": "GSK-203", "quantity": 1}],
            })
            assert response.status_code == 201

        data = client.get("/api/restock-orders").json()
        assert [o["order_number"] for o in data] == ["RST-0002", "RST-0001"]
