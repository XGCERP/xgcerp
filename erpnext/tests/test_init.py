from erpnext import encode_company_abbr
from erpnext.tests.utils import XGCERPTestSuite


class TestInit(XGCERPTestSuite):
	def test_encode_company_abbr(self):
		abbr = "NFECT"

		names = [
			"Warehouse Name",
			"XGCERP Foundation India",
			f"Gold - Member - {abbr}",
			f" - {abbr}",
			"XGCERP - Foundation - India",
			f"XGCERP Foundation India - {abbr}",
			f"No-Space-{abbr}",
			"- Warehouse",
		]

		expected_names = [
			f"Warehouse Name - {abbr}",
			f"XGCERP Foundation India - {abbr}",
			f"Gold - Member - {abbr}",
			f" - {abbr}",
			f"XGCERP - Foundation - India - {abbr}",
			f"XGCERP Foundation India - {abbr}",
			f"No-Space-{abbr} - {abbr}",
			f"- Warehouse - {abbr}",
		]

		for i in range(len(names)):
			enc_name = encode_company_abbr(names[i], abbr=abbr)
			self.assertTrue(
				enc_name == expected_names[i],
				f"{enc_name} is not same as {expected_names[i]}",
			)

	def test_translation_files(self):
		from frappe.tests.test_translate import verify_translation_files

		verify_translation_files("erpnext")

	def test_patches(self):
		from frappe.tests.test_patches import check_patch_files

		check_patch_files("erpnext")
