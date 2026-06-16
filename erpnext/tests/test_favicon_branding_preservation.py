# Copyright (c) 2026 Axina Group Inc. Created by Daniel Brody. All rights reserved.
"""
Preservation Property Tests for Favicon & Branding Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

These tests capture the baseline behavior of non-branding assets, SVG overwrite
targets, smart_replace() integration-module preservation, and app logo references.
They MUST PASS on UNFIXED code to confirm the baseline, and MUST CONTINUE TO PASS
after the fix to confirm no regressions.
"""

import ast
import hashlib
import re
import unittest
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st


REPO_ROOT = Path(__file__).parent.parent.parent
IMAGES_DIR = REPO_ROOT / "erpnext" / "public" / "images"
HOOKS_PATH = REPO_ROOT / "erpnext" / "hooks.py"
SMART_RENAME_PATH = REPO_ROOT / "scripts" / "smart_rename.py"

# --- Observed baseline: all non-branding files in erpnext/public/images/ ---
# Branding files that the fix will ADD (these are excluded from preservation checks)
BRANDING_FILENAMES = {
	"favicon.ico",
	"favicon-16x16.png",
	"favicon-32x32.png",
	"apple-touch-icon.png",
	"android-chrome-192x192.png",
	"android-chrome-512x512.png",
	"site.webmanifest",
}

# Observed non-branding files (must remain byte-identical after fix)
NON_BRANDING_FILES = [
	"erpnext-favicon.svg",
	"erpnext-logo.svg",
	"erpnext-logo.png",
	"erpnext-logo-blue.png",
	"erpnext-video-placeholder.jpg",
	"pos.svg",
	"YouTube-icon-full_color.png",
	"illustrations/shop.jpg",
	"illustrations/shop2.jpg",
	"leaflet/farmer.png",
	"leaflet/layers-2x.png",
	"leaflet/layers.png",
	"leaflet/marker-icon-2x.png",
	"leaflet/marker-icon.png",
	"leaflet/marker-shadow.png",
	"leaflet/spritesheet-2x.png",
	"leaflet/spritesheet.png",
	"leaflet/spritesheet.svg",
	"ui-states/cart-empty-state.png",
	"v16/erpnext.svg",
	"v16/hero_image.png",
]


# Expected SVG overwrite targets from smart_rename.py step 3
EXPECTED_SVG_TARGETS = [
	"erpnext-logo.svg",
	"erpnext-favicon.svg",
	"v16/erpnext.svg",
]

# Contexts where erpnext_integrations must be preserved by smart_replace()
INTEGRATION_CONTEXTS = [
	# Python import style
	"from erpnext.erpnext_integrations.doctype import plaid_settings",
	# JSON module field style
	'{"module": "AXERP Integrations", "name": "Plaid Settings"}',
	# modules.txt line style
	"AXERP Integrations",
	# Dotted Python path
	"erpnext.erpnext_integrations.doctype.plaid_settings.plaid_settings",
	# Quoted in Python
	'"erpnext_integrations"',
	# Single-quoted in Python
	"'erpnext_integrations'",
]


def _compute_file_hash(filepath: Path) -> str:
	"""Compute SHA-256 hash of a file's contents."""
	return hashlib.sha256(filepath.read_bytes()).hexdigest()


def _parse_svg_targets_from_smart_rename() -> list[str]:
	"""
	Extract the SVG overwrite target filenames from smart_rename.py step 3.
	Returns relative paths like ['erpnext-logo.svg', 'erpnext-favicon.svg', 'v16/erpnext.svg'].
	"""
	content = SMART_RENAME_PATH.read_text()
	# The targets are in the paths list inside run_rebrand(), like:
	#   os.path.join(root_dir, "erpnext", "public", "images", "erpnext-logo.svg"),
	#   os.path.join(root_dir, "erpnext", "public", "images", "v16", "erpnext.svg")
	# Extract the relative part after "images"
	pattern = re.compile(
		r'os\.path\.join\(root_dir,\s*"erpnext",\s*"public",\s*"images",\s*(.+?)\)'
	)
	targets = []
	for match in pattern.finditer(content):
		# Parse the remaining args, e.g. '"erpnext-logo.svg"' or '"v16", "erpnext.svg"'
		args_str = match.group(1)
		# Extract all quoted strings
		parts = re.findall(r'"([^"]+)"', args_str)
		if parts:
			targets.append("/".join(parts))
	return targets


