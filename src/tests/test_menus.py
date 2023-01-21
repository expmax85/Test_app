
def test_create_menu(test_app):
    response = test_app.post(
        "api/v1/menus",
        json={"title": "Test menu 1", "description": "Test menu descr 1"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["title"] == "Test menu 1"
    assert "id" in data


def test_get_menu(test_app, menu):
    response = test_app.get(f"/api/v1/menus/{menu}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Test menu 1"
    assert data["id"] == str(menu)


def test_get_menus(test_app, menu):
    response = test_app.get("/api/v1/menus")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1


def test_update_menu(test_app, menu):
    response = test_app.patch(f"/api/v1/menus/{menu}",
                              json={"title": "Updated menu 1", "description": "Updated menu descr 1"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Updated menu 1"
    assert data["id"] == str(menu)


def test_delete_menu(test_app, menu):
    response = test_app.delete(f"/api/v1/menus/{menu}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] is True
    assert data["message"] == 'The menu has been deleted'
