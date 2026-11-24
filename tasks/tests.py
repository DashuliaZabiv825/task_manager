from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Task


class TaskTests(TestCase):
    def setUp(self):
        self.a = User.objects.create_user('alice', password='pass12345')
        self.b = User.objects.create_user('bob', password='pass12345')
        self.t = Task.objects.create(owner=self.a, title='Задача Алисы')

    def test_login_required(self):
        urls = [reverse('tasks:list'), reverse('tasks:create'),
                reverse('tasks:edit', args=[self.t.id]), reverse('tasks:delete', args=[self.t.id])]
        for u in urls:
            r = self.client.get(u)
            self.assertEqual(r.status_code, 302)
            self.assertIn(reverse('users:login'), r.url)
        r = self.client.post(reverse('tasks:toggle', args=[self.t.id]))
        self.assertEqual(r.status_code, 302)
        self.t.refresh_from_db()
        self.assertFalse(self.t.completed)

    def test_list_shows_only_own_tasks(self):
        Task.objects.create(owner=self.b, title='Задача Боба')
        self.client.force_login(self.b)
        r = self.client.get(reverse('tasks:list'))
        self.assertContains(r, 'Задача Боба')
        self.assertNotContains(r, 'Задача Алисы')

    def test_list_order(self):
        Task.objects.create(owner=self.a, title='низкая', priority='low')
        Task.objects.create(owner=self.a, title='высокая', priority='high')
        Task.objects.create(owner=self.a, title='готово', priority='high', completed=True)
        self.client.force_login(self.a)
        r = self.client.get(reverse('tasks:list'))
        self.assertEqual([x.title for x in r.context['tasks']],
                         ['высокая', 'Задача Алисы', 'низкая', 'готово'])

    def test_owner_is_set_on_create(self):
        self.client.force_login(self.b)
        r = self.client.post(reverse('tasks:create'), {
            'title': 'Новая задача', 'description': '', 'due_date': '',
            'priority': 'normal', 'owner': self.a.id})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Task.objects.get(title='Новая задача').owner, self.b)

    def test_bad_due_date_is_not_500(self):
        self.client.force_login(self.a)
        r = self.client.post(reverse('tasks:create'), {
            'title': 'Плохая дата', 'due_date': 'не дата', 'priority': 'normal'})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Task.objects.filter(title='Плохая дата').exists())

    def test_cannot_edit_foreign_task(self):
        self.client.force_login(self.b)
        r = self.client.post(reverse('tasks:edit', args=[self.t.id]),
                             {'title': 'Взлом', 'priority': 'normal'})
        self.assertEqual(r.status_code, 404)
        self.t.refresh_from_db()
        self.assertEqual(self.t.title, 'Задача Алисы')

    def test_cannot_delete_foreign_task(self):
        self.client.force_login(self.b)
        r = self.client.post(reverse('tasks:delete', args=[self.t.id]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Task.objects.filter(id=self.t.id).exists())

    def test_cannot_toggle_foreign_task(self):
        self.client.force_login(self.b)
        r = self.client.post(reverse('tasks:toggle', args=[self.t.id]))
        self.assertEqual(r.status_code, 404)
        self.t.refresh_from_db()
        self.assertFalse(self.t.completed)

    def test_missing_id_gives_404(self):
        self.client.force_login(self.a)
        self.assertEqual(self.client.get(reverse('tasks:edit', args=[9999])).status_code, 404)
        self.assertEqual(self.client.get(reverse('tasks:delete', args=[9999])).status_code, 404)
        self.assertEqual(self.client.post(reverse('tasks:toggle', args=[9999])).status_code, 404)

    def test_toggle_completed(self):
        self.client.force_login(self.a)
        u = reverse('tasks:toggle', args=[self.t.id])
        self.client.post(u)
        self.t.refresh_from_db()
        self.assertTrue(self.t.completed)
        self.client.post(u)
        self.t.refresh_from_db()
        self.assertFalse(self.t.completed)

    def test_toggle_get_is_not_allowed(self):
        self.client.force_login(self.a)
        r = self.client.get(reverse('tasks:toggle', args=[self.t.id]))
        self.assertEqual(r.status_code, 405)

    def test_delete_via_get_does_not_delete(self):
        self.client.force_login(self.a)
        u = reverse('tasks:delete', args=[self.t.id])
        self.assertEqual(self.client.get(u).status_code, 200)
        self.assertTrue(Task.objects.filter(id=self.t.id).exists())
        self.assertEqual(self.client.post(u).status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.t.id).exists())

    def test_logout_only_by_post(self):
        self.client.force_login(self.a)
        self.assertEqual(self.client.get(reverse('users:logout')).status_code, 405)
        self.assertEqual(self.client.post(reverse('users:logout')).status_code, 200)
