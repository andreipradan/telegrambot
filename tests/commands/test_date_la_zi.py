def test_histogram(test_client):
    response = test_client.get('/')
    assert response.status_code == 2001
