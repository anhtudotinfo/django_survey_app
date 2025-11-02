# Testing Guide for Fixed Issues

## Overview
This guide helps you verify that all three issues have been fixed successfully.

## Prerequisites
- Development server should be running on `http://127.0.0.1:8000`
- You should be logged in as a staff user
- At least one survey should exist in the database

## Issue 1: Field Type Dropdown (dashboard/forms)

### Steps to Test:
1. Navigate to the forms page:
   ```
   http://127.0.0.1:8000/dashboard/forms/<survey-slug>/
   ```
   Replace `<survey-slug>` with any survey slug (e.g., `a`, `abc`, `guest-survey-test`)

2. Click the blue floating "Savol qo'shish" (Add Question) button at the bottom right

3. A modal should appear with the title "Field Type"

4. **Verify:** You should see a grid of 11 field types:
   - Text (icon: bi bi-type)
   - Number (icon: bi bi-123)
   - Radio (icon: bi bi-ui-radios)
   - Select (icon: bi bi-menu-button-wide-fill)
   - Multi Select (icon: bi bi-ui-checks)
   - Text Area (icon: bi bi-textarea-resize)
   - URL (icon: bi bi-link)
   - Email (icon: bi bi-envelope)
   - Date (icon: bi bi-calendar-event)
   - Rating (icon: bi bi-star)
   - File Upload (icon: bi bi-cloud-upload)

5. **Success Criteria:**
   - No JavaScript errors in the browser console
   - All 11 field types are displayed with icons
   - Clicking on any field type creates a new question

### Before the Fix:
- Browser console showed: `Uncaught ReferenceError: loading is not defined`
- Modal was empty or showed no field types

## Issue 2: Summary Charts (dashboard/summary/survey/)

### Steps to Test:
1. Navigate to the summary page:
   ```
   http://127.0.0.1:8000/dashboard/summary/survey/<survey-slug>/
   ```

2. Wait for the page to load

3. **Verify:** Charts should be displayed for different question types:
   - **Radio/Select questions:** Pie charts showing distribution of answers
   - **Multi Select questions:** Bar charts showing count for each option
   - **Rating questions:** Bar charts with average rating and star display
   - **Question2 (teacher ratings):** ApexCharts bar charts at the bottom

4. **Success Criteria:**
   - All charts render correctly
   - Charts display actual data from survey responses
   - No JavaScript errors in the browser console
   - Filter options (Year, Month, Course) work correctly

### Before the Fix:
- Charts were not displayed
- Browser console might have shown Chart.js related errors

## Issue 3: Download CSV with Correct Ordering

### Steps to Test:
1. Navigate to the download page:
   ```
   http://127.0.0.1:8000/dashboard/download/survey/<survey-slug>/
   ```

2. A CSV file should automatically download

3. Open the CSV file in Excel, Google Sheets, or a text editor

4. **Verify:**
   - First row contains headers: `user`, `submitted time`, followed by question labels
   - Questions are in the correct order (matching the order you see on the forms page)
   - File upload answers show full URLs like:
     ```
     http://127.0.0.1:8000/download/file/10/
     ```
   - All answer fields are included (no missing columns)

5. **Additional Test:** Go back to the forms page and note the order of questions:
   - The CSV columns should match this exact order

### Before the Fix:
- Questions were sorted by ID instead of the `ordering` field
- CSV column order didn't match the display order

## Quick Test Script

If you have surveys in your database, you can run the test script:

```bash
cd /home/tuna/Desktop/django_survey_app
python3 test_fixes.py
```

This script will:
- Verify `get_type_field()` returns all 11 field types
- Check existing surveys and questions
- Test file upload answer URLs
- Validate summary generation

## Common Issues

### Server Not Running
If you get "Connection refused" errors:
```bash
cd /home/tuna/Desktop/django_survey_app
python3 manage.py runserver
```

### No Surveys Available
If you don't have any surveys:
1. Go to `http://127.0.0.1:8000/dashboard/`
2. Click "Create Survey"
3. Fill in the form and save
4. Then test the fixes with your new survey

### Permission Denied
If you can't access dashboard pages:
1. Make sure you're logged in
2. Your user account must have `is_staff=True`
3. You can check/update this in Django admin: `http://127.0.0.1:8000/admin/`

## Expected Results Summary

| Issue | Before | After |
|-------|--------|-------|
| Field Type Dropdown | Error: "loading is not defined", empty modal | Modal shows 11 field types with icons |
| Summary Charts | No charts displayed | Pie, bar, and rating charts display correctly |
| CSV Download | Questions ordered by ID | Questions ordered by `ordering` field |

## Additional Notes

- All fixes are backward compatible
- No database migrations are required
- The fixes work with existing data

## Need Help?

If any of the fixes don't work:
1. Check the browser console for JavaScript errors (F12 → Console tab)
2. Check Django logs in the terminal where `runserver` is running
3. Verify you're using the correct survey slug in URLs
4. Make sure your survey has questions and responses
