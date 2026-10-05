from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Achievement, Education, Experience


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

class AchievementPageTest(TestCase):
    def test_awards_page_accessible_and_uses_correct_template(self):
        response = self.client.get(reverse('main:show_achievement'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'achievement.html')

    def test_award_data_shown_on_page(self):
        Achievement.objects.create(
            title="Finalist of BIZIONARY Business Case Competition 2026",
            issuer="Himpunan Mahasiswa Bisnis Internasional",
            year="August 2026",
            category="business_case",
            level="National",
        )
        response = self.client.get(reverse('main:show_achievement'))
        self.assertContains(response, "Finalist of BIZIONARY Business Case Competition 2026")

    def test_empty_state_shown_when_no_awards(self):
        response = self.client.get(reverse('main:show_achievement'))
        self.assertContains(response, "Belum ada penghargaan")


class EducationAjaxTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            email="owner@example.com",
            password="safe-password-123",
        )
        self.visitor = User.objects.create_user(
            username="visitor",
            password="safe-password-123",
        )
        self.education = Education.objects.create(
            nama_institusi="Akademi AJAX Nusantara",
            jenjang="s1",
            tahun_mulai=2025,
            tahun_selesai=None,
            deskripsi="Sistem Informasi",
        )

    def test_page_renders_ajax_shell_instead_of_education_data(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")
        self.assertContains(response, "js/education.js")
        self.assertNotContains(response, self.education.nama_institusi)

    def test_json_endpoint_returns_manual_data_and_filters_results(self):
        self.education.starred_by.add(self.visitor)
        self.client.force_login(self.visitor)

        response = self.client.get(
            reverse("main:get_education_json"),
            {"q": "AJAX"},
        )
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], str(self.education.id))
        self.assertEqual(data[0]["jenjang_label"], "S1")
        self.assertEqual(data[0]["star_count"], 1)
        self.assertTrue(data[0]["is_starred"])
        self.assertEqual(data[0]["starred_by_names"], ["visitor"])

    def test_json_endpoint_returns_empty_list_for_unmatched_search(self):
        response = self.client.get(
            reverse("main:get_education_json"),
            {"q": "tidak ditemukan"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_only_superuser_can_create_education_through_ajax(self):
        payload = {
            "nama_institusi": "Institut Teknologi Bandung",
            "jenjang": "s1",
            "tahun_mulai": 2024,
            "tahun_selesai": "",
            "deskripsi": "Teknik Informatika",
        }

        anonymous_response = self.client.post(
            reverse("main:create_education_ajax"),
            payload,
        )
        self.assertEqual(anonymous_response.status_code, 403)

        self.client.force_login(self.visitor)
        visitor_response = self.client.post(
            reverse("main:create_education_ajax"),
            payload,
        )
        self.assertEqual(visitor_response.status_code, 403)

        self.client.force_login(self.owner)
        owner_response = self.client.post(
            reverse("main:create_education_ajax"),
            payload,
        )
        self.assertEqual(owner_response.status_code, 201)
        self.assertTrue(
            Education.objects.filter(nama_institusi="Institut Teknologi Bandung").exists()
        )

    def test_ajax_create_returns_validation_errors(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("main:create_education_ajax"),
            {
                "nama_institusi": "Universitas Uji",
                "jenjang": "s1",
                "tahun_mulai": 2026,
                "tahun_selesai": 2020,
                "deskripsi": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("tahun_selesai", response.json()["errors"])

    def test_ajax_create_strips_html_from_text_fields(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("main:create_education_ajax"),
            {
                "nama_institusi": '<img src="x" onerror="alert(1)">Universitas Aman',
                "jenjang": "s1",
                "tahun_mulai": 2026,
                "tahun_selesai": "",
                "deskripsi": "<b>Deskripsi</b> aman",
            },
        )

        self.assertEqual(response.status_code, 201)
        education = Education.objects.get(nama_institusi="Universitas Aman")
        self.assertEqual(education.deskripsi, "Deskripsi aman")

    def test_logged_in_user_can_toggle_star(self):
        self.client.force_login(self.visitor)
        url = reverse("main:toggle_education_star", args=[self.education.id])

        first_response = self.client.post(url)
        second_response = self.client.post(url)

        self.assertEqual(first_response.status_code, 200)
        self.assertTrue(first_response.json()["is_starred"])
        self.assertEqual(first_response.json()["star_count"], 1)
        self.assertFalse(second_response.json()["is_starred"])
        self.assertEqual(second_response.json()["star_count"], 0)

    def test_star_request_uses_csrf_protection(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.visitor)
        url = reverse("main:toggle_education_star", args=[self.education.id])

        rejected_response = csrf_client.post(url)
        csrf_client.get(reverse("main:show_education"))
        csrf_token = csrf_client.cookies["csrftoken"].value
        accepted_response = csrf_client.post(url, HTTP_X_CSRFTOKEN=csrf_token)

        self.assertEqual(rejected_response.status_code, 403)
        self.assertEqual(accepted_response.status_code, 200)

    def test_anonymous_user_cannot_toggle_star(self):
        response = self.client.post(
            reverse("main:toggle_education_star", args=[self.education.id])
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.education.starred_by.count(), 0)

    def test_non_superuser_cannot_edit_or_delete_education(self):
        self.client.force_login(self.visitor)

        edit_response = self.client.get(
            reverse("main:update_education", args=[self.education.id])
        )
        delete_response = self.client.post(
            reverse("main:delete_education", args=[self.education.id])
        )

        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)
        self.assertTrue(Education.objects.filter(pk=self.education.id).exists())
