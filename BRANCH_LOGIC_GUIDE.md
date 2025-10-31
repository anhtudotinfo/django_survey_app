# Survey Branch Logic Guide

## Overview

Branch Logic allows surveys to dynamically route users to different sections based on their answers. This enables complex survey flows such as:

- **Skip Logic**: Skip sections based on answers (e.g., "If No, skip to section 5")
- **Conditional Paths**: Different question paths for different user types
- **Early Termination**: End survey early based on qualifying answers
- **Adaptive Surveys**: Show relevant sections based on previous responses

## How It Works

### Core Concepts

1. **Sections**: Surveys are divided into logical sections (pages)
2. **Branch Rules**: Define conditions that determine which section to show next
3. **Evaluation**: After completing a section, rules are evaluated in priority order
4. **Navigation**: First matching rule determines next section, otherwise proceeds sequentially

### Rule Evaluation Flow

```
User completes Section A
    ↓
Evaluate Branch Rules (ordered by priority)
    ↓
Match found? → Navigate to specified section
    ↓
No match? → Navigate to next sequential section
```

## Branch Rule Components

### 1. Condition Question
The question whose answer will be evaluated. Must be from the current or a previous section.

### 2. Condition Operator
How to compare the user's answer:

| Operator | Description | Example |
|----------|-------------|---------|
| **equals** | Exact match (case-insensitive) | Answer = "Yes" |
| **not_equals** | Does not match | Answer ≠ "No" |
| **contains** | Answer contains text | Answer contains "agree" |
| **in** | Answer is in list | Answer in ["Small", "Medium", "Large"] |

### 3. Condition Value
The value to compare against. For the `in` operator, use comma-separated values:
```
Small, Medium, Large
```

### 4. Next Section
Which section to navigate to if the condition matches:
- **Select a Section**: Jump to that section
- **Leave Empty**: End the survey immediately

### 5. Priority
Order of evaluation (lower numbers = higher priority):
- Priority 0 is evaluated first
- Priority 1 is evaluated second, etc.
- First matching rule wins, subsequent rules are ignored

## Configuration Examples

### Example 1: Simple Skip Logic

**Scenario**: If user is under 18, skip directly to final section

```
Section: Demographics
Question: "What is your age?"
Type: Number

Branch Rule:
- Condition Question: "What is your age?"
- Operator: less_than
- Condition Value: 18
- Next Section: Final Section
- Priority: 0
```

### Example 2: Multiple Conditions

**Scenario**: Different paths for different user types

```
Section: User Type
Question: "What type of user are you?"
Type: Radio
Choices: Individual, Business, Enterprise

Branch Rules:
Priority 0:
- Condition: User Type equals "Individual"
- Next Section: Individual Questions

Priority 1:
- Condition: User Type equals "Business"
- Next Section: Business Questions

Priority 2:
- Condition: User Type equals "Enterprise"
- Next Section: Enterprise Questions
```

### Example 3: Disqualification Logic

**Scenario**: End survey if user doesn't meet criteria

```
Section: Screening
Question: "Do you own a car?"
Type: Radio
Choices: Yes, No

Branch Rule:
- Condition Question: "Do you own a car?"
- Operator: equals
- Condition Value: No
- Next Section: (Leave empty - ends survey)
- Priority: 0
```

### Example 4: Contains Operator

**Scenario**: Branch based on text content

```
Section: Feedback
Question: "What did you like about our service?"
Type: Text Area

Branch Rule:
- Condition Question: "What did you like about our service?"
- Operator: contains
- Condition Value: support
- Next Section: Support Feedback Section
- Priority: 0
```

### Example 5: In Operator (Multiple Values)

**Scenario**: Same next section for multiple answers

```
Section: Location
Question: "Which region are you from?"
Type: Select
Choices: North, South, East, West

Branch Rule:
- Condition Question: "Which region are you from?"
- Operator: in
- Condition Value: North, South
- Next Section: Northern/Southern Survey Path
- Priority: 0
```

## Best Practices

