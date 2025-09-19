#!/usr/bin/env python3
"""
Test cases for client module.
"""

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


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


if __name__ == "__main__":
    unittest.main()