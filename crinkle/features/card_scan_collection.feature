Feature: Scan grading and collection storage
  As a card collector
  I want captured scans to keep their photo and grade
  So that I can review them and save them to my collection when allowed

  Scenario: Guest receives a grade but cannot save the scanned card
    Given I am scanning as a guest
    When I submit a captured card photo for grading
    Then I should receive a grade for the scanned card
    And I should be told that guests cannot save cards
    When I try to save the scanned card
    Then the scanned card should not be saved to a collection

  Scenario: Authenticated user saves and deletes a scanned card
    Given I am logged in for card scanning
    When I submit a captured card photo for grading
    And I save the scanned card to my collection
    Then the scanned card should appear in my collection
    When I delete the saved card from my collection
    Then the saved card should be removed from my collection
