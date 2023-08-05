#!/data/data/com.termux/files/usr/bin/python3


class NetMath:

    """Class that holds methods to work with IP Addresses"""

    @staticmethod
    def _increment_address(ip_address: str):
        """Returns the next address of the address given"""
        octet4 = int(ip_address.split('.')[3])
        octet3 = int(ip_address.split('.')[2])
        octet2 = int(ip_address.split('.')[1])
        octet1 = int(ip_address.split('.')[0])
        
        octet4 += 1
        if octet4 > 255:
            octet4 = 0
            octet3 += 1
            if octet3 > 255:
                octet3 = 0
                octet2 += 1
                if octet2 > 255:
                    octet2 = 0
                    octet1 += 1

        inc_address = f"{octet1}.{octet2}.{octet3}.{octet4}"
        return inc_address
    
    @staticmethod
    def get_class(ip_address):
        """Sets class, normal bits, and regular subnet mask
        for ip address"""
        first_octet = int(ip_address.split('.')[0])
        if 0 <= first_octet < 127:
            return 'A'
        if 128 <= first_octet < 192:
            return 'B'
        if 192 <= first_octet < 224:
            return 'C'
        return None
    @staticmethod
    def get_visibility(ip_address: str):
        """Returns a string value either 'Public' or 'Private' depending
           on the address."""
        octet4 = int(ip_address.split('.')[3])
        octet3 = int(ip_address.split('.')[2])
        octet2 = int(ip_address.split('.')[1])
        octet1 = int(ip_address.split('.')[0])
        
        if (octet1 == 10 or
           (octet1 == 172 and 16 <= octet2 <= 31) or
           (octet1 == 192 and octet2 == 168)):
            return "Private"
        return "Public"
        
    @staticmethod
    def _is_binary(address: str):
        """Returns True if the address provided is in binary, else False"""
        if len(address) == (32+3):
            for octet in range(4):
                for bit in range(8):
                    if address.split('.')[octet][bit] not in ['0', '1']:
                        return False
            return True
        return False

    @staticmethod
    def _is_dec_ip_len(address: str):
        """Returns True if address provided is correct length, else False"""
        if (4+3) <= len(address) <= (12+3):
            return True
        return False

    @staticmethod
    def _pass_value_check(octet: str):
        """Returns True if the number string provided falls within
           the bounds of IP addresses, else False."""
        try:
            value = int(octet)
        except Exception:
            return False
        if 0 > value > 255:
            return False
        return True

    def is_valid_address(self, ip_addr: str):
        """Returns True if the string decimal IP address provided
           is a valid address, else returns False."""
        if not self._is_dec_ip_len(ip_addr):
            return False
        for octet in ip_addr.split('.'):
            if not self._pass_value_check(octet):
                return False
        return True

    @staticmethod
    def bin2dec(bin_num):
        """Returns a decimal string version of a binary number"""
        return str(int(bin_num,2))

    @staticmethod
    def dec2bin(num):
        """Returns a binary string of a base decimal number"""
        return format(int(num), "08b")

    def bin2ip(self, binary_ip: str):
        """Returns an IP address as a string when supplied
           with a binary address seperated by spaces"""
        octets = binary_ip.split('.')
        return '.'.join([self.bin2dec(octet) for octet in octets])

    def ip2bin(self, ip_addr: str):
        """Returns a binary IP address seperated by '.'s
           when provided with an IP address string"""
        octets = ip_addr.split('.')
        return '.'.join([self.dec2bin(octet) for octet in octets])

    @staticmethod
    def and_op(bin_ip1: str, bin_ip2: str):
        """Preforms an AND OPeration on the 2 binary addresses given.
           Returns the binary Network address, octets
           seperated by a '.', when supplied with the
           subnet mask and ip address in binary"""
        net_addr = []
        for octet in range(4):
            addr_chunk = ''
            for bit in range(8):
                if bin_ip1.split('.')[octet][bit] == '1' and\
                   bin_ip2.split('.')[octet][bit] == '1':
	                addr_chunk += '1'
                else:
	                addr_chunk += '0'
            net_addr.append(addr_chunk)
            addr_chunk = ''
        return '.'.join(net_addr)

    @staticmethod
    def cidr2bin(cidr_num: int):
        """Returns a representation of a subnetmask from
           CIDR notation number in the form of a binary IP"""
        bin_num = ''
        added = 0
        for bits in range(cidr_num):
            if added == 32:
                return bin_num
            if added % 8 == 0 and added != 0:
                bin_num += '.'
            bin_num += '1'
            added += 1
        while added <= 32:
            if added == 32:
                return bin_num
            if added % 8 == 0 and bin_num[-1] != '.':
                bin_num += '.'
            bin_num += '0'
            added += 1
            
    @staticmethod
    def bin2cidr(subnet_mask: str):
        """Returns the CIDR number when supplied with a subnet mask in binary"""
        return subnet_mask.count('1')
    
    @staticmethod
    def _get_normal_net_bits(ip_address: str):
        """Returns the normal amount of net bits for the given address' class"""
        first_octet = int(ip_address.split('.')[0])
        if 1 <= first_octet < 127:
            return 8
        if 128 <= first_octet < 192:
            return 16
        if 192 <= first_octet < 224:
            return 24
        return 0
    
    def get_amount_of_subnets(self, ip_address: str, subnet_mask: str):
        """Returns the amount of subnets when an IP address and subnet mask
           is provided."""
        norm_net_bits = self._get_normal_net_bits(ip_address)
        net_bits = self.bin2cidr(self.ip2bin(subnet_mask))
        borrowed_bits = net_bits - norm_net_bits
        subnets = 2 ** borrowed_bits
        return subnets
    
    def get_hosts_per_subnet(self, subnet_mask: str):
        """Returns the amount of hosts per subnet when provided with the
           subnet mask"""
        return 2 ** self.get_host_bits(subnet_mask)
    
    def get_subnet_mask(self, net_bits: int):
        """Returns subnet mask in the form of a decimal IP address
           when provided with the total number of net bits"""
        subnet_mask = self.bin2ip(self.cidr2bin(net_bits))
        return subnet_mask
    
    def get_host_bits(self, subnet_mask: str):
        """Returns the number of host bits as an integer when
           supplied with a string subnet mask"""
        return self.ip2bin(subnet_mask).count('0')
    
    def get_network_address(self, ip_addr: str, subnet_mask: str):
        """Returns network address of the provided IP and
           subnet mask in the form of a decimal IP address."""
        net_address = self.bin2ip(self.and_op(self.ip2bin(ip_addr),
	                                          self.ip2bin(subnet_mask)))
        return net_address
        
    def get_broadcast_address(self, ip_address, subnet_mask):
        """Returns broadcast address when supplied with
           an IP address and a subnet mask."""
        norm_net_bits = self._get_normal_net_bits(ip_address)
        net_bits = self.bin2cidr(self.ip2bin(subnet_mask))
        borrowed_bits = net_bits - norm_net_bits
        try:
            subnets = 2 ** borrowed_bits
            if isinstance(subnets, float):
                raise ValueError
        except ValueError:
            return "[!] Impossible subnet given [!]"
        host_bits = self.get_host_bits(subnet_mask)
        hosts_per_subnet = 2 ** host_bits
        net_address = self.get_network_address(ip_address, subnet_mask)
        
        found = False
        ip = net_address
        for net in range(subnets):
            #print(f"Subnet #{net+1}")
            for addr in range(hosts_per_subnet - 1):
                ip = self._increment_address(ip)
                #print("Checking", ip, "...")
                if ip == ip_address:
                    found = True
            if found:
                return ip
        return "0.0.0.0"

if __name__ == "__main__":
    nmath = NetMath()
    
    DEC_IP = "197.118.153.12"
    CIDR = 27
    SUBNET_MASK = nmath.get_subnet_mask(CIDR)
    
    print("Example:")
    print("\nGiven:")
    print(f"IP Address: {DEC_IP}")
    print(f"CIDR Notation: {CIDR}")
    print("="*56)
    print("Found:")
    print(f"Class            : {nmath.get_class(DEC_IP)}")
    print(f"Subnets          : {nmath.get_amount_of_subnets(DEC_IP, SUBNET_MASK)}")
    print(f"Hosts Per Subnet : {nmath.get_hosts_per_subnet(SUBNET_MASK)}")
    print(f"Visibility       : {nmath.get_visibility(DEC_IP)}")
    print(f"Network Address  : {nmath.get_network_address(DEC_IP, SUBNET_MASK)}")
    print(f"Broadcast Address: {nmath.get_broadcast_address(DEC_IP, SUBNET_MASK)}")
    print(f"Subnet Mask      : {SUBNET_MASK}")
    print(f"Binary Formatted : {nmath.ip2bin(DEC_IP)}")
