def test_delete_without_token_returns_401(client):
    response = client.delete("/products/1")
    assert response.status_code == 401

def test_delete_with_staff_token_returns_403(client, staff_token):
    response = client.delete(
        "/products/1",
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert response.status_code == 403

def test_delete_with_admin_token_succeeds(client, admin_token):
    response = client.delete(
        "/products/1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code in (200, 404)

def test_create_product_no_token_fails(client):
    response = client.post('/products', json={
        "name": "Widget", "sku": "W-TEST-1", "quantity": 10, "price": 50
    })
    assert response.status_code == 401


def test_create_product_with_token_succeeds(client, staff_token):
    response = client.post('/products',
        json={"name": "Widget", "sku": "W-TEST-1", "quantity": 10, "price": 50},
        headers={"Authorization": f"Bearer {staff_token}"})
    assert response.status_code in (201, 409)  # 409 if SKU exists from a prior run


def test_update_product_no_token_fails(client):
    response = client.put('/products/2', json={"quantity": 99})
    assert response.status_code == 401


def test_register_new_user_succeeds(client):
    response = client.post('/register', json={
        "username": "pytest_user1", "password": "pytestpass123"
    })
    assert response.status_code in (201, 409)  # 409 if already exists from a prior run
    

def test_register_duplicate_username_fails(client):
    client.post('/register', json={"username": "pytest_dup", "password": "pass123"})
    response = client.post('/register', json={"username": "pytest_dup", "password": "pass456"})
    assert response.status_code == 409
