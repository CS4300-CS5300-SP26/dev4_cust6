from django.test import TestCase
from django.urls import reverse, resolve
from home.views import index, scan_page



class CameraPageTests(TestCase):

    def test_landing_page_links_to_scan(self):
        """Landing page should contain a link to the camera scan page"""
        response = self.client.get(reverse("index"))
        self.assertContains(response, "/scan/")

    def test_scan_url_resolves(self):
        """Scan URL should resolve to scan_page view"""
        resolver = resolve("/scan/")
        self.assertEqual(resolver.func, scan_page)

    def test_scan_page_status_code(self):
        """Camera scan page should load successfully"""
        response = self.client.get(reverse("scan"))
        self.assertEqual(response.status_code, 200)

    def test_scan_page_template(self):
        """Scan page should use scan.html"""
        response = self.client.get(reverse("scan"))
        self.assertTemplateUsed(response, "scan/scan.html")

    def test_scan_page_contains_camera_ui(self):
        """Scan page should contain camera UI elements"""
        response = self.client.get(reverse("scan"))
        content = response.content.decode().lower()

        keywords = ["camera", "video", "capture", "scan"]

        self.assertTrue(
            any(word in content for word in keywords),
            "Camera UI not detected on scan page"
        )
