# Gathering running-configuration from Cisco swithces (CatOS & IOS)

  - Telnet to swithces and send a command to gather running-configuration  
  \* Telnet is used since some of the swithces are running old version code  


## Device List file (Tab delimited)
10.4.20.16 CatOS Switch1  
10.4.20.100 IOS Switch2

## Main Logic of this script  
  - Read a device list file  
  - Access to the device  
  - Send a command either <em><strong>sh run</strong></em> or <em><strong>sh config all</strong></em> depends on the device
  - Save as a txt file
  - Compress the multiple files
