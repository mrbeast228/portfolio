import os
import sane
import cups
import uuid

class MFU:
	def __init__(self, default='', dpi=300):
		# Init printer
		self.conn = cups.Connection()
		self.print_devices = []
		self.reload_print_devices()

		# Init scanner
		sane.init()
		self.scan_devices = []
		self.reload_scan_devices()

		# Set blank defaults
		self.default_print = None
		self.default_scan = None

		# Set default printer
		if default:
			self.set_default(default)

		# Set default DPI
		self.scan_dpi = dpi

	def reload_print_devices(self):
		self.print_devices = self.conn.getPrinters()

	def reload_scan_devices(self):
		self.scan_devices = sane.get_devices()

	def set_default(self, subname):
		# Set same printer for printing and scanning
		found_prints = [p for p in self.print_devices.keys() if subname in p]
		if not found_prints:
			raise Exception("Can't find specified printer!")
		self.default_print = found_prints[0]

		for p in self.scan_devices:
			p_name = p[0]
			for property in p:
				if subname in property:
					self.default_scan = p_name
					break
		if not self.default_scan:
			raise Exception("Can't find specified printer!")

	def print(self, filename):
		if not self.default_print:
			raise Exception("Default MFU doesn't set, can't print!")
		if not filename.endswith('.pdf'):
			raise ValueError("Files must be PDF!")

		# Check and print
		if len(self.conn.getJobs()) > 1:
			raise RuntimeError("Printer is busy!")
		self.conn.printFile(self.default_print, filename, str(uuid.uuid4()), {})

	def reset_cups(self):
		if self.default_print:
			os.system("cancel -a")
			os.system(f"cupsenable {self.default_print}")

	def scan(self, filename):
		if not self.default_scan:
			raise Exception("Default MFU doesn't set, can't scan!")
		if not filename.endswith('.pdf'):
			raise ValueError("Scans must be saved to PDF!")

		# Open and start
		dev = sane.open(self.default_scan)
		print(f"DEBUG: default DPI = {dev.resolution}")
		dev.resolution = self.scan_dpi
		dev.start()

		# Save to PDF
		im = dev.snap()
		pdf = im.convert('RGB')
		pdf.save(filename)

		dev.close()

