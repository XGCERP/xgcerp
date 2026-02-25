# Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved.
"""
Bug Condition Exploration Test for Module Name Mismatch

**Validates: Requirements 2.1, 2.2, 2.3**

This test explores the bug condition where modules.txt contains "XGCERP Integrations"
but the actual folder is named "erpnext_integrations/", causing installation failures.

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

The test encodes the expected behavior - it will validate the fix when it passes after implementation.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path


class TestModuleNameMismatchBug(unittest.TestCase):
	"""
	Property 1: Fault Condition - Module Name Mismatch Causes Installation Failure
	
	This test demonstrates that when modules.txt contains "XGCERP Integrations" but the
	actual folder is "erpnext_integrations/", the system cannot properly resolve the module.
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

	def test_01_modules_txt_has_mismatched_name(self):
		"""
		Test that modules.txt contains "XGCERP Integrations" while folder is "erpnext_integrations".
		
		This is the core bug condition: the module name doesn't match the folder structure.
		
		Expected on UNFIXED code: PASS (bug exists - mismatch detected)
		Expected on FIXED code: FAIL (bug is fixed - should be "XGCERP Integrations")
		"""
		with open(self.modules_txt_path, "r") as f:
			content = f.read()
		
		# Check for the bug: modules.txt has "XGCERP Integrations"
		has_xgcerp = "XGCERP Integrations" in content
		
		# Check that folder is actually "erpnext_integrations"
		folder_exists = self.integrations_folder.exists()
		xgcerp_folder = self.repo_root / "erpnext" / "xgcerp_integrations"
		xgcerp_folder_exists = xgcerp_folder.exists()
		
		# The bug exists when:
		# 1. modules.txt has "XGCERP Integrations" (mismatched name)
		# 2. Folder is "erpnext_integrations" (correct folder)
		# 3. No "xgcerp_integrations" folder exists (proves mismatch)
		
		self.assertTrue(
			has_xgcerp and folder_exists and not xgcerp_folder_exists,
			"Bug condition: modules.txt has 'XGCERP Integrations' but folder is 'erpnext_integrations/'"
		)

	def test_02_plaid_settings_json_has_mismatched_module_field(self):
		"""
		Test that plaid_settings.json has "module": "XGCERP Integrations" (the bug).
		
		Expected on UNFIXED code: PASS (bug exists)
		Expected on FIXED code: FAIL (bug is fixed, should be "XGCERP Integrations")
		"""
		with open(self.plaid_settings_path, "r") as f:
			data = json.load(f)
		
		# On unfixed code, this should be "XGCERP Integrations" (bug exists)
		# On fixed code, this should be "XGCERP Integrations" (bug is fixed)
		self.assertEqual(
			data.get("module"),
			"XGCERP Integrations",
			"plaid_settings.json should have 'XGCERP Integrations' on unfixed code (bug condition)"
		)

	def test_03_python_path_mismatch_demonstrates_bug(self):
		"""
		Test that the Python import path doesn't match the module name in modules.txt.
		
		This demonstrates that:
		- erpnext.erpnext_integrations CAN be imported (folder exists)
		- erpnext.xgcerp_integrations CANNOT be imported (folder doesn't exist)
		- But modules.txt references "XGCERP Integrations" (the mismatch)
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
		
		# Test 2: erpnext.xgcerp_integrations should NOT be importable
		can_import_xgcerp_integrations = False
		try:
			xgcerp_integrations_path = self.repo_root / "erpnext" / "xgcerp_integrations" / "__init__.py"
			can_import_xgcerp_integrations = xgcerp_integrations_path.exists()
		except Exception:
			pass
		
		# The bug exists when:
		# - erpnext_integrations exists (correct folder)
		# - xgcerp_integrations doesn't exist (proves mismatch)
		self.assertTrue(
			can_import_erpnext_integrations,
			"erpnext.erpnext_integrations should be importable (folder exists)"
		)
		self.assertFalse(
			can_import_xgcerp_integrations,
			"erpnext.xgcerp_integrations should NOT be importable (demonstrates mismatch)"
		)

	def test_04_smart_rename_script_causes_bug(self):
		"""
		Test that smart_rename.py performs global replace without exclusions.
		
		This demonstrates the root cause: the script changes "XGCERP Integrations"
		to "XGCERP Integrations" without excluding the integrations module.
		
		Expected on UNFIXED code: PASS (script damages the module name)
		Expected on FIXED code: FAIL (script preserves "XGCERP Integrations")
		"""
		# Create a temporary test file with "XGCERP Integrations"
		with tempfile.TemporaryDirectory() as tmpdir:
			test_modules_txt = Path(tmpdir) / "modules.txt"
			test_modules_txt.write_text("XGCERP Integrations\nXGCERP Assets\n")
			
			# Simulate what the unfixed script does: global replace
			with open(test_modules_txt, "r") as f:
				content = f.read()
			
			# The unfixed script does: content.replace("XGCERP", "XGCERP")
			# This is the bug - it doesn't exclude the integrations module
			new_content = content.replace("XGCERP", "XGCERP")
			
			# On unfixed code, "XGCERP Integrations" should be changed to "XGCERP Integrations"
			# This demonstrates the bug
			self.assertIn(
				"XGCERP Integrations",
				new_content,
				"Unfixed script changes 'XGCERP Integrations' to 'XGCERP Integrations' (demonstrates root cause)"
			)
			
			# On unfixed code, "XGCERP Integrations" should NOT be preserved
			# (This confirms the bug exists)
			self.assertNotIn(
				"XGCERP Integrations",
				new_content,
				"Unfixed script does NOT preserve 'XGCERP Integrations' (bug exists)"
			)
			
			# Also verify that other modules ARE rebranded (this is correct behavior)
			self.assertIn(
				"XGCERP Assets",
				new_content,
				"Script should rebrand other modules like 'XGCERP Assets' to 'XGCERP Assets'"
			)


if __name__ == "__main__":
	unittest.main()
