import sys
from cStringIO import StringIO
from unittest import TestCase, main as unittest_main

import soya

class QuietTC(TestCase):

	def setUp(self):
		soya.quit()
		self._old_stdout = sys.stdout
		self.stdout = sys.stdout = StringIO()
		self._old_stderr = sys.stderr
		self.stderr = sys.stderr = StringIO()

	def test_quiet(self):
		if soya.inited:
			self.skip('Soya is already initialised')
		soya.init("test quiet init", quiet=True)
		self.assertEqual(self.stdout.getvalue(), '')
		self.assertEqual(self.stderr.getvalue(), '')

	def test_verbose(self):
		if soya.inited:
			self.skip('Soya is already initialised')
		soya.init("test verbose init", quiet=False)
		self.assertNotEqual(self.stdout.getvalue(), '')
		self.assertEqual(self.stderr.getvalue(), '')

	def test_default(self):
		if soya.inited:
			self.skip('Soya is already initialised')
		soya.init("test default init")
		self.assertNotEqual(self.stdout.getvalue(), '')
		self.assertEqual(self.stderr.getvalue(), '')

	def test_default_with_args(self):
		if soya.inited:
			self.skip('Soya is already initialised')
		soya.init("test default init", width=640, height=480)
		self.assertNotEqual(self.stdout.getvalue(), '')
		self.assertEqual(self.stderr.getvalue(), '')

	def tearDown(self):
		soya.quit()
		sys.stdout = self._old_stdout
		sys.stderr = self._old_stderr


if __name__ == '__main__':
	unittest_main()
