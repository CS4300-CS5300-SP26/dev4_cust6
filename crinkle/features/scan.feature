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

    Scenario: User is prompted to log in if photo is taken without logging in
        Given I am not logged in
        When I take a photo of the card
        Then I should be prompted to log in

    Scenario: User can go back to landing page from camera page
        Given I am on the camera page
        When I tap the back button
        Then I should be taken back to the landing page