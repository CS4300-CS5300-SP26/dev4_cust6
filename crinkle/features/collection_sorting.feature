Feature: Collection Sorting
    As a card collector
    I want to sort my cards by various critera
    So that I can quickly navigate my Collection

Scenario: Sort collection by card name
    Given I am logged in
    Given I have a collection of cards
    When I sort by card "name"
    Then my cards will be ordered by "name"

Scenario: Sort collection by card name descending
    Given I am logged in
    Given I have a collection of cards
    When I sort by card "-name"
    Then my cards will be ordered by "-name"

Scenario: Sort collection by scan date
    Given I am logged in
    Given I have a collection of cards
    When I sort by card "date_scanned"
    Then my cards will be ordered by "date_scanned"

Scenario: Sort collection by scan date descending
    Given I am logged in
    Given I have a collection of cards
    When I sort by card "-date_scanned"
    Then my cards will be ordered by "-date_scanned"

Scenario: Sort collection by card grade
    Given I am logged in
    Given I have a collection of cards
    When I sort by card "grading_notes"
    Then my cards will be ordered by "grading_notes"

Scenario: Sort collection by card grade descending
    Given I am logged in
    Given I have a collection of cards
    When I sort by card "-grading_notes"
    Then my cards will be ordered by "-grading_notes"
