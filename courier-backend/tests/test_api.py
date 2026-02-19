import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal

from shared.models import Courier, Delivery
from core.config import settings

API_PREFIX = settings.API_PREFIX

class TestCourierSchemas:
    """Тесты для схем Pydantic из api.schemas.py"""

    def test_courier_response_schema(self):
        """Тест схемы CourierResponse"""
        from api.schemas import CourierResponse

        data = {
            "id": 1,
            "name": "Test Courier",
            "status": "available",
            "current_order_id": None,
            "photo_url": "http://example.com/photo.jpg"
        }

        courier = CourierResponse(**data)
        assert courier.id == 1
        assert courier.name == "Test Courier"
        assert courier.status == "available"
        assert courier.current_order_id is None
        assert courier.photo_url == "http://example.com/photo.jpg"

    def test_delivery_response_schema(self):
        """Тест схемы DeliveryResponse"""
        from api.schemas import DeliveryResponse

        data = {
            "id": 1,
            "order_id": 123,
            "status": "assigned",
            "assigned_at": "2024-01-01T12:00:00",
            "picked_up_at": None,
            "delivered_at": None
        }

        delivery = DeliveryResponse(**data)
        assert delivery.id == 1
        assert delivery.order_id == 123
        assert delivery.status == "assigned"
        assert delivery.assigned_at == "2024-01-01T12:00:00"
        assert delivery.picked_up_at is None
        assert delivery.delivered_at is None

    def test_assign_delivery_request_schema(self):
        """Тест схемы AssignDeliveryRequest"""
        from api.schemas import AssignDeliveryRequest

        data = {
            "courier_id": 1,
            "order_id": 123
        }

        request = AssignDeliveryRequest(**data)
        assert request.courier_id == 1
        assert request.order_id == 123

    def test_update_courier_status_request_schema(self):
        """Тест схемы UpdateCourierStatusRequest"""
        from api.schemas import UpdateCourierStatusRequest

        data = {"status": "online"}
        request = UpdateCourierStatusRequest(**data)
        assert request.status == "online"


