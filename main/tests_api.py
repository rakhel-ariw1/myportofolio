import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)

    def test_search_and_empty_results(self):
        self.assertEqual(len(self.client.get(self.list_url, {"title": "PORT"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"title": "not-found"}).data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Changed")
        self.assertEqual(self.project.description, "My website")
        self.assertEqual(self.client.put(self.detail_url, {"title": "Incomplete"}, format="json").status_code, 400)
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url, {"user": self.owner.pk}, format="json")
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], "visitor")
        self.assertEqual(list(self.project.starred_by.all()), [self.visitor])
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        self.assertEqual(client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, 200)
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(response.status_code, 201)


class EducationAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser("owner", "owner@example.com", "test-password")
        self.visitor = User.objects.create_user("visitor", password="test-password")
        self.editor = User.objects.create_user("editor", password="test-password")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.payload = {
            "nama_institusi": "Universitas Indonesia", "jenjang": "s1",
            "tahun_mulai": 2025, "tahun_selesai": None, "deskripsi": "Sistem Informasi",
        }
        self.education = Education.objects.create(**self.payload)
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.star_url = reverse("api:education-star", args=[self.education.id])

    def test_public_read_search_and_safe_methods(self):
        self.assertEqual(self.client.get(self.list_url).status_code, 200)
        self.assertEqual(self.client.get(self.detail_url).data["jenjang_label"], "S1")
        self.assertEqual(len(self.client.get(self.list_url, {"q": "INDONESIA"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"q": "missing"}).data, [])
        for url in (self.list_url, self.detail_url):
            self.assertEqual(self.client.head(url).status_code, 200)
            self.assertEqual(self.client.options(url).status_code, 200)
        self.assertEqual(Education.objects.count(), 1)
        self.assertEqual(self.education.starred_by.count(), 0)

    def test_guest_and_visitor_cannot_manage(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"deskripsi": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.education.refresh_from_db()
        self.assertEqual(self.education.deskripsi, "Sistem Informasi")

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.patch(self.detail_url, {"deskripsi": "Updated"}, format="json").status_code, 200)
        self.education.refresh_from_db()
        self.assertEqual(self.education.deskripsi, "Updated")
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Education.objects.count(), 1)

    def test_owner_crud_and_read_only_fields(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "starred_by": [self.visitor.pk], "is_starred": True,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(self.client.put(self.detail_url, {"deskripsi": "Missing fields"}, format="json").status_code, 400)
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        self.assertEqual(self.client.patch(self.detail_url, {"deskripsi": "Updated"}, format="json").status_code, 200)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_validation_and_partial_year_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"nama_institusi": "<b></b>"}, "nama_institusi"),
            ({"jenjang": "invalid"}, "jenjang"),
            ({"tahun_mulai": 0}, "tahun_mulai"),
            ({"tahun_selesai": 2020}, "tahun_selesai"),
        ]:
            response = self.client.patch(self.detail_url, changes, format="json")
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.data)
        response = self.client.patch(self.detail_url, {
            "nama_institusi": "<b>Universitas Aman</b>", "deskripsi": "<b>Aman</b>",
        }, format="json")
        self.assertEqual(response.data["nama_institusi"], "Universitas Aman")
        self.assertEqual(response.data["deskripsi"], "Aman")

    def test_star_uses_current_user(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url, {"user": self.owner.pk}, format="json")
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], ["visitor"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(self.client.post(self.star_url).data["star_count"], 0)

    def test_session_csrf_and_editor_form(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.editor)
        self.assertEqual(client.patch(self.detail_url, {"deskripsi": "Edited"}, format="json").status_code, 403)
        page = client.get(reverse("main:update_education", args=[self.education.id]))
        self.assertEqual(page.status_code, 200)
        response = client.patch(self.detail_url, {"deskripsi": "Edited"}, format="json",
                                HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 200)


class APIIntegrationTest(APITestCase):
    def test_projects_page_issues_csrf_for_session_star(self):
        visitor = User.objects.create_user("visitor")
        project = Project.objects.create(title="Example", description="Description", tech_stack="Django")
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(visitor)
        page = client.get(reverse("main:show_projects"))
        self.assertContains(page, reverse("api:project-list"))
        self.assertNotContains(page, "item.fields")
        self.assertNotContains(page, 'src="/static/js/project.js"')
        response = client.post(reverse("api:project-star", args=[project.id]),
                               HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])

    def test_malformed_json_returns_400_without_creating_project(self):
        owner = User.objects.create_superuser("owner", "owner@example.com", "test-password")
        self.client.force_authenticate(user=owner)
        response = self.client.post(reverse("api:project-list"), '{"title":', content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Project.objects.count(), 0)
