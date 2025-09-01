from django.test import TestCase
from django.shortcuts import reverse

class LandingPageTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse("landing-page"))  # “Go to landing page”
        self.assertEqual(response.status_code, 200)         # “Check if page works (200)”
        self.assertTemplateUsed(response, "landing.html")   # “Check if correct HTML file was used”
