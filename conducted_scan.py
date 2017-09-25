#!/usr/bin/env python3

import serial
import datetime, sys, time, math, os, glob
import usbtmc, usb
import numpy

class Analyzer(object):
	def __init__(self, *args, **kwargs):
		while True:
			try:
				self.instrument = usbtmc.Instrument(*args, **kwargs)
				self.instrument.timeout = .1
				info = self.ask("*IDN?").split(",")
				self.instrument.timeout = 1
				break
			except usb.core.USBError as e:
				if e.errno != 60:
					raise
		self.manufacturer = info[0]
		self.model = info[1]
	def reset(self):
		self.write("*RST")
	def wait(self, timeout):
		self.write("*OPC", timeout = None)
		self.ask("*OPC?", timeout = timeout)
	def write(self, query, timeout = 1):
		self.instrument.write(query)
		if timeout: self.wait(timeout)
	def ask(self, query, timeout = 1):		
		old_timeout = self.instrument.timeout
		self.instrument.timeout = timeout
		ret = self.instrument.ask(query)
		self.instrument.timeout = old_timeout
		return ret
	def calibrate(self):
		self.write(":CAL:ALL")
		self.ask("*OPC?", timeout = 10)
	def csv(self, filename, *traces):
		self.write(":FORM:TRAC:DATA ASC")
		trace_data = []
		headers = ["Frequency"]
		for trace in traces:
			data = self.ask(":TRACE:DATA? TRACE{}".format(trace))
			points = [point.strip(",") for point in data.split("  ")[1:]]
			trace_data.append(points)
			headers.append("Trace {}".format(trace))

		start = int(self.ask(":SENS:FREQ:START?"))
		stop = int(self.ask(":SENS:FREQ:STOP?"))
		frequency = numpy.logspace(numpy.log10(start), numpy.log10(stop), len(trace_data[0]))
		frequency = [str(int(numpy.floor(freq))) for freq in frequency]

		with open(filename, 'w') as f:
			f.write(",".join(headers))
			f.write("\n")
			for line in zip(frequency, *trace_data):
				f.write(",".join(line))
				f.write("\n")


def setup_conducted(sa):
	sa.write(":SENS:FREQ:STAR 150000")
	sa.write(":SENS:FREQ:STOP 30000000")
	sa.write(":UNIT:POW DBUV")

def limit_qp(sa):
	#Configure the limit line
	sa.write(":CONF:PF")
	sa.write(":CALC:LLIN:CONT:DOM FREQ")
	sa.write(":CALC:LLIN:FAIL:STOP:STAT OFF")
	sa.write(":CALC:LLIN2:DEL")
	sa.write(":CALC:LLIN1:DEL")
	sa.write(":CALC:LLIN1:STAT OFF")
	sa.write(":CALC:LLIN2:STAT ON")
	sa.write(":CALC:LLIN2:DATA 150000,66,0,500000,56,1,5000000,56,1,5000001,60,1,35000000,60,1")	
	sa.write(":calculate:lline2:control:interpolate:type logarithmic")

def limit_av(sa):
	#Configure the limit line
	sa.write(":CONF:PF")
	sa.write(":CALC:LLIN:CONT:DOM FREQ")
	sa.write(":CALC:LLIN:FAIL:STOP:STAT OFF")
	sa.write(":CALC:LLIN2:DEL")
	sa.write(":CALC:LLIN1:DEL")
	sa.write(":CALC:LLIN1:STAT OFF")
	sa.write(":CALC:LLIN2:STAT ON")
	sa.write(":CALC:LLIN2:DATA 150000,55,0,500000,46,1,5000000,46,1,5000001,50,1,35000000,50,1")	
	sa.write(":calculate:lline2:control:interpolate:type logarithmic")
	# sa.write(":CONF:PF OFF")
	# sa.write(":CONF:PF ON")

def det_qp(sa, sweeps):
	#Set up display
	sa.write(":DISP:WIN:TRAC:Y:SCAL:RLEV 85")
	sa.write(":DISP:WIN:TRAC:Y:SCAL:PDIV 5")
	sa.write(":DISP:WIN:TRAC:X:SCAL:SPAC LOG")	

	#Reduce upper frequency	
	sa.write(":SENS:FREQ:STOP 500000")	

	#Set up detector
	sa.write(":SENS:BAND:EMIF:STAT ON")
	sa.write(":SENS:BAND:RES 9000")
	sa.write(":SENS:BAND:VID 30000")
	sa.write(":SENS:DET:FUNC QPE")
	sa.write(":SENS:POW:RF:ATT 20")

	#Set up sweep
	sa.write(":SENS:SWE:TIME ON")
	sa.write(":SENS:SWE:TIME:AUTO:RUL ACC")
	sa.write(":INIT:CONT OFF")

	#Max hold
	sa.write(":TRAC1:MODE MAXH")

