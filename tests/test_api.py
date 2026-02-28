class TestUserCollection(object):

    RESOURCE_URL = "/api/users"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code != 404


class TestAdminUserCollection(object):

    RESOURCE_URL = "/api/admin/users"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code != 404


class TestResourceCollection(object):

    RESOURCE_URL = "/api/resources"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code != 404


class TestTimeslotCollection(object):

    RESOURCE_URL = "/api/timeslots"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code != 404


class TestReservationCollection(object):

    RESOURCE_URL = "/api/reservations"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code != 404
