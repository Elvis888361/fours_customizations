# FINAL Server Script Setup - WORKING VERSION

## The Correct Import Method

After testing, the **ONLY** way that works in ERPNext Server Scripts is:

```python
import fours_customizations.salary_slip_handler as handler
handler.calculate_and_add_deductions(doc)
```

---

## Create These Two Server Scripts

### Script 1: For Payroll Entry (Before Insert)

**Navigation:** Customization > Server Script > New

**Settings:**
- **Name:** `Salary Slip Deductions - Before Insert`
- **DocType:** `Salary Slip`
- **Event:** `Before Insert`
- **Enabled:** ✓ (checked)

**Script (copy exactly):**
```python
# This runs when salary slips are created via Payroll Entry
import fours_customizations.salary_slip_handler as handler
handler.calculate_and_add_deductions(doc)
```

Click **Save**.

---

### Script 2: For Manual Creation (Before Save)

**Navigation:** Customization > Server Script > New

**Settings:**
- **Name:** `Salary Slip Deductions - Before Save`
- **DocType:** `Salary Slip`
- **Event:** `Before Save`
- **Enabled:** ✓ (checked)

**Script (copy exactly):**
```python
# This runs when salary slips are saved manually
if doc.docstatus == 0:  # Only for draft
    import fours_customizations.salary_slip_handler as handler
    handler.calculate_and_add_deductions(doc)
```

Click **Save**.

---

## Test Immediately

After creating both scripts:

1. **Go to:** HR > Payroll Entry
2. Create a new Payroll Entry
3. Fill in the details (company, dates, etc.)
4. Click **Get Employees**
5. Click **Create Salary Slips**
6. **Open one of the created salary slips**

You should now see:
- **Deductions** based on attendance violations
- **Overtime Pay** in earnings (if applicable)

---

## Expected Result

When you open a salary slip after running Payroll Entry, you should see:

```
EARNINGS:
  + Basic Salary: 1,000,000 UGX
  + Designation Overtime Pay: XX,XXX UGX (if employee worked overtime)
  = Gross Pay: X,XXX,XXX UGX

DEDUCTIONS:
  - Absent Deduction: XX,XXX UGX (if employee was absent)
  - Late Deduction: XX,XXX UGX (if employee was late)
  - Early Exit Deduction: XX,XXX UGX (if employee left early)
  - No Checkout Deduction: XX,XXX UGX (if employee didn't checkout)
  = Total Deductions: XX,XXX UGX

NET PAY: X,XXX,XXX UGX
```

---

## Troubleshooting

### Issue: Still getting ImportError

**Solution:** Make sure you copied the script EXACTLY as shown above. The format must be:
```python
import fours_customizations.salary_slip_handler as handler
handler.calculate_and_add_deductions(doc)
```

Do NOT use:
- ❌ `from fours_customizations.salary_slip_handler import ...`
- ❌ `frappe.get_attr(...)`

### Issue: No deductions showing

**Check these:**

1. **Are both Server Scripts created and enabled?**
   - Go to Customization > Server Script
   - You should see 2 scripts with "Salary Slip Deductions" in the name
   - Both must be enabled (checkbox checked)

2. **Does the employee have a designation?**
   - Go to HR > Employee
   - Check that the employee has a designation assigned

3. **Does the designation have rates configured?**
   - Go to HR > Designation
   - Open the employee's designation
   - Check that deduction amounts are greater than 0

4. **Are attendance records submitted?**
   - Go to HR > Attendance
   - Filter by the employee
   - Check that attendance is submitted (docstatus = 1)
   - For late/early exit, check that the checkboxes are checked

5. **Are attendance violations marked?**
   - **Absences:** Status = "Absent"
   - **Late:** late_entry checkbox checked
   - **Early Exit:** early_exit checkbox checked
   - **No Checkout:** out_time is blank

---

## Quick Console Test

To verify the calculation logic is working:

```bash
bench --site YOUR_SITE console
```

```python
from fours_customizations.salary_slip_handler import get_attendance_summary

summary = get_attendance_summary(
    employee='HR-EMP-00108',  # Replace with your employee ID
    start_date='2025-11-01',
    end_date='2025-11-30'
)

print(f"Total Deductions: {summary['total_deductions']:,.0f}")
print(f"Violations: {summary['violations']}")
```

If this shows correct values but salary slip doesn't, the Server Scripts aren't running properly.

---

## Success!

When everything is working:
- ✅ Salary slips created via Payroll Entry have automatic deductions
- ✅ Deductions match attendance violations
- ✅ Overtime is calculated and added automatically
- ✅ No manual intervention needed

You're done! 🎉
