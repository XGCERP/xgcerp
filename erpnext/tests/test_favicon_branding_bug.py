# Copyright (c) 2026 Axina Group Inc. Created by Daniel Brody. All rights reserved.
"""
Bug Condition Exploration Test for Favicon & Branding Assets

**Validates: Requirements 1.1, 1.4, 1.5, 2.1, 2.4, 2.5**

This test explores the bug condition where branding assets (favicon, email brand image,
webmanifest icons, raster favicon files) resolve to missing or old files.

CRITICAL: This test MUST FAIL on unfixed code — failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

The test encodes the expected behavior — it will validate the fix when it passes
after implementation.
"""

import json
import unittest
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st


# Concrete branding asset inputs scoped to the known failing cases
RASTER_FAVICON_FILES = [
	"favicon.ico",
	"favicon-16x16.png",
	"favicon-32x32.png",
	"apple-touch-icon.png",
	"android-chrome-192x192.png",
	"android-chrome-512x512.png",
]

REPO_ROOT = Path(__file__).parent.parent.parent
IMAGES_DIR = REPO_ROOT / "erpnext" / "public" / "images"
HOOKS_PATH = REPO_ROOT / "erpnext" / "hooks.py"
WEBMANIFEST_PATH = IMAGES_DIR / "site.webmanifest"


def _parse_hooks_value(key: str) -> str:
	"""Extract a simple string value assigned to `key` in hooks.py."""
	content = HOOKS_PATH.read_text()
	for line in content.splitlines():
		stripped = line.strip()
		if stripped.startswith(f"{key}") and "=" in stripped:
			# e.g.  email_brand_image = "assets/erpnext/images/erpnext-logo.jpg"
			_, _, value_part = stripped.partition("=")
			return value_part.strip().strip("\"'")
	return ""


def _parse_website_context_favicon() -> str:
	"""Extract website_context["favicon"] value from hooks.py."""
	content = HOOKS_PATH.read_text()
	# Find the website_context dict and extract favicon value
	in_website_context = False
	brace_depth = 0
	for line in content.splitlines():
		stripped = line.strip()
		if "website_context" in stripped and "=" in stripped and "{" in stripped:
			in_website_context = True
			brace_depth = stripped.count("{") - stripped.count("}")
			# Check if favicon is on this line
			if '"favicon"' in stripped or "'favicon'" in stripped:
				return _extract_dict_value(stripped, "favicon")
			continue
		if in_website_context:
			brace_depth += stripped.count("{") - stripped.count("}")
			if '"favicon"' in stripped or "'favicon'" in stripped:
				return _extract_dict_value(stripped, "favicon")
			if brace_depth <= 0:
				break
	return ""


def _extract_dict_value(line: str, key: str) -> str:
	"""Extract value for a key from a dict-like line."""
	# Match patterns like: "favicon": "/assets/erpnext/images/erpnext-favicon.svg",
	for quote in ['"', "'"]:
		marker = f"{quote}{key}{quote}"
		if marker in line:
			idx = line.index(marker) + len(marker)
			rest = line[idx:].strip().lstrip(":").strip()
			# Extract the quoted value
			for q in ['"', "'"]:
				if rest.startswith(q):
					end = rest.index(q, 1)
					return rest[1:end]
	return ""


class TestFaviconBrandingBug(unittest.TestCase):
	"""
	Property 1: Bug Condition — Branding Assets Resolve to Missing or Old Files

	Tests that branding asset references in hooks.py and site.webmanifest resolve
	to files that actually exist in erpnext/public/images/ and are AXERP-branded
	(not old ERPNext branding).
	"""

	def test_01_favicon_hook_resolves_to_existing_non_old_file(self):
		"""
		website_context["favicon"] must point to a file that exists in
		erpnext/public/images/ and is NOT the old erpnext-favicon.svg.

		**Validates: Requirements 1.1, 2.1**
		"""
		favicon_path = _parse_website_context_favicon()
		self.assertTrue(favicon_path, "website_context['favicon'] should be set in hooks.py")

		# The path should be like /assets/erpnext/images/<filename>
		# Strip the /assets/erpnext/ prefix to get the relative path under public/
		prefix = "/assets/erpnext/"
		self.assertTrue(
			favicon_path.startswith(prefix),
			f"Favicon path '{favicon_path}' should start with '{prefix}'",
		)
		relative = favicon_path[len(prefix):]  # e.g. "images/favicon.ico"
		resolved = REPO_ROOT / "erpnext" / "public" / relative

		# Must exist on disk
		self.assertTrue(
			resolved.exists(),
			f"Favicon file '{resolved}' does not exist on disk",
		)

		# Must NOT be the old erpnext-favicon.svg
		self.assertNotEqual(
			resolved.name,
			"erpnext-favicon.svg",
			"Favicon should NOT be old erpnext-favicon.svg",
		)

	def test_02_email_brand_image_resolves_to_existing_file(self):
		"""
		email_brand_image must reference a file that actually exists in
		erpnext/public/images/.

		**Validates: Requirements 1.4, 2.4**
		"""
		email_image = _parse_hooks_value("email_brand_image")
		self.assertTrue(email_image, "email_brand_image should be set in hooks.py")

		# The value is like "assets/erpnext/images/erpnext-logo.jpg" (no leading /)
		# Resolve to disk path
		prefix = "assets/erpnext/"
		self.assertTrue(
			email_image.startswith(prefix),
			f"email_brand_image '{email_image}' should start with '{prefix}'",
		)
		relative = email_image[len(prefix):]  # e.g. "images/erpnext-logo.jpg"
		resolved = REPO_ROOT / "erpnext" / "public" / relative

		self.assertTrue(
			resolved.exists(),
			f"email_brand_image file '{resolved}' does not exist on disk "
			f"(currently references '{email_image}')",
		)

	def test_03_site_webmanifest_exists_in_images_dir(self):
		"""
		site.webmanifest must exist in erpnext/public/images/.

		**Validates: Requirements 1.5, 2.5**
		"""
		self.assertTrue(
			WEBMANIFEST_PATH.exists(),
			f"site.webmanifest does not exist at {WEBMANIFEST_PATH}",
		)

	def test_04_webmanifest_icon_paths_use_frappe_prefix(self):
		"""
		All icon src values in erpnext/public/images/site.webmanifest must start
		with /assets/erpnext/images/.

		**Validates: Requirements 1.5, 2.5**
		"""
		if not WEBMANIFEST_PATH.exists():
			self.fail(f"site.webmanifest does not exist at {WEBMANIFEST_PATH}")

		data = json.loads(WEBMANIFEST_PATH.read_text())
		icons = data.get("icons", [])
		self.assertTrue(icons, "site.webmanifest should contain at least one icon")

		expected_prefix = "/assets/erpnext/images/"
		for icon in icons:
			src = icon.get("src", "")
			self.assertTrue(
				src.startswith(expected_prefix),
				f"Icon src '{src}' does not start with '{expected_prefix}'",
			)

	@given(filename=st.sampled_from(RASTER_FAVICON_FILES))
	@settings(max_examples=len(RASTER_FAVICON_FILES))
	def test_05_raster_favicon_files_exist_in_images_dir(self, filename: str):
		"""
		All 6 raster favicon files must exist in erpnext/public/images/.

		**Validates: Requirements 1.4, 2.4**
		"""
		filepath = IMAGES_DIR / filename
		self.assertTrue(
			filepath.exists(),
			f"Raster favicon file '{filename}' does not exist in {IMAGES_DIR}",
		)


if __name__ == "__main__":
	unittest.main()
