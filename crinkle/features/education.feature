Feature: Education Page
  As a user
  I want to view the education page
  So that I can learn how to grade my Pokemon cards

  Scenario: Education page loads successfully
    Given the app is running
    When I visit the education page
    Then I should see a 200 response

  Scenario: Education page contains grading categories
    Given the app is running
    When I visit the education page
    Then I should see "Corners" on the education page
    And I should see "Edges" on the education page
    And I should see "Centering" on the education page
    And I should see "Surface" on the education page

  Scenario: Education page contains how to grade section
    Given the app is running
    When I visit the education page
    Then I should see "How to Grade" on the education page

  Scenario: Education page contains FAQ section
    Given the app is running
    When I visit the education page
    Then I should see "Grading FAQ" on the education page