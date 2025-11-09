import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
	"""Create custom fields for Designation doctype after app installation"""
	create_designation_custom_fields()
	create_salary_components()


def create_designation_custom_fields():
	"""Add attendance deduction fields to Designation doctype"""

	custom_fields = {
		"Designation": [
			{
				"fieldname": "attendance_deductions_section",
				"label": "Attendance Deductions",
				"fieldtype": "Section Break",
				"insert_after": "description",
				"collapsible": 0,
			},
			{
				"fieldname": "attendance_deductions_note",
				"label": "Note",
				"fieldtype": "HTML",
				"insert_after": "attendance_deductions_section",
				"options": "<p style='color: #888;'>Set the deduction amounts for attendance violations. These amounts will be deducted per occurrence from employee salaries.</p>",
			},
			{
				"fieldname": "absent_deduction",
				"label": "Absent Deduction",
				"fieldtype": "Currency",
				"insert_after": "attendance_deductions_note",
				"description": "Amount to deduct per absence occurrence",
				"precision": 2,
			},
			{
				"fieldname": "column_break_deductions",
				"fieldtype": "Column Break",
				"insert_after": "absent_deduction",
			},
			{
				"fieldname": "late_deduction",
				"label": "Late Deduction",
				"fieldtype": "Currency",
				"insert_after": "column_break_deductions",
				"description": "Amount to deduct per late arrival occurrence",
				"precision": 2,
			},
			{
				"fieldname": "section_break_deductions_2",
				"fieldtype": "Section Break",
				"insert_after": "late_deduction",
			},
			{
				"fieldname": "early_exit_deduction",
				"label": "Early Exit Deduction",
				"fieldtype": "Currency",
				"insert_after": "section_break_deductions_2",
				"description": "Amount to deduct per early exit occurrence",
				"precision": 2,
			},
			{
				"fieldname": "column_break_deductions_2",
				"fieldtype": "Column Break",
				"insert_after": "early_exit_deduction",
			},
			{
				"fieldname": "no_checkout_deduction",
				"label": "Employee Doesn't Checkout Deduction",
				"fieldtype": "Currency",
				"insert_after": "column_break_deductions_2",
				"description": "Amount to deduct when employee doesn't checkout",
				"precision": 2,
			},
			# Overtime Configuration Section
			{
				"fieldname": "overtime_configuration_section",
				"label": "Overtime Configuration",
				"fieldtype": "Section Break",
				"insert_after": "no_checkout_deduction",
				"collapsible": 1,
			},
			{
				"fieldname": "overtime_configuration_note",
				"label": "Note",
				"fieldtype": "HTML",
				"insert_after": "overtime_configuration_section",
				"options": "<p style='color: #888;'>Set the overtime window and hourly rate for this designation. Overtime will be calculated between the start and end times, and capped at the end time.</p>",
			},
			{
				"fieldname": "overtime_start_time",
				"label": "Overtime Start Time",
				"fieldtype": "Time",
				"insert_after": "overtime_configuration_note",
				"description": "Time when overtime calculation begins (e.g., 17:00:00 for 5:00 PM)",
			},
			{
				"fieldname": "column_break_overtime",
				"fieldtype": "Column Break",
				"insert_after": "overtime_start_time",
			},
			{
				"fieldname": "overtime_end_time",
				"label": "Overtime End Time",
				"fieldtype": "Time",
				"insert_after": "column_break_overtime",
				"description": "Maximum time for overtime calculation (e.g., 22:00:00 for 10:00 PM). Work beyond this time will not be paid.",
			},
			{
				"fieldname": "section_break_overtime_2",
				"fieldtype": "Section Break",
				"insert_after": "overtime_end_time",
			},
			{
				"fieldname": "overtime_hourly_rate",
				"label": "Overtime Hourly Rate",
				"fieldtype": "Currency",
				"insert_after": "section_break_overtime_2",
				"description": "Amount to pay per hour of overtime worked",
				"precision": 2,
			},
		]
	}

	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()

	print("Custom fields added to Designation doctype successfully!")


def create_salary_components():
	"""Create salary components for attendance deductions and overtime"""

	components = [
		{
			'salary_component': 'Absent Deduction',
			'description': 'Deduction for absence based on designation rate',
			'type': 'Deduction'
		},
		{
			'salary_component': 'Late Deduction',
			'description': 'Deduction for late arrival based on designation rate',
			'type': 'Deduction'
		},
		{
			'salary_component': 'Early Exit Deduction',
			'description': 'Deduction for early exit based on designation rate',
			'type': 'Deduction'
		},
		{
			'salary_component': 'No Checkout Deduction',
			'description': 'Deduction when employee does not checkout based on designation rate',
			'type': 'Deduction'
		},
		{
			'salary_component': 'Designation Overtime Pay',
			'description': 'Overtime payment based on designation overtime rate',
			'type': 'Earning'
		}
	]

	for comp_data in components:
		if not frappe.db.exists('Salary Component', comp_data['salary_component']):
			comp = frappe.get_doc({
				'doctype': 'Salary Component',
				'salary_component': comp_data['salary_component'],
				'description': comp_data['description'],
				'type': comp_data['type']
			})
			comp.insert(ignore_permissions=True)
			print(f"✓ Created salary component: {comp_data['salary_component']}")

	frappe.db.commit()
	print("Salary components created successfully!")
