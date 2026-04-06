Feature: Grading Service Submission
  As a card collector
  I want to submit my card for professional grading
  So that I can get it graded without leaving the app

  Scenario: Successful submission as guest
    Given I am on the submission start page
    When I enter card name "Charizard Base Set" and select service "PSA"
    And I submit the start form
    Then I should be on the details page

  Scenario: Successful full submission
    Given I am on the details page with session data
    When I fill in all shipping and payment details
    And I submit the details form
    Then I should see the confirmation page
    And the submission should exist in the database

  Scenario: Submission as logged in user
    Given a user "naz" with password "StrongPass123!" exists
    And I am logged in as "naz"
    And I am on the submission start page
    When I enter card name "Pikachu" and select service "BGS"
    And I submit the start form
    Then I should be on the details page

  Scenario: Confirmation page shows submission details
    Given a submission exists for card "Mewtwo" with service "PSA"
    When I visit the confirmation page for that submission
    Then the confirmation page shows "Mewtwo"
    And the confirmation page shows service "PSA"

  Scenario: Details page with missing fields stays on page
    Given I am on the details page with session data
    When I submit the details form with missing fields
    Then I should stay on the details page
    And no submission should be created

  Scenario Outline: Start page accepts both grading services
    Given I am on the submission start page
    When I enter card name "Charizard" and select service "<service>"
    And I submit the start form
    Then I should be on the details page

    Examples:
      | service |
      | PSA     |
      | BGS     |