# Quick Setup for Payroll Entry

## The Issue

When creating salary slips from **Payroll Entry**, deductions don't show up even though:
- ✅ Designation has deduction amounts configured
- ✅ Salary Structure has the salary components
- ✅ Attendance records exist

## The Solution

You need **TWO Server Scripts** (not one!) because Payroll Entry uses a different event lifecycle than manual creation.

---

## Step 1: Create "Before Insert" Server Script

This handles **Payroll Entry** bulk creation.

**Go to:** Customization > Server Script > New

**Settings:**
- **Name:** `Salary Slip Deductions - Before Insert`
- **DocType:** `Salary Slip`
- **Event:** `Before Insert`
- **Enabled:** ✓

**Script:**
```python
# This runs when salary slips are created via Payroll Entry
calculate_and_add_deductions = frappe.get_attr('fours_customizations.salary_slip_handler.calculate_and_add_deductions')
calculate_and_add_deductions(doc)
```

Click **Save**.

---

## Step 2: Create "Before Save" Server Script

This handles **manual** salary slip creation.

**Go to:** Customization > Server Script > New

**Settings:**
- **Name:** `Salary Slip Deductions - Before Save`
- **DocType:** `Salary Slip`
- **Event:** `Before Save`
- **Enabled:** ✓

**Script:**
```python
# This runs when salary slips are saved manually
if doc.docstatus == 0:  # Only for draft
    calculate_and_add_deductions = frappe.get_attr('fours_customizations.salary_slip_handler.calculate_and_add_deductions')
    calculate_and_add_deductions(doc)
```

Click **Save**.

---

## Step 3: Test with Payroll Entry

1. **Go to:** HR > Payroll Entry
2. Click **New**
3. Fill in:
   - **Company:** Your company
   - **Payroll Frequency:** Monthly
   - **Start Date:** 2025-11-01
   - **End Date:** 2025-11-30
   - **Posting Date:** 2025-11-09
   - **Payment Account:** Your payment account
4. Click **Get Employees**
5. Click **Create Salary Slips**
6. **Check the created salary slips** - they should have:
   - Deductions based on actual attendance violations
   - Overtime earnings (if employees worked overtime)

---

## How It Works

### Event Flow for Payroll Entry:

```
Payroll Entry "Create Salary Slips"
  ↓
For each employee:
  ↓
  Create Salary Slip document
  ↓
  Load salary structure → earnings/deductions from structure
  ↓
  🔵 BEFORE INSERT EVENT FIRES ← Your script runs here
  ↓
  Script counts attendance violations
  ↓
  Script adds deduction amounts to slip
  ↓
  Script calculates overtime
  ↓
  Insert salary slip to database
  ↓
  🔵 BEFORE SAVE EVENT FIRES ← Backup (in case insert didn't run)
  ↓
  Save to database
```

### Why You Need Both Scripts:

- **Before Insert** - Runs when Payroll Entry creates slips in bulk
- **Before Save** - Runs when manually creating/editing slips
- Having both ensures it works in all scenarios

---

## Troubleshooting

### Issue: Deductions still not showing

**Check 1: Are both Server Scripts created and enabled?**
```
Go to: Customization > Server Script
Search: "Salary Slip Deductions"
Expected: 2 scripts (Before Insert + Before Save)
```

**Check 2: Do attendance records have violations marked?**

For ERPNext to count violations, attendance must have:
- **Absences:** `status = 'Absent'`
- **Late arrivals:** `late_entry = 1` (checkbox checked)
- **Early exits:** `early_exit = 1` (checkbox checked)
- **No checkout:** `out_time` is blank/null

**Check 3: Are attendance records submitted?**

Only submitted attendance (docstatus = 1) is counted.

**Check 4: Does the designation have rates configured?**

Go to the employee's Designation and verify:
- Absent Deduction: > 0
- Late Deduction: > 0
- Early Exit Deduction: > 0
- No Checkout Deduction: > 0

---

## Manual Testing

### Test the calculation function:

```bash
bench --site YOUR_SITE console
```

```python
from fours_customizations.salary_slip_handler import get_attendance_summary
from frappe.utils import today, get_first_day, get_last_day

# Test for a specific employee
summary = get_attendance_summary(
    employee='HR-EMP-00108',  # Replace with your employee ID
    start_date='2025-11-01',
    end_date='2025-11-30'
)

print("\n=== ATTENDANCE SUMMARY ===")
print(f"Employee: {summary['employee_name']}")
print(f"Designation: {summary['designation']}")
print(f"\nViolations:")
print(f"  Absences: {summary['violations']['absent']['count']} × {summary['violations']['absent']['rate']:,.0f} = {summary['violations']['absent']['amount']:,.0f}")
print(f"  Late: {summary['violations']['late']['count']} × {summary['violations']['late']['rate']:,.0f} = {summary['violations']['late']['amount']:,.0f}")
print(f"  Early Exit: {summary['violations']['early_exit']['count']} × {summary['violations']['early_exit']['rate']:,.0f} = {summary['violations']['early_exit']['amount']:,.0f}")
print(f"  No Checkout: {summary['violations']['no_checkout']['count']} × {summary['violations']['no_checkout']['rate']:,.0f} = {summary['violations']['no_checkout']['amount']:,.0f}")
print(f"\nTotal Deductions: {summary['total_deductions']:,.0f}")
```

If this shows correct values but the salary slip doesn't, then the Server Scripts aren't running.

---

## Key Points

1. ✅ **Always use Payroll Entry** for bulk salary slip creation
2. ✅ **Mark attendance violations** using the checkboxes (late_entry, early_exit)
3. ✅ **Submit attendance** before creating salary slips
4. ✅ **Configure designation rates** for each job role
5. ✅ **Create BOTH Server Scripts** (Before Insert + Before Save)
6. ✅ **Test with one employee first** before processing entire payroll

---

## Success Indicators

When everything is working correctly, you should see:

**In Salary Slip:**
```
EARNINGS:
  + Basic Salary: 1,000,000
  + Designation Overtime Pay: 24,000  ← Added automatically
  = Gross Pay: 1,024,000

DEDUCTIONS:
  - Absent Deduction: 10,000  ← Added automatically (if absent)
  - Late Deduction: 5,000     ← Added automatically (if late)
  - Early Exit Deduction: 5,000  ← Added automatically (if early exit)
  = Total Deduction: 20,000

NET PAY: 1,004,000
```

If you see these automatically, **it's working!** 🎉