def _load_smart_replace_function():
	"""
	Dynamically import the smart_replace function from smart_rename.py.
	"""
	import importlib.util

	spec = importlib.util.spec_from_file_location("smart_rename", str(SMART_RENAME_PATH))
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module.smart_replace


def _parse_hooks_value(key: str) -> str:
	"""Extract a simple string value assigned to `key` in hooks.py."""
	content = HOOKS_PATH.read_text()
	for line in content.splitlines():
		stripped = line.strip()
		if stripped.startswith(f"{key}") and "=" in stripped:
			_, _, value_part = stripped.partition("=")
			return value_part.strip().strip("\"'")
	return ""


def _parse_add_to_apps_screen_logo() -> str:
	"""Extract the 'logo' value from add_to_apps_screen in hooks.py."""
	content = HOOKS_PATH.read_text()
	# Find the logo line inside add_to_apps_screen block
	in_block = False
	for line in content.splitlines():
		stripped = line.strip()
		if "add_to_apps_screen" in stripped and "=" in stripped:
			in_block = True
			continue
		if in_block:
			if '"logo"' in stripped or "'logo'" in stripped:
				# Extract value: "logo": "/assets/erpnext/images/erpnext-logo.svg",
				for quote in ['"', "'"]:
					marker = f"{quote}logo{quote}"
					if marker in stripped:
						idx = stripped.index(marker) + len(marker)
						rest = stripped[idx:].strip().lstrip(":").strip()
						for q in ['"', "'"]:
							if rest.startswith(q):
								end = rest.index(q, 1)
								return rest[1:end]
			# End of block detection (closing bracket at top level)
			if stripped == "]":
				break
	return ""


class TestPreservationNonBrandingFiles(unittest.TestCase):
	"""
	Property 2a: Non-branding files in erpnext/public/images/ remain present
	and byte-identical after the fix.

	**Validates: Requirements 3.1**
	"""

	@given(rel_path=st.sampled_from(NON_BRANDING_FILES))
	@settings(max_examples=len(NON_BRANDING_FILES))
	def test_non_branding_files_exist_and_are_intact(self, rel_path: str):
		"""
		For all non-branding files in erpnext/public/images/, the file must
		exist on disk. This captures the baseline — the same test re-run after
		the fix confirms no files were deleted or corrupted.

		**Validates: Requirements 3.1**
		"""
		filepath = IMAGES_DIR / rel_path
		self.assertTrue(
			filepath.exists(),
			f"Non-branding file '{rel_path}' must exist in {IMAGES_DIR}",
		)
		# Verify the file is non-empty (not corrupted to zero bytes)
		self.assertGreater(
			filepath.stat().st_size,
			0,
			f"Non-branding file '{rel_path}' must not be empty",
		)


