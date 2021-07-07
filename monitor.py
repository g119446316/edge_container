import urllib.request
import psutil
import time
import subprocess
import os
import serial
import json
from datetime import datetime
import pytz
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad 


"""port = '/dev/ttyUSB0'
ard = serial.Serial(port,115200,timeout=3,
           parity=serial.PARITY_NONE,
           bytesize=serial.EIGHTBITS,
           stopbits=serial.STOPBITS_ONE)
"""

def get_total_info():
 while True:
  total_info = {}
  #cpu
  cpu_usage = psutil.cpu_percent(interval=1,percpu=True)
  cpu_freq = psutil.cpu_freq()

  for i in range(len(cpu_usage)):
    usage = { "CPU"+str(i+1) : cpu_usage[i] }
    total_info.update(usage)

  total_info.update({"cpu_freq" : cpu_freq[0]})

  #getloadavg 1,5,15m
  loadavg = psutil.getloadavg()
  total_info.update({"loadavg" : loadavg[2]})

  #memory
  mem = psutil.virtual_memory()
  total_info.update({"mem" : mem[2]})

  #gpu_usage
  gpu = subprocess.Popen(['cat', '/sys/devices/gpu.0/load'],stdout=subprocess.PIPE)
  gpu.wait()
  total_info.update({"GPU" : float(gpu.stdout.read())/10 })

  #fan_speed
  fan = subprocess.Popen(['cat', '/sys/devices/pwm-fan/target_pwm'],stdout=subprocess.PIPE)
  fan.wait()
  total_info.update({"fan" : int(fan.stdout.read()) })

  #AO-therm,CPU-therm,GPU-therm,PLL-therm,PMIC-Die,thermal-fan-est
  thermal_type = os.popen('cat /sys/devices/virtual/thermal/thermal_zone*/type')
  thermal_temp = os.popen('cat /sys/devices/virtual/thermal/thermal_zone*/temp')
  thermal_type_name = thermal_type.readlines()
  thermal_type_temp = thermal_temp.readlines()

  for i in range(len(thermal_type_name)):
     thermal_list = { str(thermal_type_name[i]).replace("\n","") : int(thermal_type_temp[i])/1000 }
     total_info.update(thermal_list)

  del total_info['PMIC-Die']

  #disk
  disk =  psutil.disk_usage('/')
  total_info.update({"disk" : disk[3] })
  total_info = {k.replace("-","_"): v for k,v in total_info.items()}

  #datetime
  asia = pytz.timezone('Asia/Taipei')
  cur_time = datetime.now(asia).strftime("%Y-%m-%d-%H:%M:%S")
  total_info.update({"time" : str(cur_time) })

  #network
  network_eth = os.popen('cat /sys/class/net/eth*/carrier')
  network_eth = network_eth.readlines()
  network_eth = int(network_eth[0])
  network_wlan = os.popen('cat /sys/class/net/wlan*/carrier')
  network_wlan = network_wlan.readlines()
  network_wlan = int(network_wlan[0])

  if network_eth == 1 :
    print("come1")
    try:
      response = urllib.request.urlopen('http://google.com',timeout=3)
      status = response.getcode()
      if status == 200:
         print("come2")
         total_info.update({"N" : "T" })
      else:
         total_info.update({"N" : "F" })
    except:
          pass
  else:
     total_info.update({"N" : "FC" })

  print(total_info)
  time.sleep(5)
  return total_info

def send_DMS():
  while os.path.exists("/dev/ttyUSB0")==True:
   port = '/dev/ttyUSB0'
   ard = serial.Serial(port,115200,timeout=3,
           parity=serial.PARITY_NONE,
           bytesize=serial.EIGHTBITS,
           stopbits=serial.STOPBITS_ONE
   if ard.isOpen():
      total_info = get_total_info()
      #update key name
      total_info['C1']=total_info.pop("CPU1")
      total_info['C2']=total_info.pop("CPU2")
      total_info['C3']=total_info.pop("CPU3")
      total_info['C4']=total_info.pop("CPU4")
      total_info['G']=total_info.pop("GPU")

      total_info['c_f']=total_info.pop("cpu_freq")
      total_info['L']=total_info.pop("loadavg")
      total_info['AO_t']=total_info.pop("AO_therm")
      total_info['C_t']=total_info.pop("CPU_therm")
      total_info['G_t']=total_info.pop("GPU_therm")
      total_info['PLL_t']=total_info.pop("PLL_therm")
      total_info['t_f_e']=total_info.pop("thermal_fan_est")

      total_info['D']=total_info.pop("disk")
      total_info['M']=total_info.pop("mem")
      total_info['F']=total_info.pop("fan")
      total_info['T']=total_info.pop("time")

      total_info = json.dumps(total_info).replace(" ","")

      total_info = total_info.encode('utf-8')
      total_info = pad(total_info,AES.block_size)
      print(len(total_info))

      a = "["
      b = "]"
      total_info = a.encode('utf-8') + total_info +b.encode('utf-8')
      print(total_info)

      ard.write(total_info)
      ard.flush()


if __name__ == '__main__' :
    while True:
      send_DMS()
