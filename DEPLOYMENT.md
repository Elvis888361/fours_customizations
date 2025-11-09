# Deployment Guide: Fours Customizations

This guide explains how to deploy the `fours_customizations` app to a new ERPNext site.

## Pre-Deployment Checklist

### ✅ What Will Be Installed Automatically

When you run `bench --site SITE_NAME install-app fours_customizations`, the following will be created automatically:

1. **7 Custom Fields on Designation DocType**
   - Absent Deduction (Currency)
   - Late Deduction (Currency)
   - Early Exit Deduction (Currency)
   - No Checkout Deduction (Currency)
   - Overtime Start Time (Time)
   - Overtime End Time (Time)
   - Overtime Hourly Rate (Currency)

2. **5 Salary Components**
   - Absent Deduction (Deduction)
   - Late Deduction (Deduction)
   - Early Exit Deduction (Deduction)
   - No Checkout Deduction (Deduction)
   - Designation Overtime Pay (Earning)

3. **Python Module: overtime_utils.py**
   - `calculate_designation_overtime()` - Calculate overtime for a period
   - `calculate_daily_overtime()` - Calculate overtime for a single day
   - `add_designation_overtime_to_salary_slip()` - Add overtime to salary slip

### ⚠️ What You Must Configure Manually

After installation, you need to:

1. **Configure each Designation** with deduction amounts and overtime settings
2. **Add salary components to Salary Structures**
3. **Integrate with Salary Slip** (via Server Script or custom code)

---

## Installation Steps

### Step 1: Install the App

```bash
# From your bench directory
cd /path/to/frappe-bench

# Get the app from GitHub
bench get-app https://github.com/Elvis888361/fours_customizations.git

# Install on your site
bench --site YOUR_SITE install-app fours_customizations
```

**Expected Output:**
```
Installing fours_customizations...
Custom fields added to Designation doctype successfully!
✓ Created salary component: Absent Deduction
✓ Created salary component: Late Deduction
✓ Created salary component: Early Exit Deduction
✓ Created salary component: No Checkout Deduction
✓ Created salary component: Designation Overtime Pay
Salary components created successfully!
```

### Step 2: Configure Designations

Navigate to **HR > Designation** and configure each job role:

#### Example: Manager

```
Attendance Deductions Section:
  Absent Deduction: 10000
  Late Deduction: 5000
  Early Exit Deduction: 5000
  No Checkout Deduction: 5000

Overtime Configuration Section:
  Overtime Start Time: 17:00:00
  Overtime End Time: 22:00:00
  Overtime Hourly Rate: 8000
```

#### Example: Developer

```
Attendance Deductions Section:
  Absent Deduction: 8000
  Late Deduction: 4000
  Early Exit Deduction: 4000
  No Checkout Deduction: 4000

Overtime Configuration Section:
  Overtime Start Time: 18:00:00
  Overtime End Time: 23:00:00
  Overtime Hourly Rate: 6000
```

### Step 3: Update Salary Structures

Go to **HR > Salary Structure** and add the components:

#### Add to Earnings:
- Basic Salary (existing)
- **Designation Overtime Pay** (set amount to 0)

#### Add to Deductions:
- **Absent Deduction** (set amount to 0)
- **Late Deduction** (set amount to 0)
- **Early Exit Deduction** (set amount to 0)
- **No Checkout Deduction** (set amount to 0)

**Important:** Set all amounts to 0 - they will be calculated dynamically.

### Step 4: Integrate with Salary Slip (CRITICAL - REQUIRED)

**⚠️ IMPORTANT:** Without this step, deductions and overtime will NOT be calculated automatically!

You have two options:

#### Option A: Server Script (Recommended - No Code Required)

1. Go to **Customization > Server Script**
2. Click **New**
3. Fill in the details:
   - **DocType:** Salary Slip
   - **Event:** Before Save
   - **Script Type:** DocType Event
   - **Enabled:** ✓ (checked)
   - **Script:**

```python
if doc.docstatus == 0:  # Only for draft salary slips
    from fours_customizations.salary_slip_handler import calculate_and_add_deductions
    calculate_and_add_deductions(doc)
```

4. Click **Save**

**What this does:**
- Automatically counts attendance violations (absences, late arrivals, early exits, no checkouts)
- Calculates deduction amounts based on designation rates
- Adds deductions to the salary slip
- Calculates and adds overtime (if configured)
- Updates gross pay and net pay

