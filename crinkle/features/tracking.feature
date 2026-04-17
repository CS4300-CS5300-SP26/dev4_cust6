Feature: Card Tracking
  As a Crinkle user
  I want to track Pokémon cards I'm watching or have sold
  So that I can monitor my watchlist and sales

  Scenario: Add a card to tracking
    Given I am on the tracking add page
    When I fill in card name "Charizard" set "Base Set" year "1999"
    And I select grade tier "PSA 9" and status "Watching"
    And I submit the tracking form
    Then I should be redirected to the tracking list
    And I should see "Charizard" in the tracking list

  Scenario: Add a card with no name fails
    Given I am on the tracking add page
    When I submit the tracking form without a card name
    Then I should stay on the add card page
    And no card should be created

  Scenario: Add a sold card
    Given I am on the tracking add page
    When I fill in card name "Blastoise" set "Base Set" year "1999"
    And I select grade tier "PSA 10" and status "Sold"
    And I submit the tracking form
    Then I should be redirected to the tracking list
    And I should see "Blastoise" in the tracking list

  Scenario: View tracking list
    Given a card "Mewtwo" with status "Watching"
    When I visit the tracking list
    Then I should see "Mewtwo" in the tracking list

  Scenario: View card detail
    Given a card "Pikachu" with status "Watching"
    When I view the detail page for "Pikachu"
    Then I should see "Pikachu" on the page
    And I should see "Watching" on the page

  Scenario: Filter by status
    Given a card "Mewtwo" with status "Watching"
    And a card "Venusaur" with status "Sold"
    When I filter the tracking list by "sold"
    Then I should see "Venusaur" in the tracking list
    And I should not see "Mewtwo" in the tracking list

  Scenario: Edit a tracked card
    Given a card "Mewtwo" with status "Watching"
    When I edit "Mewtwo" and change status to "Sold"
    Then the card "Mewtwo" should have status "sold"

  Scenario: Delete a tracked card
    Given a card "Jigglypuff" with status "Watching"
    When I delete the card "Jigglypuff"
    Then "Jigglypuff" should not exist in tracking

  Scenario: Sold tab shows total
    Given a card "Charizard" with status "Sold"
    And that card was sold for "300.00"
    And a card "Blastoise" with status "Sold"
    And that card was sold for "200.00"
    When I filter the tracking list by "sold"
    Then the sold total should be "500.00"

  Scenario: View market page
    Given I visit the market page
    Then I should see the market page

  Scenario: Search market
    Given a pricing entry for "Charizard" in "Base Set"
    When I search the market for "Charizard"
    Then I should see "Charizard" in the market results

  Scenario: View card pricing
    Given a pricing entry for "Mewtwo" in "Base Set"
    When I view pricing for "Mewtwo" in "Base Set"
    Then I should see "Mewtwo" on the page
    And I should see "Near Mint" on the page