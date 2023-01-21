
def test_create_submenu(test_app, menu):
    response = test_app.post(
        f"api/v1/menus/{menu}/submenus",
        json={"title": "Test submenu 1", "description": "Test submenu descr 1"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["title"] == "Test submenu 1"
    assert "id" in data


def test_get_submenu(test_app, menu, submenu):
    response = test_app.get(f"/api/v1/menus/{menu}/submenus/{submenu}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Test submenu 1"
    assert data["id"] == str(submenu)


def test_get_submenus(test_app, menu, submenu):
    response = test_app.get(f"/api/v1/menus/{menu}/submenus")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1


def test_update_menu(test_app, menu, submenu):
    response = test_app.patch(f"/api/v1/menus/{menu}/submenus/{submenu}",
                              json={"title": "Updated submenu 1", "description": "Updated submenu descr 1"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Updated submenu 1"
    assert data["id"] == str(submenu)


def test_delete_submenu(test_app, menu, submenu):
    response = test_app.delete(
        f"api/v1/menus/{menu}/submenus/{submenu}"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] is True
    assert data["message"] == 'The submenu has been deleted'
