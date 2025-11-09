# Server Script ImportError Fix

## The Error

```
ImportError: __import__ not found
```

This happens because ERPNext Server Scripts don't allow `from...import` statements for security reasons.

## ❌ WRONG (These cause errors):

```python
# This doesn't work - 'from...import' not allowed
from fours_customizations.salary_slip_handler import calculate_and_add_deductions
calculate_and_add_deductions(doc)
```

```python
# This doesn't work either - 'frappe.get_attr' doesn't exist
calculate_and_add_deductions = frappe.get_attr('fours_customizations.salary_slip_handler.calculate_and_add_deductions')
calculate_and_add_deductions(doc)
```

## ✅ CORRECT (Use this instead):

```python
# Import the module, then call the function
import fours_customizations.salary_slip_handler as handler
handler.calculate_and_add_deductions(doc)
```

---

## Updated Server Scripts

### Script 1: Before Insert (for Payroll Entry)

**Go to:** Customization > Server Script > New (or edit existing)

**Settings:**
- **Name:** `Salary Slip Deductions - Before Insert`
- **DocType:** `Salary Slip`
- **Event:** `Before Insert`
- **Enabled:** ✓

**Script:**
```python
# This runs when salary slips are created via Payroll Entry
import fours_customizations.salary_slip_handler as handler
handler.calculate_and_add_deductions(doc)
```

Click **Save**.

---

### Script 2: Before Save (for Manual Creation)

**Go to:** Customization > Server Script > New (or edit existing)

**Settings:**
- **Name:** `Salary Slip Deductions - Before Save`
- **DocType:** `Salary Slip`
- **Event:** `Before Save`
- **Enabled:** ✓

**Script:**
```python
# This runs when salary slips are saved manually
if doc.docstatus == 0:  # Only for draft
    import fours_customizations.salary_slip_handler as handler
    handler.calculate_and_add_deductions(doc)
```

Click **Save**.

---

## Test It Now

1. **Delete old Server Scripts** with the `from...import` syntax (if any exist)
2. **Create the two scripts above** with `frappe.get_attr()`
3. **Go to Payroll Entry** and create salary slips
4. **Check the salary slips** - deductions should now appear!

---

## Why This Works

- `frappe.get_attr()` is a safe way to load functions from custom apps in Server Scripts
- It bypasses the import restrictions while still loading your custom code
- Both scripts will now run without ImportError

---

## Next Steps

After fixing the scripts, test by creating a salary slip via Payroll Entry. You should see:

```
DEDUCTIONS:
  - Absent Deduction: (amount based on attendance)
  - Late Deduction: (amount based on attendance)
  - Early Exit Deduction: (amount based on attendance)
  - No Checkout Deduction: (amount based on attendance)
```

If you still don't see deductions, check [PAYROLL_ENTRY_SETUP.md](PAYROLL_ENTRY_SETUP.md) for troubleshooting steps.
