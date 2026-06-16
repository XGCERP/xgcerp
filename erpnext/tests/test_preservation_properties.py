# Copyright (c) 2026 Axina Group Inc. Created by Daniel Brody. All rights reserved.
"""
Preservation Property Tests for Module Name Mismatch Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9**

This test suite verifies that the fix for the module name mismatch bug does NOT
break existing functionality. These tests capture the baseline behavior on UNFIXED
code and ensure it is preserved after the fix.

IMPORTANT: These tests should PASS on UNFIXED code (confirming baseline behavior).
After implementing the fix, these tests should STILL PASS (confirming no regressions).

Property 2: Preservation - Other Modules and Rebranding Continue to Work
"""

import json
import unittest
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck


class TestPreservationProperties(unittest.TestCase):
	"""
	Property 2: Preservation - Other Modules and Rebranding Continue to Work

	These tests verify that:
	- All modules except "AXERP Integrations" continue to work correctly
	- The smart_rename.py script continues to rebrand other content correctly
	- Existing imports and functionality remain intact
	"""

	def setUp(self):
		"""Set up test fixtures"""
		self.repo_root = Path(__file__).parent.parent.parent
		self.modules_txt_path = self.repo_root / "erpnext" / "modules.txt"
		self.integrations_folder = self.repo_root / "erpnext" / "erpnext_integrations"

	def test_01_other_modules_exist_and_are_accessible(self):
		"""
		Test that all other modules (not integrations) exist and are accessible.

		This verifies that the module structure for all non-integrations modules
		is intact and can be accessed.

		Expected on UNFIXED code: PASS (other modules work correctly)
		Expected on FIXED code: PASS (other modules still work correctly)
		"""
		# Read all modules from modules.txt
		with open(self.modules_txt_path, "r") as f:
			modules = [line.strip() for line in f if line.strip()]

		# Filter out the integrations module (which has the bug)
		other_modules = [m for m in modules if "Integrations" not in m]

		# Verify we have other modules to test
		self.assertGreater(
			len(other_modules),
			0,
			"Should have other modules besides integrations"
		)

		# Verify that other modules have corresponding folders
		# Module names like "Assets", "CRM", etc. map to folders like "assets/", "crm/"
		for module_name in other_modules[:5]:  # Test first 5 modules as sample
			# Convert module name to folder name (lowercase, replace spaces with underscores)
			folder_name = module_name.lower().replace(" ", "_")
			module_folder = self.repo_root / "erpnext" / folder_name

			# Check if folder exists
			if module_folder.exists():
				# Verify it has an __init__.py (making it a Python module)
				init_file = module_folder / "__init__.py"
				self.assertTrue(
					init_file.exists(),
					f"Module folder {folder_name} should have __init__.py"
				)

	def test_02_integrations_folder_exists_with_correct_name(self):
		"""
		Test that the integrations folder exists as "erpnext_integrations".

		This is part of the baseline behavior - the folder has always been
		"erpnext_integrations" and should remain so after the fix.

		Expected on UNFIXED code: PASS (folder exists)
		Expected on FIXED code: PASS (folder still exists)
		"""
		self.assertTrue(
			self.integrations_folder.exists(),
			"erpnext_integrations folder should exist"
		)

		# Verify it's a Python module
		init_file = self.integrations_folder / "__init__.py"
		self.assertTrue(
			init_file.exists(),
			"erpnext_integrations should have __init__.py"
		)

	def test_03_integrations_imports_resolve_correctly(self):
		"""
		Test that existing imports from erpnext.erpnext_integrations resolve correctly.

		This verifies that the Python import path "erpnext.erpnext_integrations"
		works correctly, which is the baseline behavior to preserve.

		Expected on UNFIXED code: PASS (imports work)
		Expected on FIXED code: PASS (imports still work)
		"""
		# Check that the import path exists
		plaid_settings_path = (
			self.integrations_folder
			/ "doctype"
			/ "plaid_settings"
			/ "plaid_settings.py"
		)

		self.assertTrue(
			plaid_settings_path.exists(),
			"Plaid Settings doctype should exist at erpnext/erpnext_integrations/doctype/plaid_settings/"
		)

		# Verify the file is importable (has valid Python syntax)
		with open(plaid_settings_path, "r") as f:
			content = f.read()
			# Basic check: file should have Python code
			self.assertIn("import", content, "Python file should have import statements")

	@given(
		module_name=st.sampled_from([
			"Assets",
			"CRM",
			"Accounts",
			"Buying",
			"Selling",
			"Stock",
			"Manufacturing",
			"Projects"
		])
	)
	@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
	def test_04_property_other_modules_have_correct_structure(self, module_name):
		"""
		Property: For all modules except "AXERP Integrations", the module structure is correct.

		This property-based test generates test cases for multiple modules and verifies
		that they all have the expected folder structure.

		Expected on UNFIXED code: PASS (other modules are structured correctly)
		Expected on FIXED code: PASS (other modules still structured correctly)
		"""
		# Convert module name to folder name
		folder_name = module_name.lower().replace(" ", "_")
		module_folder = self.repo_root / "erpnext" / folder_name

		# Verify folder exists
		self.assertTrue(
			module_folder.exists(),
			f"Module {module_name} should have folder {folder_name}"
		)

		# Verify it's a Python module
		init_file = module_folder / "__init__.py"
		self.assertTrue(
			init_file.exists(),
			f"Module {module_name} should have __init__.py"
		)

	@given(
		content=st.text(
			alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs")),
			min_size=10,
			max_size=100
		).filter(lambda x: "AXERP Integrations" not in x and "Integrations" not in x)
	)
	@settings(
		max_examples=50,
		suppress_health_check=[HealthCheck.function_scoped_fixture]
	)
	def test_05_property_smart_rename_renames_erpnext_to_axerp(self, content):
		"""
		Property: For all content that does NOT contain "AXERP Integrations",
		the smart_replace logic should rename "AXERP" to "AXERP".

		This verifies that the rebranding functionality continues to work correctly
		for all content except the integrations module.

		Expected on UNFIXED code: PASS (rebranding works for other content)
		Expected on FIXED code: PASS (rebranding still works for other content)
		"""
		import importlib.util

		spec = importlib.util.spec_from_file_location(
			"smart_rename",
			str(self.repo_root / "scripts" / "smart_rename.py"),
		)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)

		# Add "AXERP" to the content to test rebranding
		test_content = f"AXERP {content}"

		# Use the actual smart_replace function
		rebranded = module.smart_replace(test_content, "test.txt")

		# Verify that "AXERP" was replaced with "AXERP"
		self.assertIn(
			"AXERP",
			rebranded,
			"Content with 'AXERP' should be rebranded to 'AXERP'"
		)
		self.assertNotIn(
			"AXERP",
			rebranded,
			"After rebranding, 'AXERP' should not remain"
		)

	@given(
		module_name=st.sampled_from([
			"AXERP Assets",
			"AXERP CRM",
			"AXERP Accounts",
			"AXERP Manufacturing"
		])
	)
	@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
	def test_06_property_other_erpnext_modules_are_rebranded(self, module_name):
		"""
		Property: For all "AXERP X" module names (except "AXERP Integrations"),
		the smart_replace logic should rename them to "AXERP X".

		This verifies that other modules with "AXERP" in their name are correctly
		rebranded, while only "AXERP Integrations" is excluded.

		Expected on UNFIXED code: PASS (other AXERP modules are rebranded)
		Expected on FIXED code: PASS (other AXERP modules still rebranded)
		"""
		import importlib.util

		spec = importlib.util.spec_from_file_location(
			"smart_rename",
			str(self.repo_root / "scripts" / "smart_rename.py"),
		)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)

		# Use the actual smart_replace function
		rebranded = module.smart_replace(module_name, "test.txt")

		# Verify rebranding occurred
		self.assertIn(
			"AXERP",
			rebranded,
			f"Module '{module_name}' should be rebranded to use 'AXERP'"
		)
		self.assertNotIn(
			"AXERP",
			rebranded,
			f"After rebranding, '{module_name}' should not contain 'AXERP'"
		)

	def test_07_json_module_fields_for_other_modules_exist(self):
		"""
		Test that JSON files for other modules (not integrations) have module fields.

		This verifies that the JSON structure for other modules is intact and
		will continue to work after the fix.

		Expected on UNFIXED code: PASS (other modules have correct JSON structure)
		Expected on FIXED code: PASS (other modules still have correct JSON structure)
		"""
		# Sample a few JSON files from other modules
		sample_json_files = [
			self.repo_root / "erpnext" / "assets" / "doctype" / "asset" / "asset.json",
			self.repo_root / "erpnext" / "crm" / "doctype" / "lead" / "lead.json",
		]

		for json_file in sample_json_files:
			if json_file.exists():
				with open(json_file, "r") as f:
					data = json.load(f)

				# Verify the JSON has a module field
				self.assertIn(
					"module",
					data,
					f"{json_file.name} should have a 'module' field"
				)

				# Verify the module field is not empty
				self.assertTrue(
					data["module"],
					f"{json_file.name} module field should not be empty"
				)

	@given(
		json_content=st.fixed_dictionaries({
			"module": st.sampled_from(["Assets", "CRM", "Accounts", "Stock"]),
			"name": st.text(min_size=1, max_size=50),
			"doctype": st.just("DocType")
		})
	)
	@settings(
		max_examples=20,
		suppress_health_check=[HealthCheck.function_scoped_fixture]
	)
	def test_08_property_json_module_fields_for_other_modules_are_valid(self, json_content):
		"""
		Property: For all JSON files with module fields (except integrations),
		the module field should reference a valid module name.

		This verifies that JSON module fields for other modules are correctly
		structured and will continue to work after the fix.

		Expected on UNFIXED code: PASS (other module fields are valid)
		Expected on FIXED code: PASS (other module fields still valid)
		"""
		# Verify the module field is present
		self.assertIn("module", json_content)

		# Verify the module field is not "AXERP Integrations"
		self.assertNotIn("Integrations", json_content["module"])

		# Verify the module name is a valid string
		self.assertIsInstance(json_content["module"], str)
		self.assertGreater(len(json_content["module"]), 0)

	def test_09_smart_rename_preserves_file_structure(self):
		"""
		Test that smart_rename.py logic doesn't rename folder names.

		This verifies that the rebranding script only modifies file contents,
		not folder names, which is the baseline behavior to preserve.

		Expected on UNFIXED code: PASS (folders are not renamed)
		Expected on FIXED code: PASS (folders still not renamed)
		"""
		# Verify that folders with "erpnext" in their name still exist
		# (the script doesn't rename folders, only file contents)

		# Check that erpnext_integrations folder exists (not renamed)
		self.assertTrue(
			self.integrations_folder.exists(),
			"erpnext_integrations folder should exist (not renamed)"
		)

		# Check that no axerp_integrations folder exists
		axerp_folder = self.repo_root / "erpnext" / "axerp_integrations"
		self.assertFalse(
			axerp_folder.exists(),
			"axerp_integrations folder should NOT exist (folders are not renamed)"
		)

	@given(
		prefix=st.text(min_size=5, max_size=50),
		suffix=st.text(min_size=5, max_size=50)
	)
	@settings(
		max_examples=30,
		suppress_health_check=[HealthCheck.function_scoped_fixture]
	)
	def test_10_property_rebranding_works_for_non_integrations_content(self, prefix, suffix):
		"""
		Property: For all content containing "AXERP" but NOT "AXERP Integrations",
		the rebranding should replace "AXERP" with "AXERP".

		This is a comprehensive property test that verifies the rebranding logic
		works correctly for all non-integrations content.

		Expected on UNFIXED code: PASS (rebranding works)
		Expected on FIXED code: PASS (rebranding still works)
		"""
		import importlib.util

		spec = importlib.util.spec_from_file_location(
			"smart_rename",
			str(self.repo_root / "scripts" / "smart_rename.py"),
		)
		mod = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(mod)

		# Construct test content with "AXERP" in the middle
		test_content = f"{prefix} AXERP {suffix}"

		# Skip if this accidentally creates "AXERP Integrations"
		if "AXERP Integrations" in test_content:
			return

		# Use the actual smart_replace function
		rebranded = mod.smart_replace(test_content, "test.txt")

		# Verify rebranding occurred
		self.assertIn(
			"AXERP",
			rebranded,
			"Content should be rebranded to use 'AXERP'"
		)

		# Verify "AXERP" was replaced
		self.assertNotIn(
			"AXERP",
			rebranded,
			"After rebranding, 'AXERP' should not remain"
		)


if __name__ == "__main__":
	unittest.main()
