# NCM2
Multi-threaded configuration back-up script for networking devices.

Created using Netmiko, this python script pushes the "copy run tftp" command to networking devices by reading a list of IP addresses from a txt file. 

Back-ups stored on the TFTP Server "10.137.79.40"

Multi-threaded and connects to 8 devices at a time.

Reads and parses the hostname of the device connected to and uses that variable as the back-up filename along with the date.

Useful reference for an instance of the "expect_script" function due to multiple prompts from the cisco device.

Should the use of the script change, replace the "copy_command" variable with the cisco command of your choice and update the instances of the "expect_script" function to suit the situation, should prompts be expected.

TD
