from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from parameterized import parameterized

from .models import GradeReport, Card, CardCollection


# Create your tests here.
class CollectionTestCase(TestCase):
    def set_up_user(self):
        """create and login a test user
        """
        username = 'username'
        password = 'p1234567890'
        self.user = User.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)

    def set_up_collection(self):
        """create a collection for the purpose of setup
        """
        self.collection = CardCollection.objects.create(user=self.user)
        self.collection.save()

        self.assertIsNotNone(self.collection.__str__())

    def set_up_add_card(self):
        """simulates saving a card to the collection
        """
        notes = GradeReport.objects.create(grade='Grade')
        card = Card.objects.create(user=self.user,
                                   name='Card',
                                   grading_notes=notes,
                                   picture_path="/",
                                   user_notes="",
                                   )
        card.name += f'-{card.pk}'  # add card primary key as differentiator
        card.save()
        self.cards = Card.objects.all()
        self.collection.cards.add(card)

        self.assertIsNotNone(notes.__str__())
        self.assertIsNotNone(card.__str__())

    def test_retrieve_no_login(self):
        """Test retrieval when not logged in
        """
        response = self.client.get(reverse('cards:collection'))
        # No response should be given, not authenticated should recieved 403 response
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')

    def test_retrieve_no_cards(self):
        """With no cards or collection the user should retrieve an empty collection
        """
        self.set_up_user()
        response = self.client.get(reverse('cards:collection'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['cards'], [])

        # check the cards returned, given seperately for ordering
        self.assertEqual(response.data['cards'], [])

    def test_retrieve_no_cards_belonging_to_user(self):
        """If there are cards but they don't belong to the user, they shouldn't be shown
        """
        user = User.objects.create(password="test_pass", username="inactive user")
        notes = GradeReport.objects.create(grade='Grade')
        card = Card.objects.create(user=user,
                                   name='Card',
                                   grading_notes=notes,
                                   picture_path="/",
                                   user_notes="",
                                   )
        card.save()  # save card not belonging to active user

        self.set_up_user()
        response = self.client.get(reverse('cards:collection'))

        self.assertEqual(response.status_code, 200)

        # check that no cards were returned as the only card belongs to another user
        self.assertEqual(response.data['cards'], [])

    def test_retrieve_collection_with_cards(self):
        """The standard case a collection is present with some cards in it
        """
        self.set_up_user()
        self.set_up_collection()
        self.set_up_add_card()
        self.set_up_add_card()
        self.set_up_add_card()

        # Show check that card and collection is created before proceeding
        self.assertIsNotNone(self.collection.__str__())

        response = self.client.get(reverse('cards:collection'))

        self.assertEqual(response.status_code, 200)

        # Check that all cards are present
        for card in response.data['cards']:
            self.assertEqual(card['name'], f'Card-{card['id']}')
            self.assertEqual(card['user'], self.user.pk)

    @parameterized.expand([
        ('name'),
        ('-name'),
        ('date_scanned'),
        ('-date_scanned'),
        ('grading_notes'),
        ('-grading_notes'),
        ('-what_is_this'),  # what happens when a user modifies the url parameter
        ('date_scanne'),  # what happens if a user copies only part of the url and cuts off the sort
    ])
    def test_retrieve_cards_ordered_name(self, sort_order):
        """test that cards can be sorted in varying orderings
        """
        self.set_up_user()
        self.set_up_collection()
        self.set_up_add_card()
        self.set_up_add_card()

        # make a request where the specified order is name
        response = self.client.get(reverse('cards:collection'), data={'order': sort_order})

        self.assertEqual(response.status_code, 200)

        # order the cards by the intended order
        ordered_cards = self.collection.order_collection(sort_order)

        # The ordered cards should be in the same order as the collection's cards
        for card in range(len(response.data['cards'])):
            # The cards of the responses should be in the same ordering
            response_card = response.data['cards'][card]['id']
            ordered_card = ordered_cards[card].id
            self.assertEqual(response_card, ordered_card)


class CardTestCase(TestCase):
    def set_up_user(self):
        """create and login a test user
        """
        username = 'username'
        password = 'p1234567890'
        self.user = User.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)

    def set_up_add_card(self):
        """simulates saving a card to the collection
        """
        notes = GradeReport.objects.create(grade='Grade')
        card = Card.objects.create(user=self.user,
                                   name='Card',
                                   grading_notes=notes,
                                   picture_path="/",
                                   user_notes="",
                                   )
        card.name += f'-{card.pk}'  # add card primary key as differentiator
        card.save()
        self.cards = Card.objects.all()

    def test_retrieve_no_login(self):
        """The user must be logged in to view cards
        """
        response = self.client.get(reverse('cards:view_card', args=[1]))
        # No response should be given, not authenticated should recieved 403 response
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')

    def test_retrieve_no_cards(self):
        """If there is no card to retrieve nothing should be found
        """
        self.set_up_user()
        response = self.client.get(reverse('cards:view_card', args=[1]))
        # No response to recieve give 404
        self.assertEqual(response.status_code, 404)

    def test_retrieve(self):
        """With the user logged in and cards existing, the user should be able to retrieve a card
        """
        self.set_up_user()
        self.set_up_add_card()
        response = self.client.get(reverse('cards:view_card', args=[self.cards.first().pk]))

        # a card should be retrived status returned will be 200
        self.assertEqual(response.status_code, 200)

        # on success the name of the returned card will be the first and only card
        # as only one was added
        self.assertEqual(response.data['name'], self.cards.first().name)

    def test_save_notes(self):
        """The user should be able to write and save notes to cards
        """
        self.set_up_user()
        self.set_up_add_card()
        self.assertEqual(self.cards.first().user_notes, '')  # no notes yet

        test_note = 'This is a test note'
        response = self.client.post(reverse('cards:save_card', args=[self.cards.first().pk]),
                                    data={'user_notes': test_note},
                                    )

        # a 200 status code should be recieved, and data of the updated card will be displayed
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_notes'], test_note)

    def test_mock_view_report(self):
        """test mocking function, not much effort put into this as it is simply a mock function standing 
        in for later implementations
        """

        self.set_up_user()
        response = self.client.get(reverse('cards:scan_report'))

        # ok it was created
        self.assertEqual(response.status_code, 200)

    def test_mock_save_report(self):
        """test mocking function, not much effort put into this as it is simply a mock function standing 
        in for later implementations
        """

        self.set_up_user()
        response = self.client.get(reverse('cards:save_report'))

        # ok it was created
        self.assertEqual(response.status_code, 200)
