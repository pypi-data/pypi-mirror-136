import seldom
from seldom import data


class TestRequest(seldom.TestCase):
    """
    http api test demo
    doc: https://requests.readthedocs.io/en/master/
    """

    def test_put_method_11(self):
        """
        test put request
        """
        self.put('/put', data={'key': 'value'})
        self.assertStatusCode(200)

    # def test_post_method_22(self):
    #     """
    #     test post request
    #     """
    #     self.post('/post', data={'key':'value'})
    #     self.assertStatusCode(200)
    #
    # def test_get_method_33(self):
    #     """
    #     test get request
    #     """
    #     payload = {'key1': 'value1', 'key2': 'value2'}
    #     self.get("/get", params=payload)
    #     self.assertStatusCode(200)
    #
    # def test_delete_method_44(self):
    #     """
    #     test delete request
    #     """
    #     self.delete('/delete')
    #     self.assertStatusCode(200)


if __name__ == '__main__':
    seldom.main(base_url="http://httpbin.org", debug=True)
