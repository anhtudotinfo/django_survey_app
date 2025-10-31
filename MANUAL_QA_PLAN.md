# Manual QA Test Plan

## 📋 Overview

**Purpose**: Verify that all new features work correctly through the user interface  
**Scope**: Multi-section surveys, branch logic, file uploads, draft responses  
**Environment**: Development/Staging  
**Prerequisite**: All automated tests passing (34/34 ✅)

---

## 🎯 Test Coverage

| Feature | Tests | Priority |
|---------|-------|----------|
| Section Management | 8 tests | High |
| Branch Logic | 6 tests | High |
| File Upload | 7 tests | High |
| Draft Responses | 6 tests | High |
| Backward Compatibility | 4 tests | High |
| Responsive Design | 3 tests | Medium |
| Performance | 3 tests | Medium |

**Total Manual Tests**: 37

---

## 🧪 Test Cases

### Section 1: Admin - Section Management (8 tests)

#### Test 1.1: Create Survey with Sections
**Priority**: High  
**Steps**:
1. Login to admin: http://localhost:8000/moi-admin/
2. Go to Surveys → Add Survey
3. Enter name: "QA Test Survey 1"
4. Save
5. Go to Sections → Add Section
   - Survey: QA Test Survey 1
   - Name: "Personal Information"
   - Description: "Tell us about yourself"
   - Ordering: 1
6. Save

**Expected**: Section created successfully

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 1.2: Add Multiple Sections
**Priority**: High  
**Steps**:
1. Using survey from Test 1.1
2. Add Section 2:
   - Name: "Experience"
   - Ordering: 2
3. Add Section 3:
   - Name: "Feedback"
   - Ordering: 3

**Expected**: All 3 sections visible in admin list

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 1.3: Assign Questions to Sections
**Priority**: High  
**Steps**:
1. Go to Questions → Add Question
2. Select "QA Test Survey 1"
3. Select Section: "Personal Information"
4. Type: Text
5. Label: "What is your name?"
6. Required: Yes
7. Ordering: 1
8. Save
9. Repeat for 2 more questions in same section
10. Add 2 questions to "Experience" section

**Expected**: Questions assigned to correct sections

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 1.4: Section Ordering Validation
**Priority**: High  
**Steps**:
1. Try to create section with duplicate ordering (e.g., ordering=1 when another section has ordering=1)

**Expected**: Error message: "Section with this Survey and Ordering already exists"

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 1.5: Section Deletion Protection
**Priority**: Medium  
**Steps**:
1. Try to delete section that has questions assigned

**Expected**: Error or warning about existing questions

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 1.6: Inline Section Management
**Priority**: Medium  
**Steps**:
1. Go to Surveys → Edit "QA Test Survey 1"
2. Check if sections are visible inline
3. Try editing section name inline

**Expected**: Sections manageable from survey edit page

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 1.7: Section Display in Question Admin
**Priority**: Medium  
**Steps**:
1. Go to Questions list
2. Check "Section" column visible
3. Filter by section

**Expected**: Section info visible and filterable

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 1.8: Section Count in Survey Admin
**Priority**: Low  
**Steps**:
1. Go to Surveys list
2. Check "Section count" column

**Expected**: Shows correct count (3 for test survey)

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

### Section 2: Admin - Branch Logic (6 tests)

#### Test 2.1: Create Simple Branch Rule
**Priority**: High  
**Steps**:
1. Go to Sections → Edit "Personal Information" section
2. In Branch Rules inline, add rule:
   - Condition Question: [select a radio question]
   - Operator: equals
   - Condition Value: [valid choice value]
   - Next Section: "Feedback" (skip Experience)
   - Priority: 0
3. Save

**Expected**: Rule created successfully

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 2.2: Branch Rule Validation - Invalid Value
**Priority**: High  
**Steps**:
1. Create branch rule with condition_value that doesn't match question choices

