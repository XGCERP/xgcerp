# Copyright (c) 2026 Axina Group Inc. Created by Daniel Brody. All rights reserved.
"""
Bug Condition Exploration Test for Module Name Mismatch

**Validates: Requirements 2.1, 2.2, 2.3**

This test explores the bug condition where modules.txt contains "AXERP Integrations"
but the actual folder is named "erpnext_integrations/", causing installation failures.

The smart_rename.py script must preserve "AXERP Integrations" in modules.txt
(matching the folder name "erpnext_integrations") and NOT rebrand it to "AXERP Integrations".

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

The test encodes the expected behavior - it will validate the fix when it passes after implementation.
"""

import json
import sys
import unittest
from pathlib import Path


class TestModuleNameMismatchBug(unittest.TestCase):
	"""
	Property 1: Fault Condition - Module Name Mismatch Causes Installation Failure

	This test demonstrates that when modules.txt contains "AXERP Integrations" but the
	actual folder is "erpnext_integrations/", the system cannot properly resolve the module.
	The correct value in modules.txt should be "AXERP Integrations".
	"""

	def setUp(self):
		"""Set up test fixtures"""
		self.repo_root = Path(__file__).parent.parent.parent
		self.modules_txt_path = self.repo_root / "erpnext" / "modules.txt"
		self.plaid_settings_path = (
			self.repo_root
			/ "erpnext"
			/ "erpnext_integrations"
			/ "doctype"
			/ "plaid_settings"
			/ "plaid_settings.json"
		)
		self.smart_rename_path = self.repo_root / "scripts" / "smart_rename.py"
		self.integrations_folder = self.repo_root / "erpnext" / "erpnext_integrations"

	def test_01_modules_txt_has_correct_integrations_name(self):
		"""
		Test that modules.txt contains "AXERP Integrations" matching the folder "erpnext_integrations".

		The smart_rename.py script must preserve "AXERP Integrations" in modules.txt
		because the folder is named "erpnext_integrations/" and renaming would break imports.

		Expected: PASS (modules.txt has "AXERP Integrations" matching the folder)
		"""
		with open(self.modules_txt_path, "r") as f:
			content = f.read()

		# modules.txt must have "AXERP Integrations" (preserved by smart_rename.py)
		has_erpnext_integrations = "AXERP Integrations" in content

		# Check that folder is actually "erpnext_integrations"
		folder_exists = self.integrations_folder.exists()
		axerp_folder = self.repo_root / "erpnext" / "axerp_integrations"
		axerp_folder_exists = axerp_folder.exists()

		# Correct state:
		# 1. modules.txt has "AXERP Integrations" (matching folder name)
		# 2. Folder is "erpnext_integrations" (correct folder)
		# 3. No "axerp_integrations" folder exists

		self.assertTrue(
			has_erpnext_integrations and folder_exists and not axerp_folder_exists,
			"modules.txt should have 'AXERP Integrations' matching folder 'erpnext_integrations/'"
		)

	def test_02_plaid_settings_json_has_correct_module_field(self):
		"""
		Test that plaid_settings.json has "module": "AXERP Integrations" (preserved).

		The smart_rename.py script preserves "AXERP Integrations" in JSON module fields
		because the folder is "erpnext_integrations" and renaming would break the module.

		Expected: PASS (module field matches the preserved folder name)
		"""
		with open(self.plaid_settings_path, "r") as f:
			data = json.load(f)

		self.assertEqual(
			data.get("module"),
			"AXERP Integrations",
			"plaid_settings.json should have 'AXERP Integrations' (preserved by smart_rename.py)"
		)

	def test_03_python_path_mismatch_demonstrates_bug(self):
		"""
		Test that the Python import path doesn't match the module name in modules.txt.

		This demonstrates that:
		- erpnext.erpnext_integrations CAN be imported (folder exists)
		- erpnext.axerp_integrations CANNOT be imported (folder doesn't exist)
		- But modules.txt references "AXERP Integrations" (the mismatch)
		"""
		# Add the repo root to sys.path so we can import erpnext
		if str(self.repo_root) not in sys.path:
			sys.path.insert(0, str(self.repo_root))

		# Test 1: erpnext.erpnext_integrations should be importable
		can_import_erpnext_integrations = False
		try:
			# Check if the module path exists
			erpnext_integrations_path = self.repo_root / "erpnext" / "erpnext_integrations" / "__init__.py"
			can_import_erpnext_integrations = erpnext_integrations_path.exists()
		except Exception:
			pass

		# Test 2: erpnext.axerp_integrations should NOT be importable
		can_import_axerp_integrations = False
		try:
			axerp_integrations_path = self.repo_root / "erpnext" / "axerp_integrations" / "__init__.py"
			can_import_axerp_integrations = axerp_integrations_path.exists()
		except Exception:
			pass

		# The bug exists when:
		# - erpnext_integrations exists (correct folder)
		# - axerp_integrations doesn't exist (proves mismatch)
		self.assertTrue(
			can_import_erpnext_integrations,
			"erpnext.erpnext_integrations should be importable (folder exists)"
		)
		self.assertFalse(
			can_import_axerp_integrations,
			"erpnext.axerp_integrations should NOT be importable (demonstrates mismatch)"
		)

	def test_04_smart_rename_script_preserves_integrations(self):
		"""
		Test that smart_rename.py's smart_replace() preserves "AXERP Integrations"
		in modules.txt while rebranding other module names.

		This verifies the fix: smart_replace() correctly handles the integrations
		module exclusion.

		Expected: PASS (smart_replace preserves AXERP Integrations)
		"""
		import importlib.util

		spec = importlib.util.spec_from_file_location("smart_rename", str(self.smart_rename_path))
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
		smart_replace = module.smart_replace

		# Create test content simulating modules.txt with the original AXERP names
		test_content = "AXERP Integrations\nAXERP Assets\n"

		# Apply smart_replace (which should preserve AXERP Integrations)
		new_content = smart_replace(test_content, "modules.txt")

		# "AXERP Integrations" must be preserved (not renamed)
		self.assertIn(
			"AXERP Integrations",
			new_content,
			"smart_replace() should preserve 'AXERP Integrations' in modules.txt"
		)

		# Other modules should be rebranded
		self.assertNotIn(
			"AXERP Assets",
			new_content,
			"smart_replace() should rebrand 'AXERP Assets' to 'AXERP Assets'"
		)
		self.assertIn(
			"AXERP Assets",
			new_content,
			"smart_replace() should rebrand 'AXERP Assets' to 'AXERP Assets'"
		)


if __name__ == "__main__":
	unittest.main()