def det_pk(sa, sweeps):
	#Set up display
	sa.write(":DISP:WIN:TRAC:Y:SCAL:RLEV 85")
	sa.write(":DISP:WIN:TRAC:Y:SCAL:PDIV 5")
	sa.write(":DISP:WIN:TRAC:X:SCAL:SPAC LOG")		

	#Set up detector
	sa.write(":SENS:BAND:EMIF:STAT ON")
	sa.write(":SENS:BAND:RES 9000")
	sa.write(":SENS:BAND:VID 30000")
	sa.write(":SENS:DET:FUNC POS")
	sa.write(":SENS:POW:RF:ATT 20")

	#Set up sweep
	sa.write(":SENS:SWE:TIME ON")
	sa.write(":SENS:SWE:TIME:AUTO:RUL NORM")
	sa.write(":INIT:CONT OFF")

	#Max hold
	sa.write(":TRAC1:MODE BLANK")
	sa.write(":TRAC1:MODE MAXH")

def det_av(sa, sweeps):	
	#Set up display
	sa.write(":DISP:WIN:TRAC:Y:SCAL:RLEV 75")
	sa.write(":DISP:WIN:TRAC:Y:SCAL:PDIV 5")
	sa.write(":DISP:WIN:TRAC:X:SCAL:SPAC LOG")		

	#Set up detector
	sa.write(":SENS:BAND:EMIF:STAT ON")
	sa.write(":SENS:BAND:RES 9000")
	sa.write(":SENS:BAND:VID 30000")
	sa.write(":SENS:DET:FUNC POS")
	sa.write(":SENS:POW:RF:ATT 20")

	#Set up sweep
	sa.write(":SENS:SWE:TIME ON")
	sa.write(":SENS:SWE:TIME:AUTO:RUL NORM")
	sa.write(":INIT:CONT OFF")

	#Video average the sweeps
	sa.write(":TRAC1:MODE VID")
	sa.write(":TRAC1:AVER:COUNT {}".format(sweeps))

def measure(sa, limit, detector, sweeps):
	setup_conducted(sa)
	# sa.wait(10)
	detector(sa, sweeps)
	# sa.wait(10)
	limit(sa)
	# sa.wait(10)

	sa.write(":SENS:SWE:COUN {}".format(sweeps))

	#Start the sweep 	
	sweep_time = float(sa.ask(":SENSE:SWEEP:TIME?"))
	start_time = time.monotonic()
	total_m, total_s = divmod(sweep_time*sweeps, 60)
	sa.write(":INIT:IMM", timeout = None)

	#Wait for the sweep to finish
	count = 0
	while count < sweeps:
		count = int(sa.ask(":SENSE:SWEEP:COUNT:CURRENT?", timeout = sweep_time*1.1))
		m, s = divmod(time.monotonic() - start_time, 60)
		print("\r[{:02d}:{:02d}/{:02d}:{:02d}] sweep {}/{}".format(int(m), int(s), int(total_m), int(total_s), count, sweeps), end = '')
		time.sleep(1)


def main():
	scan_type = sys.argv[1]
	scan_name = sys.argv[2]

	instr = Analyzer(0x1ab1, 0x0960, term_char = ord('\n'))
	print("Connected to", instr.manufacturer, instr.model)

	instr.reset()

	#Perform calibration so it doesn't interrupt our scan
	print("Calibrating...")
	instr.calibrate()
	# wait(instr, 60)

	print("Performing", scan_type, "scan.")

	if scan_type == "pk":
		measure(instr, limit_qp, det_pk, 200)
	elif scan_type == "av":
		measure(instr, limit_av, det_av, 100)
	elif scan_type == "qp":
		measure(instr, limit_qp, det_qp, 10)
	else:
		print(scan_type, "scan unsupported")

	print("Saving trace to {}.csv...".format(scan_name))
	instr.csv("{}.csv".format(scan_name), 1, 2)

if __name__ == "__main__":
	main()
	




