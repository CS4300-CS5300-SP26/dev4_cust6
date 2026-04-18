Feature: Save scanned card into VM-backed media storage

  As a logged in collector
  I want scanned card images to be saved into server media storage
  So that they appear in my collection on the website

  Scenario: Logged in user saves a scan and sees it in the collection
    Given I am a logged in collector for VM media saves
    And I have a captured scan image ready to save
    And AI grading is stubbed for the VM media scenario
    When I submit the captured scan for grading
    And I save the graded scan to my collection using VM media storage
    Then a scan image file should exist in VM media storage
    And the saved scan should belong to my collection
    And the collection page should show the saved scan image
