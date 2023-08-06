from unittest import TestCase

from rcn.http.client import RCNHttpClient


class TestRCNHttpClient(TestCase):
    def setUp(self) -> None:
        self.rcnHttpClient = RCNHttpClient()

    def doLogin(self):
        response = self.rcnHttpClient.login({
            "username": "admin",
            "password": "admin"
        })
        return response

    def testLogin(self):
        response = self.doLogin()
        responseData = response.json()

        self.assertEqual(response.status_code, 200, 'Not able to login')
        self.assertEqual(responseData['status'], "CREATED", "JWT not created")
        self.assertIsNotNone(responseData['jwt'], "Could not receive JWt token")

    def testGetDevices(self):
        self.doLogin()
        response = self.rcnHttpClient.getDevices()

        self.assertIsInstance(response, list)
        self.assertGreater(response.__len__(), 0)

    def testGetDevice(self):
        self.doLogin()
        devices = self.rcnHttpClient.getDevices()
        for device in devices:
            self.assertIsInstance(device, dict)
            responseDevice = self.rcnHttpClient.getSingleDevice(device['id'])
            self.assertDictEqual(device, responseDevice)

    def testGetConnections(self):
        self.doLogin()
        response = self.rcnHttpClient.getConnections()

        self.assertIsInstance(response, list)
        self.assertGreater(response.__len__(), 0)

    def testGetSupportedDevices(self):
        response = self.rcnHttpClient.getSupportedDevices()

        self.assertIsInstance(response, list, "Response is not list")
        self.assertGreater(response.__len__(), 0)