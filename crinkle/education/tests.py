from django.test import TestCase, Client
from django.urls import reverse

class EducationViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_education_page_loads(self):
        response = self.client.get(reverse('education'))
        self.assertEqual(response.status_code, 200)

    def test_education_uses_correct_template(self):
        response = self.client.get(reverse('education'))
        self.assertTemplateUsed(response, 'education.html')

    def test_education_page_contains_how_to_grade(self):
        response = self.client.get(reverse('education'))
        self.assertContains(response, 'How to Grade')

    def test_education_page_contains_grading_faq(self):
        response = self.client.get(reverse('education'))
        self.assertContains(response, 'Grading FAQ')

    def test_education_page_contains_categories(self):
        response = self.client.get(reverse('education'))
        self.assertContains(response, 'Corners')
        self.assertContains(response, 'Edges')
        self.assertContains(response, 'Centering')
        self.assertContains(response, 'Surface')

    def test_education_url_resolves(self):
        response = self.client.get('/education/')
        self.assertEqual(response.status_code, 200)