class TestCourierAPI:
    """Тесты для API endpoints из api.schemas.py"""

    def test_get_courier_success(self, client: TestClient, db_session: Session, test_courier):
        """Тест успешного получения курьера"""
        print(f"{API_PREFIX}/couriers/{test_courier.id}")
        response = client.get(f"{API_PREFIX}/couriers/{test_courier.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == test_courier.id
        assert data["name"] == "Test Courier"
        assert data["status"] == "available"
        assert data["photo_url"] == "http://example.com/photo.jpg"

    def test_get_courier_not_found(self, client: TestClient, db_session: Session):
        """Тест получения несуществующего курьера"""
        response = client.get(f"{API_PREFIX}/couriers/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Courier not found"

    def test_update_courier_status_success(self, client: TestClient, db_session: Session, test_courier):
        """Тест успешного обновления статуса курьера"""
        update_data = {"status": "online"}

        response = client.put(
            f"{API_PREFIX}/couriers/{test_courier.id}/status",
            json=update_data
        )

        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Проверяем, что в базе обновилось
        db_session.refresh(test_courier)
        assert test_courier.status == "online"

    def test_update_courier_status_invalid_status(self, client: TestClient, db_session: Session, test_courier):
        """Тест обновления статуса с недопустимым значением"""
        update_data = {"status": "invalid_status"}

        response = client.put(
            f"{API_PREFIX}/couriers/{test_courier.id}/status",
            json=update_data
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid status"

    def test_update_courier_status_not_found(self, client: TestClient, db_session: Session):
        """Тест обновления статуса несуществующего курьера"""
        update_data = {"status": "online"}

        response = client.put(
            f"{API_PREFIX}/couriers/999999/status",
            json=update_data
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Courier not found"

    def test_get_available_orders_empty(self, client: TestClient, db_session: Session):
        """Тест получения пустого списка доступных заказов"""
        # Очищаем таблицы перед тестом
        db_session.execute(text("DELETE FROM deliveries"))
        db_session.execute(text("DELETE FROM orders"))
        db_session.commit()

        response = client.get(f"{API_PREFIX}/orders/available-orders/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_available_orders_with_data(self, client: TestClient, db_session: Session):
        """Тест получения списка доступных заказов"""
        # Очищаем таблицы перед тестом
        db_session.execute(text("DELETE FROM deliveries"))
        db_session.execute(text("DELETE FROM orders"))
        db_session.commit()

        # Создаем тестовые заказы
        from conftest import Order

        order1 = Order(
            user_id=1,
            total_price=Decimal("100.50"),
            status="pending"
        )
        order2 = Order(
            user_id=2,
            total_price=Decimal("200.00"),
            status="pending"
        )

        db_session.add_all([order1, order2])
        db_session.commit()

        response = client.get(f"{API_PREFIX}/orders/available-orders/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2

        # Проверяем структуру ответа
        for order in data:
            assert "id" in order
            assert "user_id" in order
            assert "total_price" in order
            assert "status" in order

    def test_assign_delivery_success(self, client: TestClient, db_session: Session, test_courier):
        """Тест успешного назначения доставки"""
        # Создаем тестовый заказ
        from conftest import Order

        order = Order(
            user_id=1,
            total_price=Decimal("100.50"),
            status="pending"
        )
        db_session.add(order)
        db_session.commit()

        # Назначаем доставку
        assign_data = {
            "courier_id": test_courier.id,
            "order_id": order.id
        }

        response = client.post(f"{API_PREFIX}/deliveries/assign-delivery/", json=assign_data)
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Проверяем, что доставка создана
        delivery = db_session.query(Delivery).filter(
            Delivery.order_id == order.id
        ).first()

        assert delivery is not None
        assert delivery.courier_id == test_courier.id
        assert delivery.status == "assigned"

        # Проверяем, что статус курьера обновился
        db_session.refresh(test_courier)
        assert test_courier.status == "going_to_pickup"
        assert test_courier.current_order_id == order.id

    def test_assign_delivery_courier_not_available(self, client: TestClient, db_session: Session, test_courier):
        """Тест назначения доставки недоступному курьеру"""
        # Устанавливаем курьеру статус offline
        test_courier.status = "off_line"
        db_session.commit()

        # Создаем тестовый заказ
        from conftest import Order

        order = Order(
            user_id=1,
            total_price=Decimal("100.50"),
            status="pending"
        )
        db_session.add(order)
        db_session.commit()

        assign_data = {
            "courier_id": test_courier.id,
            "order_id": order.id
        }

        response = client.post(f"{API_PREFIX}/deliveries/assign-delivery/", json=assign_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Courier is not available"

    def test_assign_delivery_order_already_assigned(self, client: TestClient, db_session: Session, test_courier, test_delivery):
        """Тест назначения уже назначенного заказа"""
        assign_data = {
            "courier_id": test_courier.id,
            "order_id": test_delivery.order_id
        }

        response = client.post(f"{API_PREFIX}/deliveries/assign-delivery/", json=assign_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Order is already assigned"

    def test_update_delivery_status_success(self, client: TestClient, db_session: Session, test_delivery):
        """Тест успешного обновления статуса доставки"""
        response = client.post(f"{API_PREFIX}/deliveries/update-delivery-status/{test_delivery.id}?status=picked_up")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

        # Проверяем, что статус обновился
        db_session.refresh(test_delivery)
        assert test_delivery.status == "picked_up"
        assert test_delivery.picked_up_at is not None

        # Проверяем, что статус заказа обновился
        from conftest import Order
        order = db_session.query(Order).filter(Order.id == test_delivery.order_id).first()
        assert order.status == "picked_up"

        # Проверяем статус курьера
        courier = db_session.query(Courier).filter(Courier.id == test_delivery.courier_id).first()
        assert courier.status == "delivering"

    def test_update_delivery_status_to_delivered(self, client: TestClient, db_session: Session, test_delivery):
        """Тест обновления статуса доставки на delivered"""
        # Сначала обновляем на picked_up
        test_delivery.status = "picked_up"
        db_session.commit()

        response = client.post(f"{API_PREFIX}/deliveries/update-delivery-status/{test_delivery.id}?status=delivered")
        assert response.status_code == 200

        # Проверяем обновления
        db_session.refresh(test_delivery)
        assert test_delivery.status == "delivered"
        assert test_delivery.delivered_at is not None

        # Проверяем, что статус курьера сбросился
        courier = db_session.query(Courier).filter(Courier.id == test_delivery.courier_id).first()
        assert courier.status == "available"
        assert courier.current_order_id is None

    def test_update_delivery_status_not_found(self, client: TestClient, db_session: Session):
        """Тест обновления статуса несуществующей доставки"""
        response = client.post(f"{API_PREFIX}/deliveries/update-delivery-status/999999?status=picked_up")
        assert response.status_code == 404
        assert response.json()["detail"] == "Delivery not found"

    def test_get_my_deliveries_active(self, client: TestClient, db_session: Session, test_courier, test_delivery):
        """Тест получения активных доставок курьера"""
        response = client.get(f"{API_PREFIX}/deliveries/my-deliveries/{test_courier.id}")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_delivery.id
        assert data[0]["order_id"] == test_delivery.order_id
        assert data[0]["status"] == "assigned"

    def test_get_my_deliveries_with_history(self, client: TestClient, db_session: Session, test_courier, test_delivery):
        """Тест получения истории доставок курьера"""
        # Меняем статус доставки на delivered
        test_delivery.status = "delivered"
        db_session.commit()

        response = client.get(f"{API_PREFIX}/deliveries/my-deliveries/{test_courier.id}?history=true")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1  # Все равно должна показываться

        # Без history параметра доставка не должна показываться
        response2 = client.get(f"{API_PREFIX}/deliveries/my-deliveries/{test_courier.id}")
        data2 = response2.json()
        assert len(data2) == 0

    def test_get_my_deliveries_empty(self, client: TestClient, db_session: Session, test_courier):
        """Тест получения доставок для курьера без доставок"""
        response = client.get(f"{API_PREFIX}/deliveries/my-deliveries/{test_courier.id}")
        assert response.status_code == 200
        assert response.json() == []# courier-backend/tests/test_courier_api.py