**Expected**: Validation error with helpful message

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 2.3: Branch Rule - Question from Wrong Section
**Priority**: High  
**Steps**:
1. Try to create rule in Section 1 using question from Section 3 (future section)

**Expected**: Validation error: "Question must be from current or previous section"

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 2.4: Branch Rule - Circular Reference Warning
**Priority**: Medium  
**Steps**:
1. Create Rule in Section 2 → Next Section: Section 3
2. Create Rule in Section 3 → Next Section: Section 2
3. Save

**Expected**: Warning message about circular references

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 2.5: Branch Rule Priority
**Priority**: Medium  
**Steps**:
1. Create 2 rules for same section with different priorities
2. Check they're ordered by priority in list

**Expected**: Rules displayed in priority order (0, 1, 2...)

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 2.6: Standalone Branch Rule Admin
**Priority**: Low  
**Steps**:
1. Go to Branch Rules admin (standalone)
2. Check list display shows all relevant fields
3. Filter by survey/section

**Expected**: Branch rules manageable from standalone admin

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

### Section 3: File Upload (7 tests)

#### Test 3.1: Create File Upload Question
**Priority**: High  
**Steps**:
1. Create question with Type: "File Upload"
2. Label: "Upload your CV"
3. Help text: "PDF or Word documents only"
4. Required: Yes

**Expected**: Question created with file upload type

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 3.2: Upload Valid PDF File
**Priority**: High  
**Steps**:
1. Open survey with file upload question
2. Upload a PDF file (< 10MB)
3. Submit survey

**Expected**: File uploaded successfully, no errors

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 3.3: Upload Valid Image File
**Priority**: High  
**Steps**:
1. Upload JPG/PNG file (< 10MB)

**Expected**: File uploaded successfully

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 3.4: Reject Invalid File Type
**Priority**: High  
**Steps**:
1. Try to upload .exe file
2. OR rename .exe to .pdf and upload

**Expected**: Validation error: "File type not allowed"

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 3.5: Reject Oversized File
**Priority**: High  
**Steps**:
1. Try to upload file > 10MB

**Expected**: Error: "File too large. Maximum size: 10 MB"

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 3.6: File Download from Admin
**Priority**: High  
**Steps**:
1. After uploading file, go to admin
2. Answers → Find the file answer
3. Click file link

**Expected**: File downloads successfully

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 3.7: File Access Control
**Priority**: High  
**Steps**:
1. Upload file as User A
2. Login as User B
3. Try to access User A's file URL directly

**Expected**: Access denied (403/404)

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

### Section 4: Multi-Section Navigation (6 tests)

#### Test 4.1: Display First Section Only
**Priority**: High  
**Steps**:
1. Open survey URL: /create/qa-test-survey-1/
2. Check only Section 1 questions visible
3. Check Section 2 and 3 questions NOT visible

**Expected**: Only first section questions shown

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 4.2: Next Button Navigation
**Priority**: High  
**Steps**:
1. Fill out Section 1 questions
2. Click "Next" button

**Expected**: 
- Section 1 saved
- Section 2 displayed
- Progress indicator updates

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 4.3: Previous Button Navigation
**Priority**: High  
**Steps**:
1. From Section 2, click "Previous"

**Expected**: 
- Return to Section 1
- Previous answers pre-filled

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 4.4: Progress Indicator
**Priority**: Medium  
**Steps**:
1. Check progress bar/indicator visible
2. Verify shows "Section 1 of 3"
3. Navigate to Section 2
4. Verify shows "Section 2 of 3"

**Expected**: Progress indicator updates correctly

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 4.5: Validation Per Section
**Priority**: High  
**Steps**:
1. Leave required field empty in Section 1
2. Try to click "Next"

**Expected**: Validation error, stays on Section 1

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 4.6: Submit from Final Section
**Priority**: High  
**Steps**:
1. Fill all sections
2. On last section, see "Submit" button (not "Next")
3. Click Submit

