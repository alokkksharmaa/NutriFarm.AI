from django.test import TestCase, override_settings
from django.urls import reverse


class PageViewTests(TestCase):
    def test_existing_homepage_still_loads(self):
        response = self.client.get(reverse('core:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Know what')

    def test_about_features_and_contact_pages_load(self):
        pages = (
            ('testing:about', 'ABOUT NUTRIFARM AI'),
            ('testing:features', 'PLATFORM FEATURES'),
            ('testing:contact', 'CONTACT US'),
        )

        for url_name, expected_text in pages:
            with self.subTest(page=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_text)

        contact_response = self.client.get(reverse('testing:contact'))
        self.assertContains(contact_response, 'csrfmiddlewaretoken')

    def test_contact_post_is_not_implemented_yet(self):
        response = self.client.post(reverse('testing:contact'), {'name': 'Farmer'})

        self.assertEqual(response.status_code, 501)
        self.assertContains(response, 'not implemented yet', status_code=501)

    def test_sample_id_is_displayed_from_url(self):
        response = self.client.get(reverse('testing:sample_detail', args=[101]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sample 101')

    def test_zero_sample_id_returns_404(self):
        response = self.client.get('/sample/0/')

        self.assertEqual(response.status_code, 404)

    def test_non_numeric_sample_id_returns_404(self):
        response = self.client.get('/sample/not-a-number/')

        self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG=False)
    def test_unknown_page_returns_friendly_404(self):
        response = self.client.get('/not-a-page/', HTTP_HOST='localhost')

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'We couldn’t find that page.', status_code=404)
