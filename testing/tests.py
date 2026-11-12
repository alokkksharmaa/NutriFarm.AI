from decimal import Decimal
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .assessment import assess_sample
from .models import FeedSample, TestResult


class PublicPageTests(TestCase):
    def test_existing_homepage_and_information_pages_load(self):
        pages = (
            ('core:home', 'Know what'),
            ('testing:about', 'ABOUT NUTRIFARM AI'),
            ('testing:features', 'PLATFORM FEATURES'),
            ('testing:contact', 'CONTACT US'),
        )

        for url_name, expected_text in pages:
            with self.subTest(page=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_text)

    def test_contact_post_is_not_implemented_yet(self):
        response = self.client.post(reverse('testing:contact'), {'name': 'Farmer'})

        self.assertEqual(response.status_code, 501)
        self.assertContains(response, 'not implemented yet', status_code=501)

    @override_settings(DEBUG=False)
    def test_unknown_page_returns_friendly_404(self):
        response = self.client.get('/not-a-page/', HTTP_HOST='localhost')

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'We couldn’t find that page.', status_code=404)


class FarmerAccountTests(TestCase):
    def registration_data(self, **overrides):
        data = {
            'full_name': 'River Farmer',
            'username': 'river',
            'email': 'river@example.com',
            'password1': 'StrongFarmPassword!829',
            'password2': 'StrongFarmPassword!829',
        }
        data.update(overrides)
        return data

    def test_registration_creates_hashed_user_and_logs_in(self):
        response = self.client.post(
            reverse('testing:register'),
            self.registration_data(),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('testing:dashboard'))
        self.assertContains(response, 'Welcome, River Farmer.')
        user = User.objects.get(username='river')
        self.assertEqual(user.email, 'river@example.com')
        self.assertEqual(user.get_full_name(), 'River Farmer')
        self.assertNotEqual(user.password, 'StrongFarmPassword!829')
        self.assertTrue(user.check_password('StrongFarmPassword!829'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse('testing:register'),
            self.registration_data(password2='DifferentPassword!829'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='river').exists())
        self.assertIn('password2', response.context['form'].errors)

    def test_registration_and_login_pages_include_csrf_tokens(self):
        for url_name in ('testing:register', 'testing:login'):
            with self.subTest(page=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'csrfmiddlewaretoken')

    def test_login_and_logout_use_authentication_session(self):
        user = User.objects.create_user(username='river', password='StrongFarmPassword!829')

        response = self.client.post(
            reverse('testing:login'),
            {'username': 'river', 'password': 'StrongFarmPassword!829'},
        )
        self.assertRedirects(response, reverse('testing:dashboard'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

        response = self.client.post(reverse('testing:logout'))
        self.assertRedirects(response, reverse('core:home'))
        dashboard_response = self.client.get(reverse('testing:dashboard'))
        self.assertRedirects(
            dashboard_response,
            f"{reverse('testing:login')}?next={reverse('testing:dashboard')}",
        )

    def test_invalid_login_does_not_authenticate(self):
        User.objects.create_user(username='river', password='StrongFarmPassword!829')

        response = self.client.post(
            reverse('testing:login'),
            {'username': 'river', 'password': 'incorrect-password'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_requires_post(self):
        response = self.client.get(reverse('testing:logout'))

        self.assertEqual(response.status_code, 405)


class FeedSampleDashboardTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username='farmer-one',
            password='StrongFarmPassword!829',
            first_name='Avery',
            last_name='Farmer',
        )
        self.other_farmer = User.objects.create_user(
            username='farmer-two',
            password='StrongFarmPassword!829',
        )

    def create_sample(self, farmer, sample_name='Fresh silage'):
        return FeedSample.objects.create(
            farmer=farmer,
            sample_name=sample_name,
            feed_type=FeedSample.FeedType.SILAGE,
            ph_value=Decimal('5.20'),
            moisture=Decimal('62.50'),
            temperature=Decimal('19.00'),
            smell='Fresh',
            mold_present=False,
        )

    def test_dashboard_requires_login_and_displays_empty_counts(self):
        response = self.client.get(reverse('testing:dashboard'))
        self.assertRedirects(
            response,
            f"{reverse('testing:login')}?next={reverse('testing:dashboard')}",
        )

        self.client.force_login(self.farmer)
        response = self.client.get(reverse('testing:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome, Avery Farmer.')
        self.assertContains(response, 'TOTAL SAMPLES')
        self.assertContains(response, 'TESTED SAMPLES')
        self.assertContains(response, reverse('testing:sample_create'))
        self.assertContains(response, reverse('testing:sample_history'))
        self.assertEqual(response.context['total_samples'], 0)
        self.assertEqual(response.context['total_tested'], 0)
        self.assertQuerySetEqual(response.context['recent_samples'], [])

    def test_dashboard_counts_only_owned_database_records(self):
        sample = self.create_sample(self.farmer)
        TestResult.objects.create(
            sample=sample,
            quality_score=84,
            quality_status='Good',
            recommendations='Continue regular checks.',
        )
        self.create_sample(self.other_farmer, 'Other farmer sample')
        self.client.force_login(self.farmer)

        response = self.client.get(reverse('testing:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_samples'], 1)
        self.assertEqual(response.context['total_tested'], 1)
        self.assertEqual(list(response.context['recent_samples']), [sample])
        self.assertContains(response, 'Fresh silage')
        self.assertNotContains(response, 'Other farmer sample')
        self.assertEqual(sample.test_result.quality_status, 'Good')
        self.assertEqual(sample.test_result.quality_score, 84)

    def test_sample_detail_is_private_to_its_farmer(self):
        sample = self.create_sample(self.farmer)
        url = reverse('testing:sample_detail', args=[sample.pk])

        anonymous_response = self.client.get(url)
        self.assertRedirects(
            anonymous_response,
            f"{reverse('testing:login')}?next={url}",
        )

        self.client.force_login(self.other_farmer)
        self.assertEqual(self.client.get(url).status_code, 404)

        self.client.force_login(self.farmer)
        own_response = self.client.get(url)
        self.assertEqual(own_response.status_code, 200)
        self.assertContains(own_response, 'Fresh silage')

    def test_admin_has_both_models_registered_and_changelists_are_available(self):
        self.assertTrue(admin.site.is_registered(FeedSample))
        self.assertTrue(admin.site.is_registered(TestResult))
        admin_user = User.objects.create_superuser(
            username='site-admin',
            email='admin@example.com',
            password='StrongFarmPassword!829',
        )
        self.client.force_login(admin_user)

        sample_response = self.client.get('/admin/testing/feedSample/'.lower())
        result_response = self.client.get('/admin/testing/testresult/')

        self.assertEqual(sample_response.status_code, 200)
        self.assertEqual(result_response.status_code, 200)

    def test_admin_can_add_change_and_delete_sample_records(self):
        admin_user = User.objects.create_superuser(
            username='crud-admin',
            email='crud-admin@example.com',
            password='StrongFarmPassword!829',
        )
        self.client.force_login(admin_user)
        sample_data = {
            'sample_name': 'Admin sample',
            'farmer': self.farmer.pk,
            'feed_type': FeedSample.FeedType.SILAGE,
            'collection_date': timezone.localdate().isoformat(),
            'ph_value': '5.20',
            'moisture': '62.50',
            'temperature': '19.00',
            'smell': 'Fresh',
            '_save': 'Save',
        }

        response = self.client.post(reverse('admin:testing_feedsample_add'), sample_data)
        self.assertEqual(
            response.status_code,
            302,
            response.context['adminform'].form.errors if response.context else response.content[:2000],
        )
        sample = FeedSample.objects.get(sample_name='Admin sample')

        sample_data['sample_name'] = 'Updated sample'
        response = self.client.post(
            reverse('admin:testing_feedsample_change', args=[sample.pk]),
            sample_data,
        )
        self.assertEqual(response.status_code, 302)
        sample.refresh_from_db()
        self.assertEqual(sample.sample_name, 'Updated sample')

        response = self.client.post(
            reverse('admin:testing_feedsample_delete', args=[sample.pk]),
            {'post': 'yes'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(FeedSample.objects.filter(pk=sample.pk).exists())


class SampleManagementTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username='sample-farmer',
            password='StrongFarmPassword!829',
        )
        self.other_farmer = User.objects.create_user(
            username='other-sample-farmer',
            password='StrongFarmPassword!829',
        )
        self.client.force_login(self.farmer)

    def sample_data(self, **overrides):
        data = {
            'sample_name': 'Morning field sample',
            'feed_type': FeedSample.FeedType.GREEN_FODDER,
            'collection_date': timezone.localdate().isoformat(),
            'ph_value': '7.10',
            'moisture': '75.50',
            'temperature': '20.50',
            'smell': 'fresh',
            'observations': 'Cut from the north paddock.',
            'mold_present': 'on',
        }
        data.update(overrides)
        return data

    def test_submit_sample_persists_owner_and_shows_details_after_refresh(self):
        response = self.client.post(
            reverse('testing:sample_create'),
            self.sample_data(),
        )

        sample = FeedSample.objects.get(sample_name='Morning field sample')
        self.assertRedirects(
            response,
            reverse('testing:sample_detail', args=[sample.pk]),
        )
        self.assertEqual(sample.farmer, self.farmer)
        self.assertEqual(sample.collection_date, timezone.localdate())
        self.assertEqual(sample.ph_value, Decimal('7.10'))
        self.assertEqual(sample.moisture, Decimal('75.50'))
        self.assertEqual(sample.temperature, Decimal('20.50'))
        self.assertTrue(sample.mold_present)
        self.assertEqual(sample.observations, 'Cut from the north paddock.')

        refreshed_response = self.client.get(
            reverse('testing:sample_detail', args=[sample.pk]),
        )
        self.assertEqual(refreshed_response.status_code, 200)
        self.assertContains(refreshed_response, 'Cut from the north paddock.')
        self.assertContains(refreshed_response, 'Morning field sample')

        dashboard_response = self.client.get(reverse('testing:dashboard'))
        self.assertEqual(dashboard_response.context['total_samples'], 1)

    def test_posted_farmer_id_cannot_change_sample_owner(self):
        response = self.client.post(
            reverse('testing:sample_create'),
            self.sample_data(farmer=str(self.other_farmer.pk)),
        )

        self.assertEqual(response.status_code, 302)
        sample = FeedSample.objects.get(sample_name='Morning field sample')
        self.assertEqual(sample.farmer, self.farmer)

    def test_submission_rejects_invalid_values_and_future_dates(self):
        invalid_inputs = (
            ('ph_value', '14.01'),
            ('ph_value', '-0.01'),
            ('moisture', '100.01'),
            ('moisture', '-0.01'),
            ('temperature', '80.01'),
            ('temperature', '-20.01'),
            ('temperature', 'not-a-number'),
            ('collection_date', (timezone.localdate() + timedelta(days=1)).isoformat()),
            ('sample_name', ''),
        )

        for field_name, invalid_value in invalid_inputs:
            with self.subTest(field=field_name, value=invalid_value):
                response = self.client.post(
                    reverse('testing:sample_create'),
                    self.sample_data(**{field_name: invalid_value}),
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(field_name, response.context['form'].errors)
                self.assertFalse(
                    FeedSample.objects.filter(sample_name='Morning field sample').exists()
                )

    def test_required_sample_fields_cannot_be_empty(self):
        required_fields = (
            'sample_name',
            'feed_type',
            'collection_date',
            'ph_value',
            'moisture',
            'temperature',
            'smell',
        )
        response = self.client.post(
            reverse('testing:sample_create'),
            self.sample_data(**{field_name: '' for field_name in required_fields}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(set(required_fields).issubset(response.context['form'].errors))
        self.assertFalse(FeedSample.objects.exists())

    def test_sample_form_requires_login_and_includes_csrf_token(self):
        self.client.logout()
        response = self.client.get(reverse('testing:sample_create'))
        self.assertRedirects(
            response,
            f"{reverse('testing:login')}?next={reverse('testing:sample_create')}",
        )

        self.client.force_login(self.farmer)
        response = self.client.get(reverse('testing:sample_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_csrf_middleware_rejects_sample_post_without_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.farmer)

        response = csrf_client.post(
            reverse('testing:sample_create'),
            self.sample_data(),
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(FeedSample.objects.exists())

    def test_history_shows_only_the_current_farmers_samples(self):
        own_sample = FeedSample.objects.create(
            farmer=self.farmer,
            sample_name='My paddock sample',
            feed_type=FeedSample.FeedType.DRY_FODDER,
            collection_date=timezone.localdate(),
            ph_value=Decimal('6.20'),
            moisture=Decimal('20.00'),
            temperature=Decimal('18.00'),
            smell='fresh',
        )
        FeedSample.objects.create(
            farmer=self.other_farmer,
            sample_name='Private other sample',
            feed_type=FeedSample.FeedType.SILAGE,
            collection_date=timezone.localdate(),
            ph_value=Decimal('5.20'),
            moisture=Decimal('62.50'),
            temperature=Decimal('19.00'),
            smell='fresh',
        )

        response = self.client.get(reverse('testing:sample_history'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['samples']), [own_sample])
        self.assertContains(response, 'My paddock sample')
        self.assertNotContains(response, 'Private other sample')

    def test_history_displays_helpful_empty_state(self):
        response = self.client.get(reverse('testing:sample_history'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No samples yet')
        self.assertContains(response, 'Submit your first sample')

    def test_other_farmer_cannot_open_sample_details(self):
        sample = FeedSample.objects.create(
            farmer=self.other_farmer,
            sample_name='Not your sample',
            feed_type=FeedSample.FeedType.SILAGE,
            collection_date=timezone.localdate(),
            ph_value=Decimal('5.20'),
            moisture=Decimal('62.50'),
            temperature=Decimal('19.00'),
            smell='fresh',
        )

        response = self.client.get(
            reverse('testing:sample_detail', args=[sample.pk]),
        )

        self.assertEqual(response.status_code, 404)


class AssessmentEngineTests(TestCase):
    def test_valid_sample_returns_prototype_category_without_score(self):
        sample = SimpleNamespace(
            ph_value=Decimal('6.50'),
            moisture=Decimal('60.00'),
            temperature=Decimal('22.00'),
            smell='fresh',
            mold_present=False,
        )

        assessment = assess_sample(sample)

        self.assertEqual(assessment['quality_status'], 'Within prototype criteria')
        self.assertIsNone(assessment['quality_score'])
        self.assertIn('illustrative', assessment['assessment_explanation'])
        self.assertIn('not scientifically validated', assessment['assessment_explanation'])
        self.assertTrue(assessment['recommendations'])

    def test_missing_or_unusable_measurements_return_incomplete_result(self):
        sample = SimpleNamespace(
            ph_value=None,
            moisture='not recorded',
            temperature=Decimal('20.00'),
            smell='',
            mold_present=None,
        )

        assessment = assess_sample(sample)

        self.assertEqual(assessment['quality_status'], 'Incomplete')
        self.assertIsNone(assessment['quality_score'])
        self.assertIn('pH', assessment['assessment_explanation'])
        self.assertIn('Moisture percentage', assessment['assessment_explanation'])
        self.assertIn('Smell condition', assessment['assessment_explanation'])
        self.assertIn('Visible mold observation', assessment['assessment_explanation'])
        self.assertIn('valid pH', assessment['recommendations'])

    def test_flagged_values_create_parameter_specific_recommendations(self):
        sample = SimpleNamespace(
            ph_value=Decimal('9.00'),
            moisture=Decimal('90.00'),
            temperature=Decimal('50.00'),
            smell='musty',
            mold_present=True,
        )

        assessment = assess_sample(sample)

        self.assertEqual(assessment['quality_status'], 'Needs review')
        self.assertIn('pH', assessment['recommendations'])
        self.assertIn('moisture', assessment['recommendations'].lower())
        self.assertIn('temperature', assessment['recommendations'].lower())
        self.assertIn('smell', assessment['recommendations'].lower())
        self.assertIn('mold', assessment['recommendations'].lower())


class AssessmentViewTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username='assessment-farmer',
            password='StrongFarmPassword!829',
        )
        self.other_farmer = User.objects.create_user(
            username='other-assessment-farmer',
            password='StrongFarmPassword!829',
        )
        self.sample = FeedSample.objects.create(
            farmer=self.farmer,
            sample_name='Assessment silage',
            feed_type=FeedSample.FeedType.SILAGE,
            collection_date=timezone.localdate(),
            ph_value=Decimal('6.50'),
            moisture=Decimal('60.00'),
            temperature=Decimal('22.00'),
            smell='fresh',
            mold_present=False,
        )

    def test_evaluate_persists_result_and_re_evaluation_updates_it(self):
        self.client.force_login(self.farmer)
        evaluate_url = reverse('testing:evaluate_sample', args=[self.sample.pk])
        result_url = reverse('testing:sample_result', args=[self.sample.pk])

        first_response = self.client.post(evaluate_url)
        self.assertRedirects(first_response, result_url)
        result = TestResult.objects.get(sample=self.sample)
        first_id = result.pk
        first_tested_at = result.tested_at
        self.assertEqual(result.quality_status, 'Within prototype criteria')
        self.assertIsNone(result.quality_score)
        self.assertIn('illustrative', result.assessment_explanation)

        self.sample.mold_present = True
        self.sample.save(update_fields=['mold_present'])
        later_time = first_tested_at + timedelta(minutes=1)
        with patch('testing.views.timezone.now', return_value=later_time):
            second_response = self.client.post(evaluate_url)

        self.assertRedirects(second_response, result_url)
        result.refresh_from_db()
        self.assertEqual(TestResult.objects.filter(sample=self.sample).count(), 1)
        self.assertEqual(result.pk, first_id)
        self.assertEqual(result.quality_status, 'Needs review')
        self.assertEqual(result.tested_at, later_time)

    def test_sample_detail_and_result_page_show_assessment(self):
        self.client.force_login(self.farmer)
        self.client.post(reverse('testing:evaluate_sample', args=[self.sample.pk]))

        detail_response = self.client.get(reverse('testing:sample_detail', args=[self.sample.pk]))
        result_response = self.client.get(reverse('testing:sample_result', args=[self.sample.pk]))

        self.assertContains(detail_response, 'Within prototype criteria')
        self.assertContains(
            detail_response,
            reverse('testing:sample_result', args=[self.sample.pk]),
        )
        self.assertContains(detail_response, 'Mold present:')
        self.assertContains(result_response, 'PROTOTYPE CATEGORY')
        self.assertContains(result_response, 'not scientifically validated')
        self.assertContains(result_response, self.sample.collection_date.strftime('%b'))

    def test_unevaluated_result_page_has_evaluate_action_and_detail_message(self):
        self.client.force_login(self.farmer)

        result_response = self.client.get(reverse('testing:sample_result', args=[self.sample.pk]))
        detail_response = self.client.get(reverse('testing:sample_detail', args=[self.sample.pk]))

        self.assertContains(result_response, 'This sample has not been assessed yet.')
        self.assertContains(detail_response, 'This sample has not been assessed yet.')
        self.assertContains(result_response, reverse('testing:evaluate_sample', args=[self.sample.pk]))

    def test_assessment_is_post_only_and_uses_csrf(self):
        self.client.force_login(self.farmer)
        evaluate_url = reverse('testing:evaluate_sample', args=[self.sample.pk])
        self.assertEqual(self.client.get(evaluate_url).status_code, 405)

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.farmer)
        response = csrf_client.post(evaluate_url)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(TestResult.objects.filter(sample=self.sample).exists())

    def test_user_cannot_evaluate_or_view_another_users_result(self):
        self.client.force_login(self.other_farmer)
        result_url = reverse('testing:sample_result', args=[self.sample.pk])
        evaluate_url = reverse('testing:evaluate_sample', args=[self.sample.pk])

        self.assertEqual(self.client.get(result_url).status_code, 404)
        self.assertEqual(self.client.post(evaluate_url).status_code, 404)
        self.assertFalse(TestResult.objects.filter(sample=self.sample).exists())

    def test_assessment_route_requires_authentication(self):
        response = self.client.post(
            reverse('testing:evaluate_sample', args=[self.sample.pk]),
        )

        self.assertRedirects(
            response,
            f"{reverse('testing:login')}?next={reverse('testing:evaluate_sample', args=[self.sample.pk])}",
        )
