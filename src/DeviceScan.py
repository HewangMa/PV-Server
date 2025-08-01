import nmap
import socket


class DeviceScan:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.addr = socket.gethostbyname(self.hostname)
        self.ports_to_scan = ['80',  # http
                              '554',  # rtsp
                              '8017']  # ms
        ip_nums = self.addr.split('.')
        self.host_base = f"192.168.{ip_nums[2]}.0/24"
        self.scan_ports_arg = "-p "+','.join(self.ports_to_scan)
        print(f"running on device {self.addr}")

    def find_all_ip(self):
        nm = nmap.PortScanner()
        nm.scan(hosts=self.host_base, arguments=self.scan_ports_arg)
        res = []
        for host in nm.all_hosts():
            host_res = f"{host}"
            for port in self.ports_to_scan:
                port_n = int(port)
                if 'tcp' in nm[host] and port_n in nm[host]['tcp']:
                    port_info = nm[host]['tcp'][port_n]
                    host_res += f', port {port} {port_info['state']}'
            res.append(host_res)
        for one in res:
            print(one)


if __name__ == "__main__":
    DeviceScan().find_all_ip()