**Expected**: 
- Survey submitted
- Success page shown
- Response saved in database

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

### Section 5: Branch Logic in Action (6 tests)

#### Test 5.1: Branch Rule - Condition Met
**Priority**: High  
**Setup**: Create rule: If Age="18-25" → Skip to Section 3  
**Steps**:
1. Fill Section 1, select Age="18-25"
2. Click Next

**Expected**: Jumps directly to Section 3 (skips Section 2)

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 5.2: Branch Rule - Condition Not Met
**Priority**: High  
**Setup**: Same rule as 5.1  
**Steps**:
1. Fill Section 1, select Age="26-35" (different value)
2. Click Next

**Expected**: Goes to Section 2 (sequential navigation)

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 5.3: Multiple Branch Rules - Priority
**Priority**: High  
**Setup**: 
- Rule 1 (priority 0): Age="18-25" → Section 3
- Rule 2 (priority 1): Age="18-25" → Section 4  
**Steps**:
1. Select Age="18-25"
2. Click Next

**Expected**: Rule 1 executes (priority 0 first) → Goes to Section 3

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 5.4: Branch to Survey End
**Priority**: Medium  
**Setup**: Create rule with Next Section = null (end survey)  
**Steps**:
1. Meet condition
2. Click Next

**Expected**: Shows success page, survey ends

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 5.5: Contains Operator
**Priority**: Medium  
**Setup**: Rule with operator="contains", value="student"  
**Steps**:
1. Enter text containing "student"
2. Click Next

**Expected**: Branch rule triggers

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 5.6: Not Equals Operator
**Priority**: Medium  
**Setup**: Rule with operator="not_equals", value="No"  
**Steps**:
1. Select any value except "No"
2. Click Next

**Expected**: Branch rule triggers

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

### Section 6: Draft Responses (6 tests)

#### Test 6.1: Save Draft (Authenticated User)
**Priority**: High  
**Steps**:
1. Login as user
2. Start filling survey
3. Fill Section 1 partially
4. Click "Save Draft" button

**Expected**: 
- Success message
- Draft saved notification

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 6.2: Resume Draft (Authenticated User)
**Priority**: High  
**Steps**:
1. After Test 6.1, close browser
2. Login again
3. Go to survey URL

**Expected**: 
- "Resume draft" banner visible
- Shows saved progress

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 6.3: Resume Draft - Pre-filled Answers
**Priority**: High  
**Steps**:
1. Click "Resume" from banner
2. Check all previously answered questions

**Expected**: All answers pre-filled correctly

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 6.4: Save Draft (Anonymous User)
**Priority**: High  
**Steps**:
1. Logout (or use incognito)
2. Fill survey partially
3. Save draft

**Expected**: Draft saved with session key

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 6.5: Resume Draft (Anonymous User - Same Session)
**Priority**: High  
**Steps**:
1. After Test 6.4, close browser
2. Re-open SAME browser (same session)
3. Go to survey URL

**Expected**: Draft resume banner shows

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 6.6: Draft Deleted on Submit
**Priority**: High  
**Steps**:
1. Save draft
2. Complete and submit survey
3. Try to access draft again

**Expected**: No draft found, fresh survey form

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

### Section 7: Backward Compatibility (4 tests)

#### Test 7.1: Survey Without Sections
**Priority**: High  
**Steps**:
1. Create survey (existing old survey)
2. Add questions WITHOUT assigning sections
3. Open survey form

**Expected**: All questions show on one page (old behavior)

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 7.2: Default Section Migration
**Priority**: High  
**Steps**:
1. Check admin for surveys created before migration
2. Verify they have "Default Section"

**Expected**: Old surveys automatically have default section

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 7.3: Existing Responses Still Visible
**Priority**: High  
**Steps**:
1. Check old survey responses (before sections feature)
2. View in admin

