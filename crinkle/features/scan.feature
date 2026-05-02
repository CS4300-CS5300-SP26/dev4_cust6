Feature: Card Scanning

    As a user
    I want to scan cards using the application
    So that I can receive grades for my crads

    Background:
        Given the application is running

    Scenario: Navigate to scan page from landing page
        Given I am on the landing page
        When I tap the scan button
        Then I should be taken to the scan page

    Scenario: Initialise camera on scan page
        Given I am on the scan page
        When the scan page loads
        Then the camera should be initialised

    Scenario: Frame for card pops up
        Given the camera is initialised
        When the scan page is displayed
        Then a frame for the card should appear

    Scenario: Frame for card is horizontal
        Given the frame for the card is displayed
        Then the frame should be horizontal

    Scenario: User is prompted to take a photo and place the card in frame
        Given the frame for the card is displayed
        Then I should be prompted to place the card in the frame and take a photo

    Scenario: Successfully take a photo of the card
        Given I have a card ready to scan
        When I select the scan option
        And I place the card in the frame
        And I press the camera button
        Then the photo should be taken successfully
        And the image should be displayed in the application    

    Scenario: User has option to retake photo
        Given a photo has been taken
        Then I should see an option to retake the photo

    Scenario: Guest can grade a scanned card but must log in to save it
        Given I am not logged in
        And I have taken a captured scan image
        When I request a grade for the captured scan
        Then I should see the grading report
        And I should see a prompt to create an account to save to collection
        When I try to save the scanned card to my collection
        Then I should be redirected to the login page

    @stub_ai
    Scenario: Logged in user can save a scanned image to the collection
        Given I am logged in
        And I have taken a captured scan image
        When I request a grade for the captured scan
        And I save the scanned card to my collection
        Then the scanned card image should be saved in my collection

    Scenario: User can go back to landing page from camera page
        Given I am on the camera page
        When I tap the back button
        Then I should be taken back to the landing page
    Scenario: Guest receives AI grade after scanning a card
    Given I am not logged in
    And I have taken a captured scan image
    When I request a grade for the captured scan
    Then I should see the scan report page
    And I should see a PSA grade on the report

  Scenario: AI grade breakdown shows all four criteria
    Given I am not logged in
    And I have taken a captured scan image
    When I request a grade for the captured scan
    Then I should see the scan report page
    And I should see corners analysis on the report
    And I should see edges analysis on the report
    And I should see centering analysis on the report
    And I should see surface analysis on the report

  Scenario: Grade result is stored in session after scanning
    Given I am not logged in
    And I have taken a captured scan image
    When I request a grade for the captured scan
    Then the grade result should be stored in the session    
  Scenario: AI identifies card set and year from scan
    Given I am not logged in
    And I have taken a captured scan image
    When I request a grade for the captured scan
    Then I should see the scan report page

  Scenario: Poor quality image shows feedback instead of grade
    Given I am not logged in
    And I have taken a captured scan image
    When I request a grade for the captured scan
    Then I should see the scan report page

  Scenario: Poor quality image shows retake button
    Given I am not logged in
    And I have taken a captured scan image
    When I request a grade for the captured scan
    Then I should see the scan report page  
