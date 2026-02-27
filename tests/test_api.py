import pytest

@pytest.mark.parametrize("endpoint", [
    "/api/users",
    "/api/admin/users",
    "/api/resources",
    "/api/timeslots",
    "/api/reservations"
])
def test_collection_endpoints_exist(client, endpoint):
    response = client.get(endpoint)
    assert response.status_code != 404