**Expected**: All old responses intact and viewable

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 7.4: Edit Existing Survey
**Priority**: Medium  
**Steps**:
1. Open old survey in admin
2. Edit without touching sections
3. Save

**Expected**: Survey still works, no errors

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

### Section 8: Responsive Design (3 tests)

#### Test 8.1: Mobile - Survey Form
**Priority**: Medium  
**Device**: iPhone/Android phone  
**Steps**:
1. Open survey on mobile
2. Test navigation buttons
3. Test form inputs

**Expected**: Usable on mobile, no layout issues

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 8.2: Tablet - Admin Interface
**Priority**: Low  
**Device**: iPad/Android tablet  
**Steps**:
1. Access admin on tablet
2. Try CRUD operations

**Expected**: Admin functional on tablet

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 8.3: Different Browsers
**Priority**: Medium  
**Browsers**: Chrome, Firefox, Safari, Edge  
**Steps**:
1. Test survey form in each browser
2. Test admin in each browser

**Expected**: Works in all major browsers

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

### Section 9: Performance (3 tests)

#### Test 9.1: Large Survey (Many Questions)
**Priority**: Medium  
**Steps**:
1. Create survey with 50+ questions across 10 sections
2. Fill and submit

**Expected**: 
- Page loads < 2 seconds
- No performance issues

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 9.2: File Upload Speed
**Priority**: Medium  
**Steps**:
1. Upload 10MB PDF file
2. Time the upload

**Expected**: Uploads in < 10 seconds on normal connection

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

#### Test 9.3: Many Branch Rules
**Priority**: Low  
**Steps**:
1. Create section with 5+ branch rules
2. Test navigation

**Expected**: No noticeable delay in navigation

**Status**: [ ] Pass [ ] Fail [ ] Blocked

---

## 📊 Test Execution Tracking

### Summary

| Section | Total Tests | Passed | Failed | Blocked | % Complete |
|---------|-------------|--------|--------|---------|------------|
| Section Management | 8 | 0 | 0 | 0 | 0% |
| Branch Logic Admin | 6 | 0 | 0 | 0 | 0% |
| File Upload | 7 | 0 | 0 | 0 | 0% |
| Multi-Section Nav | 6 | 0 | 0 | 0 | 0% |
| Branch Logic Action | 6 | 0 | 0 | 0 | 0% |
| Draft Responses | 6 | 0 | 0 | 0 | 0% |
| Backward Compat | 4 | 0 | 0 | 0 | 0% |
| Responsive Design | 3 | 0 | 0 | 0 | 0% |
| Performance | 3 | 0 | 0 | 0 | 0% |
| **TOTAL** | **49** | **0** | **0** | **0** | **0%** |

---

## 🐛 Bug Tracking

### Bugs Found

| ID | Test | Severity | Description | Status |
|----|------|----------|-------------|--------|
| B001 | | | | |
| B002 | | | | |

### Severity Levels
- **Critical**: Blocks core functionality
- **High**: Major feature broken
- **Medium**: Minor feature issue
- **Low**: Cosmetic or edge case

---

## ✅ Sign-Off

### QA Testing Completed By:

**Name**: _________________  
**Date**: _________________

### Results:
- **Total Tests**: 49
- **Passed**: ___
- **Failed**: ___  
- **Pass Rate**: ___%

### Recommendation:
- [ ] Ready for Production
- [ ] Ready with Minor Fixes
- [ ] Not Ready - Major Issues Found

**Notes**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## 📝 Notes Template

Use this template for each test execution:

```
Test: [Test ID and Name]
Date: [Date]
Tester: [Name]
Environment: [Dev/Staging/Prod]

Steps Executed:
1. 
2.
3.

Actual Result:


Expected Result:


Status: [Pass/Fail/Blocked]

Screenshots: [Attach if failed]

Notes:

```

---

**Document Version**: 1.0  
**Last Updated**: October 31, 2025  
**Status**: Ready for Execution