### 1. Plan Your Flow First
Draw a flowchart of your survey before creating rules:
```
[Start] → [Demographics] → [Screening]
                               ↓
                    Yes ← Qualified? → No → [End]
                     ↓
                [Main Survey] → [End]
```

### 2. Use Clear Priorities
- Number rules in increments of 10 (0, 10, 20) to allow insertions later
- Document why each priority is set

### 3. Test All Paths
- Test each possible answer combination
- Verify no infinite loops
- Ensure all paths reach either end or next section

### 4. Avoid Circular References
**DON'T** create rules that can loop:
```
Section A → Branch to Section B (when X)
Section B → Branch to Section A (when Y)
```
This can create infinite loops.

### 5. Question Placement
- Place condition questions in current or previous sections only
- Cannot branch based on questions that haven't been answered yet

### 6. Fallback Behavior
- Always have a default sequential path
- Only matching rules trigger branches
- If no rules match, survey proceeds to next section naturally

## Validation Rules

The system automatically validates:

1. **No Forward References**: Condition questions must be answered before evaluation
2. **No Self-Loops**: Cannot branch to the same section
3. **Same Survey**: Next section must belong to same survey
4. **No Circular Paths**: System warns about potential circular references

## Debugging Tips

### Rule Not Triggering?
1. Check the answer format matches condition value exactly
2. Remember comparisons are case-insensitive but whitespace matters
3. Verify the question is actually in the current/previous section
4. Check rule priority - a higher priority rule may be matching first

### Wrong Section Shown?
1. Check rule priority order
2. Verify operator type (equals vs contains vs in)
3. Look for conflicting rules with higher priority

### Circular Loop Detected?
1. Review all rules in affected sections
2. Draw a flow diagram to visualize paths
3. Remove or adjust rules creating the loop

## Admin Interface

### Creating Branch Rules

1. Navigate to **Admin → Sections**
2. Click on the section where you want to add rules
3. Scroll to **Branch Rules** inline section
4. Click **Add another Branch rule**
5. Fill in:
   - Condition Question
   - Operator
   - Condition Value
   - Next Section (or leave empty to end survey)
   - Priority
6. Save

### Viewing All Rules

- Admin → Branch Rules (for global overview)
- Or view inline within each Section

## Technical Implementation

### BranchEvaluator Class

Located in `djf_surveys/branch_logic.py`, this class handles rule evaluation:

```python
from djf_surveys.branch_logic import BranchEvaluator

# Evaluate rules for a section
evaluator = BranchEvaluator(current_section)
next_section = evaluator.evaluate(user_answers)

if next_section:
    # Branch to next_section
elif next_section is None:
    # End survey
else:
    # No match, proceed sequentially
```

### Integration Points

- **Forms**: Rules evaluated during form submission
- **Views**: `SectionNavigator` class integrates branch logic
- **Templates**: Progress indicators account for potential branches

## Performance Considerations

- Rules are fetched with `select_related` to minimize queries
- Evaluation is O(n) where n = number of rules per section
- Cached section queries reduce database load
- Index on `section` and `priority` fields optimizes lookups

## Migration from Non-Branching Surveys

Existing surveys without branches work unchanged:
1. All questions treated as one implicit section
2. No branch rules = sequential navigation
3. Add sections and rules gradually
4. Test each addition before deployment

## Limitations

Current implementation limits:
- Maximum ~1000 rules per section (practical limit)
- No complex boolean logic (AND/OR combinations)
- No numeric comparisons (>, <, >=, <=) - must use custom operators
- No regex pattern matching

For complex logic needs, consider:
- Breaking into multiple simpler rules
- Using priority ordering creatively
- Custom validators in Question model

## Further Reading

- **Admin Guide**: See `ADMIN_GUIDE.md` for setup instructions
- **Draft System**: See `DRAFT_SYSTEM_GUIDE.md` for save/resume with branching
- **Testing**: See `test_implementation.py` for example test cases
- **Code**: See `djf_surveys/branch_logic.py` for implementation details
