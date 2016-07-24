from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape

from lists.views import home_page
from lists.models import Item, List
from lists.forms import ItemForm


class HomePageTest(TestCase):
    maxDiff = None

#    def test_root_url_resolves_to_home_page_view(self):
#        found = resolve('/')
#        self.assertEqual(found.func, home_page)
#
#    def test_home_page_returns_correct_html(self):
#        request = HttpRequest()
#        response = home_page(request)
#        expected_html = render_to_string(
#            'home.html', 
#            # request=request,
#            {'form': ItemForm()}
#        )
#
#        self.assertEqual(response.content.decode(), expected_html)
#        # 긴 문자열 비교할 때 유용. diff 형태의 결과를 보여주지만,
#        # 너무 긴 경우 뒷부분을 자르도록 maxDiff = None 설정
#        self.assertMultiLineEqual(response.content.decode(), expected_html)

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_itemform(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)



class ListViewTest(TestCase):

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/{id}/'.format(id=list_.id))
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='item 1', list=correct_list)
        Item.objects.create(text='item 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='other item 1', list=other_list)
        Item.objects.create(text='other item 2', list=other_list)

        response = self.client.get('/lists/{id}/'.format(id=correct_list.id))

        self.assertContains(response, 'item 1')
        self.assertContains(response, 'item 2')
        self.assertNotContains(response, 'other item 1')
        self.assertNotContains(response, 'other item 2')

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.get('/lists/{id}/'.format(id=correct_list.id))
        self.assertEqual(response.context['list'], correct_list)


    def test_saving_a_POST_request(self):
        self.client.post(
            '/lists/new',
            data={'text': '신규 작업 아이템'}
        )

        # 모델 연동 테스트
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, '신규 작업 아이템')

    def test_redirects_after_POST(self):
        response = self.client.post(
            '/lists/new',
            data={
                'text': '신규 작업 아이템',     
            }
        )

        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/{id}/'.format(id=new_list.id))
        # self.assertEqual(response.status_code, 302)
        # self.assertEqual(response['location'], '/lists/the-only-list-in-the-world/')

    def test_saving_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            '/lists/{id}/'.format(id=correct_list.id),
            data={'text': '신규 작업 아이템 in existing list'}
        )

        # 모델 연동 테스트
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, '신규 작업 아이템 in existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            '/lists/{id}/'.format(id=correct_list.id),
            data={
                'text': '신규 작업 아이템 in existing list',     
            }
        )

        self.assertRedirects(response, '/lists/{id}/'.format(id=correct_list.id))

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        expected_error = escape("You can't have an empty list item")
        #print(response.content.decode())
        self.assertContains(response, expected_error)

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_validation_errors_end_up_on_lists_page(self):
        list_ = List.objects.create()
        response = self.client.post(
            '/lists/{list_id}/'.format(list_id=list_.id),
            data={'text': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)
