# Quick Setup Guide for Fours Customizations

## The Problem You're Facing

When you create a salary slip, **the deductions don't show up even though**:
- ✅ You set the deduction amounts in the Designation
- ✅ You added the salary components to the Salary Structure
- ✅ You recorded attendance as Absent/Present

## Why This Happens

ERPNext's Salary Slip **doesn't automatically calculate** deductions based on attendance. You need to:

1. **Mark attendance violations** in the Attendance records (late_entry, early_exit checkboxes)
2. **Create a Server Script** to count violations and calculate deductions

---

## Complete Setup Steps

### Step 1: Install the App (Already Done)

```bash
bench get-app https://github.com/Elvis888361/fours_customizations.git
bench --site YOUR_SITE install-app fours_customizations
```

### Step 2: Configure Designation with Deduction Rates

Go to **HR > Designation** and set amounts:

```
Attendance Deductions Section:
  ✓ Absent Deduction: 10,000
  ✓ Late Deduction: 5,000
  ✓ Early Exit Deduction: 5,000
  ✓ No Checkout Deduction: 5,000

Overtime Configuration Section:
  ✓ Overtime Start Time: 17:00:00
  ✓ Overtime End Time: 22:00:00
  ✓ Overtime Hourly Rate: 8,000
```

### Step 3: Add Salary Components to Salary Structure

Go to **HR > Salary Structure** and add these components with **amount = 0**:

**Earnings:**
- Basic Salary (your existing amount)
- **Designation Overtime Pay** (0)

**Deductions:**
- **Absent Deduction** (0)
- **Late Deduction** (0)
- **Early Exit Deduction** (0)
- **No Checkout Deduction** (0)

**Important:** Set amounts to 0 - they will be calculated automatically!

### Step 4: Assign Salary Structure to Employee

Go to **HR > Salary Structure Assignment** and create:

- Employee: Select your employee
- Salary Structure: Select the structure you configured
- From Date: Start date
- Base: Employee's base salary

### Step 5: Create Server Script (THIS IS THE CRITICAL STEP!)

**Without this, deductions will NOT calculate automatically!**

1. Go to **Customization > Server Script**
2. Click **New**
3. Fill in:

```
Name: Calculate Salary Deductions
DocType: Salary Slip
Event: Before Save
Enabled: ✓ (checked)
```

4. **Copy this script EXACTLY:**

```python
if doc.docstatus == 0:  # Only for draft salary slips
    from fours_customizations.salary_slip_handler import calculate_and_add_deductions
    calculate_and_add_deductions(doc)
```

5. Click **Save**

### Step 6: Record Attendance with Violations

When recording attendance, you need to:

#### For Absences:
- **Status:** Absent
- The Server Script will count these automatically

#### For Late Arrivals:
- **Status:** Present or Half Day
- **Late Entry:** ✓ (check this box)
- Or set **In Time** after shift start time (if auto-marking is enabled)

#### For Early Exits:
- **Status:** Present or Half Day
- **Early Exit:** ✓ (check this box)
- Or set **Out Time** before shift end time (if auto-marking is enabled)

