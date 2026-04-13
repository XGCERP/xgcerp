from erpnext.tests.utils import AXERPTestSuite
from erpnext.utilities.activation import get_level


class TestActivation(AXERPTestSuite):
	def test_activation(self):
		site_info = {"activation": {"activation_level": 0, "sales_data": []}}
		levels = get_level(site_info)
		self.assertTrue(levels)
