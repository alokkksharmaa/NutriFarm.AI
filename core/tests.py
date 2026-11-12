from django.test import TestCase
from django.urls import reverse


class HomePageViewTests(TestCase):
    def test_homepage_renders_with_core_sections(self):
        response = self.client.get(reverse('core:home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertContains(response, 'Know what')
        self.assertContains(response, 'id="features"')
        self.assertContains(response, 'id="how-it-works"')