#### For No Checkout:
- **Status:** Present or Half Day
- **In Time:** Set check-in time
- **Out Time:** Leave blank (don't set checkout time)

#### For Overtime:
- **Status:** Present
- **In Time:** Normal check-in (e.g., 08:00:00)
- **Out Time:** After overtime start time (e.g., 20:00:00 for 3 hours overtime)

**Example Attendance Records:**

```
Date       Status      In Time    Out Time   Late Entry  Early Exit
----------------------------------------------------------------------
Nov 1      Absent      -          -          -           -
Nov 2      Present     08:00      17:00      -           -
Nov 3      Present     09:30      17:00      ✓           -
Nov 4      Present     08:00      15:00      -           ✓
Nov 5      Present     08:00      -          -           -
Nov 6      Present     08:00      20:00      -           -
```

**This will result in:**
- 1 Absent × 10,000 = 10,000 deduction
- 1 Late × 5,000 = 5,000 deduction
- 1 Early Exit × 5,000 = 5,000 deduction
- 1 No Checkout × 5,000 = 5,000 deduction
- 3 hours overtime × 8,000 = 24,000 earning

### Step 7: Create Salary Slip

Now when you create a salary slip:

1. Go to **HR > Salary Slip**
2. Click **New**
3. Select **Employee**
4. Set **Posting Date** and **Period** (Start Date / End Date)
5. Click **"Get Earnings and Deductions"** button
   - This loads the salary structure components
6. **The Server Script will automatically run and:**
   - Count attendance violations from attendance records
   - Calculate deduction amounts based on designation rates
   - Add overtime earnings (if configured)
   - Update totals
7. Click **Save**

**Important:** You MUST click "Get Earnings and Deductions" first before saving. The Server Script only runs after the salary structure has been loaded.

---

## Verification Checklist

Before creating a salary slip, verify:

- [ ] Designation has deduction amounts configured
- [ ] Salary Structure has all 5 salary components (with amount = 0)
- [ ] Employee has Salary Structure Assignment
- [ ] **Server Script is created and enabled** ← MOST IMPORTANT!
- [ ] Attendance records are submitted (docstatus = 1)
- [ ] Attendance violations are marked (late_entry, early_exit checkboxes)

---

## Troubleshooting

### Problem: No deductions showing in salary slip

**Solution:**

1. **Check if Server Script exists:**
   - Go to **Customization > Server Script**
   - Search for "Salary"
   - Verify the script exists and is **Enabled**

2. **Check if Server Script has errors:**
   - Open the Server Script
   - Click **Test** button
   - If there are errors, check the error log

3. **Check attendance records:**
   ```python
   # Run in bench console
   bench --site YOUR_SITE console

   import frappe
   att = frappe.get_all('Attendance',
       filters={'employee': 'HR-EMP-00001', 'attendance_date': '2025-11-05'},
       fields=['status', 'late_entry', 'early_exit', 'out_time'])
   print(att)
   ```

4. **Manually test the calculation:**
   ```python
   # Run in bench console
   from fours_customizations.salary_slip_handler import get_attendance_summary

   summary = get_attendance_summary(
       employee='HR-EMP-00001',
       start_date='2025-11-01',
       end_date='2025-11-30'
   )

   print(summary)
   ```

5. **Check designation configuration:**
   ```python
   # Run in bench console
   import frappe
   designation = frappe.get_doc('Designation', 'Manager')
   print(f"Absent: {designation.absent_deduction}")
   print(f"Late: {designation.late_deduction}")
   print(f"Early Exit: {designation.early_exit_deduction}")
   print(f"No Checkout: {designation.no_checkout_deduction}")
   ```

### Problem: Overtime not calculating

**Solution:**

1. Check designation has overtime configuration:
   - Overtime Start Time (e.g., 17:00:00)
   - Overtime End Time (e.g., 22:00:00)
   - Overtime Hourly Rate (e.g., 8000)

2. Check attendance has **out_time** (checkout time) after overtime_start_time

3. Check attendance is **submitted** (docstatus = 1)

---

## How the Calculation Works

### Deduction Calculation:

1. Server Script runs **before_save** on Salary Slip
2. Fetches all **submitted** attendance for the salary period
3. Counts violations:
   - `status == 'Absent'` → absent_count
   - `late_entry == 1` → late_count
   - `early_exit == 1` → early_exit_count
   - `out_time is None and status in ['Present', 'Half Day']` → no_checkout_count
4. Calculates amounts:
   - `absent_count × designation.absent_deduction`
   - `late_count × designation.late_deduction`
   - `early_exit_count × designation.early_exit_deduction`
   - `no_checkout_count × designation.no_checkout_deduction`
5. Adds deduction rows to salary slip
6. Recalculates totals

### Overtime Calculation:

1. For each attendance with `out_time`:
2. If `out_time > overtime_start_time`:
   - Calculate hours: `min(out_time, overtime_end_time) - overtime_start_time`
   - Calculate amount: `hours × designation.overtime_hourly_rate`
3. Sum all overtime and add to earnings

---

## Testing with Console Commands

### Create test attendance with violations:

```python
bench --site YOUR_SITE console

import frappe
from frappe.utils import today, add_days, get_datetime

employee_id = 'HR-EMP-00001'  # Replace with your employee ID

# Absence
att1 = frappe.get_doc({
    'doctype': 'Attendance',
    'employee': employee_id,
    'attendance_date': add_days(today(), -5),
    'status': 'Absent',
    'company': 'Your Company'
})
att1.insert()
att1.submit()

# Late entry
att2 = frappe.get_doc({
    'doctype': 'Attendance',
    'employee': employee_id,
    'attendance_date': add_days(today(), -4),
    'status': 'Present',
    'in_time': get_datetime(f"{add_days(today(), -4)} 09:30:00"),  # Late
    'out_time': get_datetime(f"{add_days(today(), -4)} 17:00:00"),
    'late_entry': 1,  # Mark as late
    'company': 'Your Company'
})
att2.insert()
att2.submit()

# Early exit
att3 = frappe.get_doc({
    'doctype': 'Attendance',
    'employee': employee_id,
    'attendance_date': add_days(today(), -3),
    'status': 'Present',
    'in_time': get_datetime(f"{add_days(today(), -3)} 08:00:00"),
    'out_time': get_datetime(f"{add_days(today(), -3)} 15:00:00"),  # Early
    'early_exit': 1,  # Mark as early exit
    'company': 'Your Company'
})
att3.insert()
att3.submit()

# No checkout
att4 = frappe.get_doc({
    'doctype': 'Attendance',
    'employee': employee_id,
    'attendance_date': add_days(today(), -2),
    'status': 'Present',
    'in_time': get_datetime(f"{add_days(today(), -2)} 08:00:00"),
    # No out_time
    'company': 'Your Company'
})
att4.insert()
att4.submit()

# Overtime
att5 = frappe.get_doc({
    'doctype': 'Attendance',
    'employee': employee_id,
    'attendance_date': add_days(today(), -1),
    'status': 'Present',
    'in_time': get_datetime(f"{add_days(today(), -1)} 08:00:00"),
    'out_time': get_datetime(f"{add_days(today(), -1)} 20:00:00"),  # 3 hrs OT
    'company': 'Your Company'
})
att5.insert()
att5.submit()

frappe.db.commit()
print("✓ Test attendance created!")
```

### Test the calculation:

```python
from fours_customizations.salary_slip_handler import get_attendance_summary
from frappe.utils import today, get_first_day, get_last_day

summary = get_attendance_summary(
    employee='HR-EMP-00001',
    start_date=get_first_day(today()),
    end_date=get_last_day(today())
)

print("\n=== ATTENDANCE SUMMARY ===")
print(f"Employee: {summary['employee_name']}")
print(f"Designation: {summary['designation']}")
print(f"Period: {summary['period']}")
print(f"\nViolations:")
print(f"  Absences: {summary['violations']['absent']['count']} × {summary['violations']['absent']['rate']:,.0f} = {summary['violations']['absent']['amount']:,.0f}")
print(f"  Late: {summary['violations']['late']['count']} × {summary['violations']['late']['rate']:,.0f} = {summary['violations']['late']['amount']:,.0f}")
print(f"  Early Exit: {summary['violations']['early_exit']['count']} × {summary['violations']['early_exit']['rate']:,.0f} = {summary['violations']['early_exit']['amount']:,.0f}")
print(f"  No Checkout: {summary['violations']['no_checkout']['count']} × {summary['violations']['no_checkout']['rate']:,.0f} = {summary['violations']['no_checkout']['amount']:,.0f}")
print(f"\nTotal Deductions: {summary['total_deductions']:,.0f}")
```

---

## Summary

The **key missing step** in your setup was **Step 5: Creating the Server Script**.

Without the Server Script, ERPNext has no way to know it should:
1. Count attendance violations
2. Multiply by designation rates
3. Add deductions to the salary slip

The Server Script acts as the "bridge" between:
- Your attendance records
- Your designation configuration
- Your salary slip

**Once you create the Server Script, everything will work automatically!**
