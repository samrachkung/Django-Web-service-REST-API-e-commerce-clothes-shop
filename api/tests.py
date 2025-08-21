from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User


class APIRootTestCase(APITestCase):
    def test_api_root_accessible(self):
        """Test that API root is accessible"""
        url = reverse('api:api-root')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('endpoints', response.data)
    
    def test_health_check(self):
        """Test health check endpoint"""
        url = reverse('api:health-check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')


class SearchTestCase(APITestCase):
    def test_search_requires_query(self):
        """Test that search requires a query parameter"""
        url = reverse('api:search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_with_query(self):
        """Test search with valid query"""
        url = reverse('api:search')
        response = self.client.get(url, {'q': 'shirt'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)