**Important Workflow:**
1. First, click **"Get Earnings and Deductions"** button in the salary slip to load the salary structure
2. The Server Script will automatically run and add deductions/overtime
3. Save the salary slip

#### Option B: Custom App Hook (For Developers)

If you have your own custom app, add this to your `hooks.py`:

```python
doc_events = {
    "Salary Slip": {
        "before_save": "your_app.salary.calculate_salary_slip"
    }
}
```

In `your_app/salary.py`:

```python
def calculate_salary_slip(doc, method):
    if doc.docstatus == 0:
        from fours_customizations.salary_slip_handler import calculate_and_add_deductions
        calculate_and_add_deductions(doc)
```

Then restart your bench:
```bash
bench --site YOUR_SITE clear-cache
bench restart
```

---

## Verification

### Test the Installation

1. **Check Custom Fields:**
   ```bash
   bench --site YOUR_SITE execute fours_customizations.test_setup.verify_designation_fields
   ```

2. **Check Salary Components:**
   ```bash
   bench --site YOUR_SITE console
   ```
   ```python
   frappe.get_all('Salary Component',
       filters={'salary_component': ['like', '%Deduction%']},
       fields=['salary_component', 'type'])
   ```

3. **Test Overtime Calculation:**
   ```python
   from fours_customizations.overtime_utils import calculate_designation_overtime

   overtime_data = calculate_designation_overtime(
       employee='HR-EMP-00001',
       start_date='2025-11-01',
       end_date='2025-11-30'
   )

   print(overtime_data)
   ```

### Create Test Data (Optional)

```bash
# Create test designation, employee, and attendance
bench --site YOUR_SITE execute fours_customizations.test_setup.create_test_data

# Create test attendance with overtime
bench --site YOUR_SITE execute fours_customizations.test_setup.create_test_attendance_with_overtime

# Test overtime calculation
bench --site YOUR_SITE execute fours_customizations.test_setup.test_overtime_calculation
```

---

## Troubleshooting

### Issue: Custom fields not showing

**Solution:**
```bash
bench --site YOUR_SITE clear-cache
bench --site YOUR_SITE execute fours_customizations.install.create_designation_custom_fields
```

### Issue: Salary components not created

**Solution:**
```bash
bench --site YOUR_SITE execute fours_customizations.install.create_salary_components
```

### Issue: Overtime not calculating

**Checklist:**
- [ ] Designation has overtime_start_time, overtime_end_time, and overtime_hourly_rate set
- [ ] Attendance records have out_time (checkout time) populated
- [ ] Attendance records are submitted (docstatus = 1)
- [ ] Checkout time is after overtime_start_time

**Debug:**
```python
from fours_customizations.overtime_utils import calculate_designation_overtime

overtime_data = calculate_designation_overtime(
    employee='YOUR_EMPLOYEE_ID',
    start_date='2025-11-01',
    end_date='2025-11-30'
)

# Check for errors
if 'error' in overtime_data:
    print(overtime_data['error'])
elif 'note' in overtime_data:
    print(overtime_data['note'])
else:
    print(f"Total: {overtime_data['total_hours']} hrs = {overtime_data['total_amount']}")
```

---

## Uninstallation

To remove the app:

```bash
# Uninstall from site
bench --site YOUR_SITE uninstall-app fours_customizations

# Remove app files
bench remove-app fours_customizations
```

**Note:** Custom fields and salary components will remain in the database. You'll need to delete them manually if desired.

---

## Production Considerations

### Performance

- Overtime calculation runs once per salary slip creation
- For large datasets (1000+ employees), consider running overnight batch jobs
- Cache designation configurations if processing many employees

### Data Integrity

- Always use submitted attendance records (docstatus = 1)
- Validate checkout times before calculating overtime
- Log all overtime calculations for audit trail

### Scaling

For high-volume deployments:
- Consider adding database indexes on `attendance_date`, `employee`
- Implement background job processing for bulk salary slip generation
- Monitor calculation performance and optimize queries if needed

---

## Support

For issues, feature requests, or questions:
- Create an issue on GitHub
- Check existing documentation in README.md
- Review code comments in overtime_utils.py

---

## Changelog

### Version 1.0.0 (Initial Release)
- Designation-based attendance deductions
- Overtime calculation with flexible windows
- Automatic overtime capping
- Salary component auto-creation
- Custom field installation
