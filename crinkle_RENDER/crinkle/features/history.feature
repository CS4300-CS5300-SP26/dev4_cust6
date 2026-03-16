Feature: Card History Page
  As a user
  I want to view my scanned card history
  So that I can track my collection

  Scenario: History page loads successfully
    Given the app is running
    When I visit the history page
    Then I should see a 200 response

  Scenario: History page shows scanned cards
    Given a card named "Charizard VMAX" exists in the database
    When I visit the history page
    Then I should see "Charizard VMAX" on the history page

  Scenario: History page shows empty state when no cards exist
    Given there are no cards in the database
    When I visit the history page
    Then I should see a 200 response