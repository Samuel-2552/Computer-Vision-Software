# import platform
# import psutil
# import netifaces
# import socket
# import wmi

# def get_system_info():
#     system_info = {}

#     # Basic System Information
#     system_info['System'] = platform.system()
#     system_info['Node Name'] = platform.node()
#     system_info['Release'] = platform.release()
#     system_info['Version'] = platform.version()
#     system_info['Machine'] = platform.machine()
#     system_info['Processor'] = platform.processor()

#     # Network Information
#     system_info['Hostname'] = socket.gethostname()
#     system_info['IP Address'] = socket.gethostbyname(socket.gethostname())

#     # CPU Information
#     cpu_info = {}
#     cpu_info['Physical Cores'] = psutil.cpu_count(logical=False)
#     cpu_info['Total Cores'] = psutil.cpu_count(logical=True)
#     cpu_info['CPU Frequencies'] = psutil.cpu_freq(percpu=True)

#     system_info['CPU'] = cpu_info

#     # Memory Information
#     mem_info = psutil.virtual_memory()
#     system_info['Memory'] = {
#         'Total': mem_info.total,
#         'Available': mem_info.available,
#         'Used': mem_info.used,
#         'Free': mem_info.free
#     }

#     # Disk Information
#     disk_info = {}
#     partitions = psutil.disk_partitions()
#     for partition in partitions:
#         try:
#             partition_info = psutil.disk_usage(partition.mountpoint)
#             disk_info[partition.device] = {
#                 'Total Size': partition_info.total,
#                 'Used': partition_info.used,
#                 'Free': partition_info.free,
#                 'File System Type': partition.fstype
#             }
#         except PermissionError:
#             continue

#     system_info['Disks'] = disk_info

#     return system_info

# # Get and print system information
# system_details = get_system_info()
# for category, details in system_details.items():
#     print(f"\n{category} Information:")
#     if isinstance(details, dict):
#         for item, value in details.items():
#             print(f"{item}: {value}")
#     else:
#         print(details)


# def get_mac_addresses():
#     mac_addresses = {}
#     interfaces = netifaces.interfaces()

#     for interface in interfaces:
#         try:
#             addresses = netifaces.ifaddresses(interface)[netifaces.AF_LINK]
#             mac_addr = addresses[0]['addr']
#             mac_addresses[interface] = mac_addr
#         except KeyError:
#             continue

#     return mac_addresses

# # Get and print MAC addresses
# mac_addresses = get_mac_addresses()
# print("\nMAC Addresses:")
# for interface, mac_addr in mac_addresses.items():
#     print(f"{interface}: {mac_addr}")

# def get_system_identifiers():
#     system_info = {}

#     try:
#         # Connect to Windows Management Instrumentation (WMI)
#         c = wmi.WMI()

#         # CPU ID
#         for processor in c.Win32_Processor():
#             system_info['CPU ID'] = processor.ProcessorId

#         # Hard Drive Serial Number
#         for disk in c.Win32_DiskDrive():
#             system_info['Hard Drive Serial Number'] = disk.SerialNumber

#         # Motherboard Serial Number
#         for board in c.Win32_BaseBoard():
#             system_info['Motherboard Serial Number'] = board.SerialNumber

#         # BIOS Information
#         for bios in c.Win32_BIOS():
#             system_info['BIOS Manufacturer'] = bios.Manufacturer
#             system_info['BIOS Version'] = bios.Version

#         # System UUID (Universally Unique Identifier)
#         for system in c.Win32_ComputerSystemProduct():
#             system_info['System UUID'] = system.UUID

#     except Exception as e:
#         print(f"Error: {e}")

#     return system_info

# # Get and print system identifiers
# system_identifiers = get_system_identifiers()
# print("\nSystem Identifiers:")
# for identifier, value in system_identifiers.items():
#     print(f"{identifier}: {value}")

import wmi 

def get_system_id():
    try:
        # Connect to Windows Management Instrumentation (WMI)
        c = wmi.WMI()
        # System UUID (Universally Unique Identifier)
        for system in c.Win32_ComputerSystemProduct():
            system_info = system.UUID
            print(type(system_info))

    except Exception as e:
        print(f"Error: {e}")
        system_info = "0"

    return system_info

print(get_system_id())