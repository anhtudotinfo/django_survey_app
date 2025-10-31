# Admin Guide: Sections and Branch Logic Setup

## Table of Contents
1. [Introduction](#introduction)
2. [Creating Multi-Section Surveys](#creating-multi-section-surveys)
3. [Setting Up Branch Logic](#setting-up-branch-logic)
4. [Common Scenarios](#common-scenarios)
5. [Testing Your Setup](#testing-your-setup)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Introduction

This guide walks through creating surveys with multiple sections and conditional navigation (branch logic) in the Django admin interface.

### What You'll Learn
- How to organize questions into sections
- How to create navigation rules based on user answers
- How to test complex survey flows
- Common pitfalls and how to avoid them

### Prerequisites
- Admin account with superuser or survey management permissions
- Basic understanding of your survey's structure and flow
- Access to Django admin interface

---

## Creating Multi-Section Surveys

### Step-by-Step: Basic Multi-Section Survey

#### 1. Create the Survey

**Path**: Admin → Surveys → Add Survey

Fill in:
```
Name: Customer Satisfaction Survey 2025
Description: Annual customer feedback survey
Slug: customer-satisfaction-2025 (auto-generated)

Settings:
☑ Editable (users can edit responses)
☑ Deletable (users can delete responses)
☐ Duplicate Entry (allow multiple submissions)
☐ Private Response (only admin and owner can see)
☑ Can Anonymous User (allow anonymous submissions)

Notification To: feedback@company.com
Success Page Content: Thank you for your feedback!
```

Click **Save and continue editing**

#### 2. Add Sections to Survey

**Option A: Inline** (Recommended)

While still editing the survey, scroll to **SECTIONS** inline section:

```
Section 1:
  Name: Personal Information
  Description: Tell us about yourself
  Ordering: 1

Section 2:
  Name: Product Experience
  Description: Share your experience with our products
  Ordering: 2

Section 3:
  Name: Service Feedback
  Description: Rate our customer service
  Ordering: 3

Section 4:
  Name: Additional Comments
  Description: Any other thoughts?
  Ordering: 4
```

Click **Save**

**Option B: Separate** (Alternative)

Go to Admin → Sections → Add Section for each:

```
Survey: Customer Satisfaction Survey 2025
Name: Personal Information
Description: Tell us about yourself
Ordering: 1
```

Repeat for each section.

#### 3. Add Questions to Sections

**Path**: Admin → Questions → Add Question

**Section 1 Questions:**

```
Question 1:
  Survey: Customer Satisfaction Survey 2025
  Section: Personal Information
  Type: Text
  Label: What is your name?
  Required: ☑
  Ordering: 1

Question 2:
  Survey: Customer Satisfaction Survey 2025
  Section: Personal Information
  Type: Email
  Label: What is your email address?
  Help Text: We'll never share your email
  Required: ☑
  Ordering: 2

Question 3:
  Survey: Customer Satisfaction Survey 2025
  Section: Personal Information
  Type: Radio
  Label: Are you a current customer?
  Choices: Yes, No, Previously was
  Required: ☑
  Ordering: 3
```

**Section 2 Questions:**

```
Question 4:
  Survey: Customer Satisfaction Survey 2025
  Section: Product Experience
  Type: Select
  Label: Which product did you purchase?
  Choices: Product A, Product B, Product C, Product D
  Required: ☑
  Ordering: 4

Question 5:
  Survey: Customer Satisfaction Survey 2025
  Section: Product Experience
  Type: Rating
  Label: How would you rate the product quality?
  Choices: 5 (for 5-star rating)
  Required: ☑
  Ordering: 5
```

Continue for all sections...

#### 4. Preview Survey

**URL**: `/surveys/customer-satisfaction-2025/`

You should see:
- Section 1 questions only
- Progress indicator: "Section 1 of 4"
- Progress bar: 25%
- "Next" button (not Submit yet)

---

## Setting Up Branch Logic

### Understanding Branch Rules

Branch rules allow dynamic navigation:
- **Normal flow**: Section 1 → 2 → 3 → 4 → End
- **With branches**: Section 1 → 3 (skip 2) → End (skip 4)

### Components of a Branch Rule

```
Section: Which section this rule applies to
Condition Question: Which question to check
Operator: How to compare (equals, contains, etc.)
Condition Value: What value to match
Next Section: Where to go if match (or empty = end survey)
Priority: Order of evaluation (0 = highest)
```

### Step-by-Step: Adding Branch Logic

#### Scenario 1: Skip Section Based on Answer

**Goal**: If user is not a current customer, skip to feedback section

**Setup**:

1. Go to **Admin → Sections → Personal Information**
2. Scroll to **BRANCH RULES** inline
3. Click **Add another Branch rule**

```
Condition Question: Are you a current customer?
Operator: equals
Condition Value: No
Next Section: Additional Comments (skip Product & Service sections)
Priority: 0
```

4. Click **Save**

**Result**: 
- User answers "No" → jumps to Additional Comments
- User answers "Yes" → proceeds to Product Experience normally

#### Scenario 2: Multiple Branches (Product-Specific Questions)

**Goal**: Different questions for different products

**Setup Section 2 (Product Experience) Questions:**

```
Question 4: Which product did you purchase?
  Choices: Product A, Product B, Product C

Question 5: Rate Product A quality (only for Product A users)
Question 6: Rate Product B quality (only for Product B users)
Question 7: Rate Product C quality (only for Product C users)
```

But this is inefficient. Better approach:

**Create Product-Specific Sections:**

```
Section 2: Product Selection
Section 3a: Product A Questions
Section 3b: Product B Questions
Section 3c: Product C Questions
Section 4: Service Feedback (all products)
```

**Branch Rules on Section 2:**

```
Rule 1:
  Condition Question: Which product did you purchase?
  Operator: equals
  Condition Value: Product A
  Next Section: Product A Questions
  Priority: 0

Rule 2:
  Condition Question: Which product did you purchase?
  Operator: equals
  Condition Value: Product B
  Next Section: Product B Questions
  Priority: 1

Rule 3:
  Condition Question: Which product did you purchase?
  Operator: equals
  Condition Value: Product C
  Next Section: Product C Questions
  Priority: 2
```

**Branch Rules on Sections 3a, 3b, 3c:**

All three sections need this rule to converge back:

```
Condition Question: (leave as first question in section)
Operator: (doesn't matter, will never match)
Condition Value: (empty)
Next Section: Service Feedback
Priority: 99

OR simply rely on sequential navigation (no rule needed)
```

Actually, for convergence, better to not add rules and let it flow sequentially to section 4.

#### Scenario 3: Early Termination (Disqualification)

**Goal**: End survey if user selects "Not interested"

**Setup Section 1:**

```
Question 3: Are you interested in participating in this survey?
  Type: Radio
  Choices: Yes, No
```

**Branch Rule on Section 1:**

```
Condition Question: Are you interested in participating in this survey?
Operator: equals
Condition Value: No
Next Section: (Leave empty)
Priority: 0
```

**Result**: User answers "No" → survey ends immediately

#### Scenario 4: Skip Based on Text Content

**Goal**: If user mentions "support" in feedback, show support follow-up questions

**Setup Section 3:**

```
Question 10: What did you like about our service?
  Type: Text Area
```

**Create Section 3b: Support Follow-up**

```
Question 11: Please elaborate on your support experience
Question 12: Rate support responsiveness
```

**Branch Rule on Section 3:**

```
Condition Question: What did you like about our service?
Operator: contains
Condition Value: support
Next Section: Support Follow-up
Priority: 0
```

**Result**: If answer contains "support" (case-insensitive) → shows Section 3b

#### Scenario 5: Multiple Conditions (Using Priority)

**Goal**: Different paths for different age groups

**Setup Section 1:**

```
Question: What is your age?
  Type: Number
```

**Create Age-Specific Sections:**
- Section 2a: Under 18 Questions
- Section 2b: 18-65 Questions
- Section 2c: 65+ Questions

**Branch Rules on Section 1:**

Wait, we can't do numeric comparison with current operators!

**Alternative**: Use radio choices

```
Question: What is your age group?
  Type: Radio
  Choices: Under 18, 18-30, 31-50, 51-65, Over 65
```

**Branch Rules:**

```
Rule 1:
  Condition: Age group equals "Under 18"
  Next Section: Under 18 Questions
  Priority: 0

Rule 2:
  Condition: Age group in "18-30, 31-50, 51-65"
  Operator: in
  Condition Value: 18-30, 31-50, 51-65
  Next Section: Adult Questions
  Priority: 1

Rule 3:
  Condition: Age group equals "Over 65"
  Next Section: Senior Questions
  Priority: 2
```

---

## Common Scenarios

### 1. Linear Survey (No Branching)

**Use case**: Simple surveys where everyone answers same questions

**Setup**:
- Create sections
- Add questions to sections
- No branch rules needed
- Users progress: Section 1 → 2 → 3 → End

### 2. Conditional Skip Logic

**Use case**: Skip sections based on qualifying questions

**Example**:
```
Section 1: Screening
  Q: "Do you own a car?"
  If No → Skip to Final Section
  If Yes → Section 2: Car Ownership Questions
```

**Setup**:
```
Branch Rule (Section 1):
  Condition: Own car? equals "No"
  Next Section: Final Section
```

### 3. Parallel Paths (Choose Your Adventure)

**Use case**: Different question sets for different user types

**Example**:
```
Section 1: User Type Selection
  Q: "I am a..." → Individual / Business / Enterprise

Section 2a: Individual Questions
Section 2b: Business Questions
Section 2c: Enterprise Questions

Section 3: Common Final Questions (all converge here)
```

**Setup**:
```
Branch Rules (Section 1):
  Rule 1: Type = Individual → Section 2a (Priority 0)
  Rule 2: Type = Business → Section 2b (Priority 1)
  Rule 3: Type = Enterprise → Section 2c (Priority 2)

No rules needed on 2a/2b/2c - they naturally flow to Section 3
```

### 4. Nested Conditions

**Use case**: Sub-branching within branches

**Example**:
```
Section 1: Are you a customer? (Yes/No)
  If No → End survey
  If Yes → Section 2

Section 2: How satisfied are you? (Satisfied/Unsatisfied)
  If Satisfied → Section 3: Positive Feedback
  If Unsatisfied → Section 4: Improvement Suggestions

Sections 3 & 4 → Section 5: Final Comments
```

**Setup**:
```
Branch Rules (Section 1):
  Condition: Customer equals "No"
  Next Section: (empty = end)

Branch Rules (Section 2):
  Rule 1: Satisfied equals "Satisfied" → Section 3
  Rule 2: Satisfied equals "Unsatisfied" → Section 4
```

### 5. Complex Multi-Path Survey

**Example: Medical Intake Form**

```
Section 1: Basic Info
Section 2: Symptoms Check
  Q: Primary symptom? (Headache/Stomach/Respiratory/Other)
  
Section 3a: Headache Questions
Section 3b: Stomach Questions
Section 3c: Respiratory Questions
Section 3d: Other Symptoms

Section 4: Medical History (all converge)
Section 5: Emergency Contact
```

**Branch Rules**:
```
Section 2 → Branches to 3a/3b/3c/3d based on symptom
Sections 3a/3b/3c/3d → All flow to Section 4
```

---

## Testing Your Setup

### Pre-Launch Checklist

- [ ] All sections have appropriate ordering (1, 2, 3...)
- [ ] All questions assigned to sections
- [ ] Branch rules priorities set correctly
- [ ] No circular references
- [ ] All condition questions exist in current/previous sections

### Testing Process

#### 1. Test Sequential Path (No Branches Triggered)

Fill out survey with answers that DON'T match any branch conditions:
- Verify all sections shown in order
- Check progress indicator updates
- Confirm can navigate back
- Ensure submit works

#### 2. Test Each Branch Path

For each branch rule, test with matching condition:

**Example**:
```
Rule: If "Customer? = No" → Jump to Section 4

Test:
1. Start survey
2. Section 1: Answer "Customer?" with "No"
3. Click Next
4. VERIFY: Should jump to Section 4 (skip 2 and 3)
5. Complete survey
6. Check response in admin
```

#### 3. Test Priority Order

If multiple rules on same section:

```
Rule 1 (Priority 0): Age = "Under 18" → Section A
Rule 2 (Priority 1): Age = "18-30" → Section B

Test:
1. Answer "Under 18"
2. VERIFY: Goes to Section A (Rule 1 matched first)
3. Start new response
4. Answer "18-30"
5. VERIFY: Goes to Section B (Rule 2 matched)
```

#### 4. Test Edge Cases

- Empty answers (if not required)
- Special characters in text answers
- Very long text answers
- Multiple selections (for multi_select type)

#### 5. Test Draft Save/Resume

- Answer questions in Section 1
- Click "Save Draft"
- Logout/close browser
- Return and resume
- VERIFY: Returns to same section with answers filled

### Testing Tools

**Admin View**:
```
Admin → User Answers → [Select response] → View details
```

Check:
- Which sections were shown
- Which were skipped
- Answer values
- Section progression

**Browser Console**:
```javascript
// Check current section
console.log(document.querySelector('[data-section-id]'));

// Check form data
console.log(new FormData(document.querySelector('form')));
```

**Django Debug Toolbar** (if installed):
```python
# View queries and section navigation logic
# Check BranchEvaluator calls
# Verify rule evaluation order
```

---

## Troubleshooting

### Problem: Branch Rule Not Triggering

**Symptoms**: User answers match condition but doesn't branch

**Checks**:
1. **Exact value match**
   ```
   Condition Value: "Yes"
   User Answer: "yes " (extra space)
   → Won't match!
   ```
   Solution: Values are trimmed and case-insensitive, but check for typos

2. **Wrong operator**
   ```
   Operator: equals
   Condition Value: "Product A"
   User Answer: "Product A and B"
   → Won't match!
   ```
   Solution: Use `contains` operator

3. **Question not answered yet**
   ```
   Rule on Section 1
   Condition Question from Section 2
   → Can't evaluate!
   ```
   Solution: Only reference questions from current or previous sections

4. **Higher priority rule matched first**
   ```
   Rule 1 (Priority 0): Any answer → Section X
   Rule 2 (Priority 1): Specific answer → Section Y
   → Rule 2 never reached!
   ```
   Solution: Reorder priorities

**Debug**:
```python
# In Django shell
from djf_surveys.models import BranchRule, Section
from djf_surveys.branch_logic import BranchEvaluator

section = Section.objects.get(id=1)
evaluator = BranchEvaluator(section)

# Simulate user answers
answers = {1: "No", 2: "test@example.com"}
next_section = evaluator.evaluate(answers)
print(f"Next section: {next_section}")
```

### Problem: Circular Loop Warning

**Symptoms**: Admin shows validation error about circular references

**Example**:
```
Section A → Branch to Section B (when X)
Section B → Branch to Section A (when Y)
```

**Solution**: Redesign flow to avoid loops:
```
Section A → Branch to Section B (when X)
Section B → Branch to Section C (when Y)
Section C → End or next sequential
```

### Problem: Unreachable Section

**Symptoms**: Section never shown to any users

**Cause**: No path leads to it

**Example**:
```
Section 1 → Branches to Section 3 or 4
Section 2 → Never referenced in any rule
```

**Solution**: 
- Add branch rule to reach Section 2
- Or delete Section 2 if not needed

### Problem: Wrong Section Shown

**Symptoms**: Jumps to unexpected section

**Checks**:
1. Verify rule priority (lower = higher priority)
2. Check operator type
3. Verify condition value format
4. Test with exact user input

### Problem: Can't Delete Section

**Symptoms**: "Cannot delete section with existing questions"

**Solution**:
1. Go to Questions admin
2. Filter by section
3. Delete all questions (or reassign to another section)
4. Then delete section

### Problem: Progress Bar Incorrect

**Symptoms**: Shows wrong completion percentage

**Cause**: Branch logic makes total sections variable

**Note**: This is expected behavior. Progress calculated as:
```
current_section_position / total_sections * 100
```

But branching changes the path, so may not be accurate.

**Solution**: Progress bar shows position in overall survey, not personalized path. This is a known limitation.

---

## Best Practices

### 1. Plan Before Building

**Draw a flowchart**:
```
[Start] → [Section 1: Screening]
            ↓
    Qualified? (Yes/No)
      ↓           ↓
    [Yes]        [No] → [End]
      ↓
  [Section 2: Details]
      ↓
  [Section 3: Feedback]
      ↓
    [End]
```

### 2. Use Clear Section Names

❌ Bad:
- Section 1
- Section 2
- Section 3

✅ Good:
- Personal Information
- Product Feedback
- Additional Comments

### 3. Logical Ordering Numbers

Use increments of 10:
- Section ordering: 10, 20, 30, 40
- Question ordering: 10, 20, 30, 40

**Benefit**: Easy to insert new items:
- New section between 10 and 20 → use 15
- New question between 10 and 20 → use 15

### 4. Document Branch Rules

Add comments in section descriptions:

```
Description: Product selection section

BRANCH RULES:
- If Product A → Section 3a (ordering 31)
- If Product B → Section 3b (ordering 32)
- If Product C → Section 3c (ordering 33)
```

### 5. Test Incrementally

Don't build entire survey then test. Instead:
1. Create 2 sections + questions → test
2. Add 1 branch rule → test
3. Add more sections → test
4. Add more rules → test

### 6. Use Descriptive Condition Values

Match exactly what users see:

```
Question: Are you satisfied?
Choices: Very Satisfied, Satisfied, Neutral, Dissatisfied, Very Dissatisfied

Branch Rule:
  Condition Value: Very Satisfied
  ✅ Matches choice exactly
```

### 7. Handle Edge Cases

Consider:
- What if optional question not answered?
- What if no rules match? (falls through to next section)
- What if last section branches? (can go to end)

### 8. Keep It Simple

**Start simple**:
- Linear survey first
- Add sections gradually
- Add branching only if truly needed

**Avoid**:
- Too many branches (confusing for users)
- Deep nesting (hard to maintain)
- Complex dependencies (hard to test)

### 9. Version Control

Before major changes:
1. Export survey structure (document it)
2. Test in staging environment
3. Have rollback plan

### 10. User Experience

- Keep sections focused (5-10 questions max)
- Clear section names and descriptions
- Progress indicator visible
- Allow going back
- Save draft option for long surveys

---

## Advanced Topics

### Dynamic Question Visibility (Workaround)

Current limitation: Can't hide/show individual questions based on answers within same section.

**Workaround**: Use sections as question groups:

```
Section 2: Main Questions
Section 2a: Follow-up (if answered "Yes" to Q5)
Section 3: Continue...

Branch rule on Section 2:
  If Q5 = "Yes" → Section 2a
  Otherwise → Section 3
```

### Convergence Points

After parallel branches, bring users back together:

```
Section 1 → Branches to A, B, or C
Sections A, B, C → All lead to Section 4 (convergence)
```

**Implementation**: No rules needed on A, B, C. They naturally flow to Section 4 by ordering.

### Conditional Endings

End survey early based on answers:

```
Branch Rule:
  Condition: Disqualified
  Next Section: (empty)
  → Ends survey immediately
```

### Complex Boolean Logic

Current limitation: No AND/OR combinations.

**Workaround**: Use priority and multiple rules:

```
Condition: (Age = "18-30" OR Age = "31-50") AND Product = "A"

Implement as:
Section 1: Age selection
Section 2: Product selection (only if age matches)

Branch on Section 1:
  If Age in "18-30, 31-50" → Section 2
  Otherwise → End

Branch on Section 2:
  If Product = "A" → Section 3
  Otherwise → End
```

---

## Summary

### Quick Reference

**Creating Sections**:
1. Admin → Surveys → Edit → Sections inline
2. Add sections with ordering
3. Save

**Adding Questions**:
1. Admin → Questions → Add
2. Select survey and section
3. Configure question
4. Save

**Branch Rules**:
1. Admin → Sections → Edit section
2. Scroll to Branch Rules inline
3. Add rule with condition and target
4. Set priority
5. Save

**Testing**:
1. Fill survey with different answer combinations
2. Verify correct sections shown
3. Check responses in admin
4. Test edge cases

### Key Points

✅ Sections organize questions into pages
✅ Branch rules enable conditional navigation
✅ Priority determines rule evaluation order
✅ First matching rule wins
✅ No match = proceed sequentially
✅ Empty next_section = end survey
✅ Test thoroughly before launch

---

## Need Help?

- **Technical Docs**: See `BRANCH_LOGIC_GUIDE.md` for implementation details
- **User Guide**: See `README.md` for user-facing documentation
- **Security**: See `SECURITY_REVIEW.md` for security considerations
- **Code**: See `djf_surveys/branch_logic.py` for technical implementation

**Support Contacts**:
- Developer: [your-email]
- Documentation: [docs-link]
- Issue Tracker: [issues-link]
