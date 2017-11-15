# emctools
Tools for performing electromagnetic compatibility measurements.

# Conducted Emissions
`conducted_scan.py <pk|av|qp> <scan_name>` will perform a conducted emissions scan using a Rigol DSA815 connected to your PC via USB.
The script will configure the signal analyzer for the scan, conduct the scan, and save the results (including the CE limit line) to a csv file titled `<scan_name>.csv`.

## Quasi-Peak Scans
Given the speed of a quasi-peak scan, this script currently only performs a scan from 150-500kHz. You can adjust the upper frequency manually in the `det_qp` method.

## Dependencies
This script requires pyusb, pyserial, python-usbtmc, and numpy.

### Installation Instructions (Windows)
1. install python3 from https://www.python.org/ftp/python/3.6.3/python-3.6.3-amd64.exe
2. open powershell
3. `pip install pyserial`
4. `pip install pyusb`
5. `pip install numpy`
6. download https://github.com/python-ivi/python-usbtmc/archive/master.zip
7. extract the zip, and open powershell in the extracted directory
8. `python setup.py install`
9. plug in and power on your DSA815
10. download zadig from http://zadig.akeo.ie/downloads
11. run the executable
12. select the DSA815 in the drop-down
13. above the "install driver" button, select libusb-win32
14. press "install driver"
15. clone this repository and run the script.
