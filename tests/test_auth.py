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