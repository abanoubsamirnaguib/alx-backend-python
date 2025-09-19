#!/usr/bin/env python3
"""
Test cases for client module.
"""

import unittest
from unittest.mock import patch
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value."""
        # Setup expected return value
        expected_result = {"login": org_name, "id": 12345}
        mock_get_json.return_value = expected_result

        # Create client instance
        client = GithubOrgClient(org_name)

        # Call the org method
        result = client.org

        # Assert get_json was called once with expected URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

        # Assert correct result is returned
        self.assertEqual(result, expected_result)

    def test_public_repos_url(self):
        """Test that GithubOrgClient._public_repos_url returns the correct URL."""
        # Define known payload with repos_url
        known_payload = {
            "repos_url": "https://api.github.com/orgs/test/repos",
            "login": "test",
            "id": 12345
        }

        # Use patch as context manager to mock the org property
        with patch.object(GithubOrgClient, 'org',
                          new_callable=lambda: property(
                              lambda self: known_payload)):
            client = GithubOrgClient("test")

            # Access _public_repos_url property
            result = client._public_repos_url

            # Assert the result matches the repos_url from the mocked payload
            self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that GithubOrgClient.public_repos returns the correct list of repos."""
        # Define test payload with repo data
        test_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None}
        ]
        mock_get_json.return_value = test_payload

        # Mock _public_repos_url property
        with patch.object(GithubOrgClient, '_public_repos_url',
                          new_callable=lambda: property(
                              lambda self: "https://api.github.com/orgs/test/repos")):
            client = GithubOrgClient("test")

            # Call public_repos method
            result = client.public_repos()

            # Expected list of repo names
            expected_repos = ["repo1", "repo2", "repo3"]

            # Assert correct list of repos is returned
            self.assertEqual(result, expected_repos)

            # Assert get_json was called once
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that GithubOrgClient.has_license returns the expected result."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3]
    }
])

class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Set up class method to start patcher."""
        def side_effect(url):
            """Side effect function for mocked requests.get."""
            class MockResponse:
                def __init__(self, json_data):
                    self.json_data = json_data

                def json(self):
                    return self.json_data

            if url == "https://api.github.com/orgs/google":
                return MockResponse(cls.org_payload)
            elif url == cls.org_payload["repos_url"]:
                return MockResponse(cls.repos_payload)
            return MockResponse({})

        cls.get_patcher = patch('requests.get', side_effect=side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down class method to stop patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos method in integration test."""
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos method with license filter."""
        client = GithubOrgClient("google")
        result = client.public_repos("apache-2.0")
        self.assertEqual(result, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
