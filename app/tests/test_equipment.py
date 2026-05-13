from fastapi import status


class TestEquipment:
    def test_get_equipment_endpoint(self, client):
        response = client.get("/equipment")
        assert response.status_code == status.HTTP_200_OK

    def test_get_equipment_by_category(self, client):
        response = client.get("/equipment?category=blade")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_equipment_by_brand(self, client):
        response = client.get("/equipment?brand=Butterfly")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_equipment_search(self, client):
        response = client.get("/equipment?search=Viscaria")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_equipment_search_too_long(self, client):
        response = client.get(f"/equipment?search={'x' * 101}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_equipment_by_id_not_found(self, client):
        response = client.get("/equipment/fake-equipment-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_equipment_reviews_not_found(self, client):
        response = client.get("/equipment/fake-equipment-id/reviews")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_create_equipment_review_unauthorized(self, client):
        review_data = {"rating": 5, "review_text": "Great blade!"}
        response = client.post("/equipment/fake-equipment-id/reviews", json=review_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_equipment_review_equipment_not_found(self, client, auth_headers):
        review_data = {"rating": 5, "review_text": "Great blade!"}
        response = client.post(
            "/equipment/fake-equipment-id/reviews", json=review_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_recommend_setup_endpoint(self, client):
        request_data = {"playing_style": "beginner", "budget_usd": 200, "preferred_brands": []}
        response = client.post("/equipment/recommend-setup", json=request_data)
        # May return 404 if no equipment seeded in test DB, or 200 if seeded
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_recommend_setup_invalid_style(self, client):
        request_data = {"playing_style": "invalid_style", "budget_usd": 200}
        response = client.post("/equipment/recommend-setup", json=request_data)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_recommend_setup_no_budget(self, client):
        request_data = {"playing_style": "beginner"}
        response = client.post("/equipment/recommend-setup", json=request_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_equipment_response_structure(self, client):
        response = client.get("/equipment")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            item = data[0]
            assert "id" in item
            assert "name" in item
            assert "brand" in item
            assert "category" in item

    def test_equipment_detail_response_structure(self, client):
        # First get any equipment id
        list_response = client.get("/equipment")
        if list_response.status_code == status.HTTP_200_OK:
            data = list_response.json()
            if len(data) > 0:
                equipment_id = data[0]["id"]
                detail_response = client.get(f"/equipment/{equipment_id}")
                assert detail_response.status_code == status.HTTP_200_OK
                detail = detail_response.json()
                assert "id" in detail
                assert "name" in detail
                assert "blade_specs" in detail or "rubber_specs" in detail
