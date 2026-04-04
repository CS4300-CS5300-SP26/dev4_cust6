Feature: Card Tracking
    As a card collector
    I want to know if a card is potentially valuable enough to be worth professional grading
    So that I can avoid wasting money submitting low-grade cards to professional services

    Scenario: Cards with value above threshold are valuable
        Given I am logged in
        Given I have a collection of cards of value 50
        When I set a value threshold of 40
        Then it is "True" that my cards are valuable

    Scenario: Cards with value below threshold are not valuable
        Given I am logged in
        Given I have a collection of cards of value 39
        When I set a value threshold of 40
        Then it is "False" that my cards are valuable

    Scenario: Cards matching threshold are valuable
        Given I am logged in
        Given I have a collection of cards of value 40
        When I set a value threshold of 40
        Then it is "True" that my cards are valuable

