Feature: Account Management
  As a Crinkle user
  I want to register, log in, and manage my account
  So that I can save my grading history and collection

  # ── Registration ────────────────────────────────────────────────────────────

  Scenario: Successful registration
    Given I am on the register page
    When I fill in username "naz" email "naz@test.com" password "StrongPass123!"
    And I submit the registration form
    Then I should be redirected to my profile page
    And a user account should exist for "naz"

  Scenario: Registration with mismatched passwords
    Given I am on the register page
    When I fill in username "naz" email "naz@test.com" password "StrongPass123!"
    And I enter confirm password "WrongPass999!"
    And I submit the registration form
    Then I should stay on the register page
    And no account should be created for "naz"

  Scenario: Registration with duplicate username
    Given a user "naz" already exists
    And I am on the register page
    When I fill in username "naz" email "other@test.com" password "StrongPass123!"
    And I submit the registration form
    Then I should stay on the register page
    And only one account should exist for "naz"

  Scenario Outline: Registration with invalid inputs
    Given I am on the register page
    When I submit registration with username "<username>" email "<email>" password "<password>"
    Then I should stay on the register page
    And no account should be created for "<username>"

    Examples:
      | username | email          | password       |
      | naz      | not-an-email   | StrongPass123! |
      | naz      | naz@test.com   | 123            |

  # ── Login ───────────────────────────────────────────────────────────────────

  Scenario: Successful login
    Given a user "naz" with password "StrongPass123!" exists
    And I am on the login page
    When I log in with username "naz" and password "StrongPass123!"
    Then I should be redirected to my profile page

  Scenario: Login with wrong password
    Given a user "naz" with password "StrongPass123!" exists
    And I am on the login page
    When I log in with username "naz" and password "WrongPass!"
    Then I should stay on the login page

  Scenario: Login with non-existent user
    Given I am on the login page
    When I log in with username "ghost" and password "StrongPass123!"
    Then I should stay on the login page

  Scenario Outline: Login with invalid credentials
    Given a user "naz" with password "StrongPass123!" exists
    And I am on the login page
    When I log in with username "<username>" and password "<password>"
    Then I should stay on the login page

    Examples:
      | username | password       |
      | naz      | WrongPassword! |
      | nobody   | StrongPass123! |

  # ── Profile ─────────────────────────────────────────────────────────────────

  Scenario: Logged-in user can view profile
    Given a user "naz" with password "StrongPass123!" exists
    And I am logged in as "naz"
    When I visit the profile page
    Then I should see my username "naz" on the page

  Scenario: Unauthenticated user cannot view profile
    Given I am not logged in
    When I visit the profile page
    Then I should be redirected to the login page

  # ── Logout ──────────────────────────────────────────────────────────────────

  Scenario: User can log out
    Given a user "naz" with password "StrongPass123!" exists
    And I am logged in as "naz"
    When I log out
    Then I should be redirected to the home page
    And I should not be able to access the profile page

  # ── Guest mode ──────────────────────────────────────────────────────────────

  Scenario: Guest can continue without account
    Given I am on the login page
    When I click continue as guest
    Then I should be redirected to the home page
    And the guest session flag should be set