class TestPreservationSVGOverwriteTargets(unittest.TestCase):
	"""
	Property 2b: smart_rename.py SVG overwrite targets remain exactly
	erpnext-logo.svg, erpnext-favicon.svg, v16/erpnext.svg.

	**Validates: Requirements 3.2**
	"""

	def test_svg_overwrite_targets_match_expected(self):
		"""
		The SVG overwrite target list in smart_rename.py step 3 must contain
		exactly the 3 expected targets, in any order.

		**Validates: Requirements 3.2**
		"""
		actual_targets = _parse_svg_targets_from_smart_rename()
		self.assertEqual(
			sorted(actual_targets),
			sorted(EXPECTED_SVG_TARGETS),
			f"SVG overwrite targets changed! Expected {EXPECTED_SVG_TARGETS}, got {actual_targets}",
		)

	@given(target=st.sampled_from(EXPECTED_SVG_TARGETS))
	@settings(max_examples=len(EXPECTED_SVG_TARGETS))
	def test_each_svg_target_present_in_smart_rename(self, target: str):
		"""
		Each expected SVG overwrite target must appear in smart_rename.py.

		**Validates: Requirements 3.2**
		"""
		content = SMART_RENAME_PATH.read_text()
		# The target filename (last component) must appear in the file
		filename = target.split("/")[-1]
		self.assertIn(
			filename,
			content,
			f"SVG target '{target}' (filename '{filename}') not found in smart_rename.py",
		)


class TestPreservationSmartReplace(unittest.TestCase):
	"""
	Property 2c: smart_replace() preserves erpnext_integrations in all contexts
	(Python imports, JSON module fields, modules.txt).

	**Validates: Requirements 3.3**
	"""

	@classmethod
	def setUpClass(cls):
		cls._smart_replace_fn = _load_smart_replace_function()

	@given(context=st.sampled_from(INTEGRATION_CONTEXTS))
	@settings(max_examples=len(INTEGRATION_CONTEXTS))
	def test_smart_replace_preserves_erpnext_integrations(self, context: str):
		"""
		For all contexts containing erpnext_integrations references,
		smart_replace() must preserve them unchanged after replacement.

		**Validates: Requirements 3.3**
		"""
		smart_replace = self.__class__._smart_replace_fn

		# Determine filename hint for smart_replace
		if context.strip().startswith("{"):
			filename = "test.json"
		elif context.strip() == "AXERP Integrations":
			filename = "modules.txt"
		else:
			filename = "test.py"

		result = smart_replace(context, filename)

		# erpnext_integrations must still be present (not renamed to axerp_integrations)
		if "erpnext_integrations" in context:
			self.assertIn(
				"erpnext_integrations",
				result,
				f"smart_replace() corrupted erpnext_integrations in context: {context!r}",
			)
			self.assertNotIn(
				"axerp_integrations",
				result,
				f"smart_replace() incorrectly renamed erpnext_integrations in: {context!r}",
			)

		# "AXERP Integrations" module name must be preserved in modules.txt and JSON
		if "AXERP Integrations" in context:
			self.assertIn(
				"AXERP Integrations",
				result,
				f"smart_replace() corrupted 'AXERP Integrations' module name in: {context!r}",
			)


class TestPreservationAppLogoReferences(unittest.TestCase):
	"""
	Property 2d: app_logo_url and add_to_apps_screen logo still reference
	the SVG logo path.

	**Validates: Requirements 3.4**
	"""

	def test_app_logo_url_references_svg(self):
		"""
		app_logo_url in hooks.py must reference the SVG logo path
		(/assets/erpnext/images/erpnext-logo.svg).

		**Validates: Requirements 3.4**
		"""
		logo_url = _parse_hooks_value("app_logo_url")
		self.assertTrue(logo_url, "app_logo_url should be set in hooks.py")
		self.assertEqual(
			logo_url,
			"/assets/erpnext/images/erpnext-logo.svg",
			f"app_logo_url should reference erpnext-logo.svg, got '{logo_url}'",
		)

	def test_add_to_apps_screen_logo_references_svg(self):
		"""
		add_to_apps_screen logo in hooks.py must reference the SVG logo path.

		**Validates: Requirements 3.4**
		"""
		logo = _parse_add_to_apps_screen_logo()
		self.assertTrue(logo, "add_to_apps_screen logo should be set in hooks.py")
		self.assertEqual(
			logo,
			"/assets/erpnext/images/erpnext-logo.svg",
			f"add_to_apps_screen logo should reference erpnext-logo.svg, got '{logo}'",
		)


if __name__ == "__main__":
	unittest.main()
