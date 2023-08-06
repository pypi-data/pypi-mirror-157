import datetime
import ipaddress
import re
from enum import Enum
from io import TextIOWrapper
from ipaddress import IPv4Network, IPv6Network
from typing import Union


class PolicyAction(Enum):
    NXDOMAIN = "."
    NODATA = "*."
    PASSTHRU = "rpz-passthru."
    TCP_ONLY = "rpz-tcp-only."
    DROP = "rpz-drop."
    LOCAL_DATA = "local-data."
    LOCALHOST = "localhost."
    NULL = "null."


class RecordType(Enum):
    A = 1
    AAAA = 28
    CNAME = 5
    NAPTR = 35
    PTR = 12
    SOA = 6
    SRV = 33
    TXT = 16


class RPZLib:
    def __init__(self, origin: str = ".rpz", policy_action: PolicyAction = PolicyAction.NXDOMAIN, policy_action_local_data_type: str = None,
                 policy_action_local_data: str = None, ttl: int = 300, mname: str = None, email: str = None, serial: int = None,
                 refresh: int = 14400, retry: int = 3600, expire: int = 1209600, negative_ttl: int = 3600):
        self.origin = origin
        self.policy_action = policy_action
        self.policy_action_local_data = policy_action_local_data
        self.policy_action_local_data_type = policy_action_local_data_type

        self.ttl = ttl
        self.mname = mname
        self.email = email
        if serial:
            self.serial = serial
        else:
            utc_now = datetime.datetime.utcnow()
            self.serial = int(utc_now.strftime("%y%m%d%H%M"))
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.negative_ttl = negative_ttl

    @staticmethod
    def _get_padding(value: str, padding_length) -> str:
        return " " * (padding_length - len(value))

    @staticmethod
    def _is_domain(address):
        domain_pattern = re.compile(
            r'^(([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)*'
            r'[a-z0-9][a-z0-9-]{0,61}[a-z])$'
        )
        return domain_pattern.match(address)

    @staticmethod
    def _parse_network(address):
        try:
            network = ipaddress.ip_network(address)
        except ValueError:
            return None

        return network

    @classmethod
    def _generate_rpz_record_raw(cls, domain: str, block_zone: bool = False,
                                 rdata: str = "", rr_type: RecordType = None):
        left_padding_length = (56 - len(domain))

        if left_padding_length < 3:
            left_padding_length = 3

        left_padding = " " * left_padding_length
        rdata_padding = " " * (10 - len(rr_type.name))

        entry = f"{domain}{left_padding}{rr_type.name}{rdata_padding}{rdata}\n"
        if block_zone:
            entry += f"*.{domain}{left_padding[:-2]}{rr_type.name}{rdata_padding}{rdata}\n"
        
        return entry

    @classmethod
    def generate_domain_entry(cls, domain: str, block_zone: bool = False,
                              policy_action: PolicyAction = PolicyAction.NXDOMAIN,
                              policy_action_local_data_type: RecordType = None, policy_action_local_data: str = None):
        policy_action_value = policy_action.value
        rr_type = RecordType.CNAME

        if policy_action == PolicyAction.LOCAL_DATA:
            if policy_action_local_data_type:
                rr_type = policy_action_local_data_type
            if policy_action_local_data:
                policy_action_value = policy_action_local_data

        if policy_action == PolicyAction.LOCALHOST:
            entry = cls._generate_rpz_record_raw(
                domain=domain,
                block_zone=block_zone,
                rdata='127.0.0.1',
                rr_type=RecordType.A
            )
            entry += cls._generate_rpz_record_raw(
                domain=domain,
                block_zone=block_zone,
                rdata='::1',
                rr_type=RecordType.AAAA
            )
        elif policy_action == PolicyAction.NULL:
            entry = cls._generate_rpz_record_raw(
                domain=domain,
                block_zone=block_zone,
                rdata='0.0.0.0',
                rr_type=RecordType.A
            )
            entry += cls._generate_rpz_record_raw(
                domain=domain,
                block_zone=block_zone,
                rdata='::',
                rr_type=RecordType.AAAA
            )
        else:  
            entry = cls._generate_rpz_record_raw(
                domain=domain,
                block_zone=block_zone,
                rdata=policy_action_value,
                rr_type=rr_type
            )

        return entry

    @classmethod
    def generate_network_entry(cls, network: Union[IPv4Network, IPv6Network],
                               policy_action: PolicyAction = PolicyAction.NXDOMAIN,
                               policy_action_local_data_type: RecordType = None, policy_action_local_data: str = None):
        raise NotImplementedError()

    @classmethod
    def generate_policy_entry(cls, address: str, block_zone: bool = False,
                              policy_action: PolicyAction = PolicyAction.NXDOMAIN,
                              policy_action_local_data_type: RecordType = None,
                              policy_action_local_data: str = None) -> str:
        if cls._is_domain(address):
            return cls.generate_domain_entry(
                domain=address,
                policy_action=policy_action,
                block_zone=block_zone,
                policy_action_local_data_type=policy_action_local_data_type,
                policy_action_local_data=policy_action_local_data
            )
        else:
            network = cls._parse_network(address)
            if network:
                return cls.generate_network_entry(
                    network=network,
                    policy_action=policy_action,
                    policy_action_local_data_type=policy_action_local_data_type,
                    policy_action_local_data=policy_action_local_data)

        return None

    def generate_header(self, origin) -> str:
        if origin[-1] != '.':
            origin += '.'

        padding_length = 11

        serial_padding = self._get_padding(str(self.serial), padding_length)
        refresh_padding = self._get_padding(str(self.refresh), padding_length)
        retry_padding = self._get_padding(str(self.retry), padding_length)
        expire_padding = self._get_padding(str(self.expire), padding_length)
        negative_ttl_padding = self._get_padding(
            str(self.negative_ttl), padding_length
        )

        mname = self.mname.lower() if self.mname else f"ns1.{origin}"
        email = self.email.lower() if self.email else f"hostmaster.{origin}"
        space = " " * 49

        return (
            f"$TTL {self.ttl}\n"
            f"$ORIGIN {origin}\n"
            f"@{space}IN    SOA       {mname} {email} (\n"
            f" {space}                    {self.serial}{serial_padding}; Serial Number\n"
            f" {space}                    {self.refresh}{refresh_padding}; Refresh Period\n"
            f" {space}                    {self.retry}{retry_padding}; Retry Period\n"
            f" {space}                    {self.expire}{expire_padding}; Expire Time\n"
            f" {space}                    {self.negative_ttl}{negative_ttl_padding}; Negative Caching TTL\n"
            f" {space}                )\n"
            f" {space}      NS        {mname}\n"
        )

    def list2rpz_pipe(self, input_stream: TextIOWrapper, output_stream: TextIOWrapper, block_zone: bool = False,
                      origin: str = None, policy_action: PolicyAction = None,
                      policy_action_local_data_type: RecordType = None, policy_action_local_data: str = None):
        if not origin:
            origin = self.origin
        if not policy_action:
            policy_action = self.policy_action
        if not policy_action_local_data_type:
            policy_action_local_data_type = self.policy_action_local_data_type
        if not policy_action_local_data:
            policy_action_local_data = self.policy_action_local_data

        output_stream.write(self.generate_header(origin.lower()))
        output_stream.write("\n")

        for entry in input_stream.readlines():
            policy_entry = self.generate_policy_entry(
                address=entry.rstrip().lower(),
                block_zone=block_zone,
                policy_action=policy_action,
                policy_action_local_data_type=policy_action_local_data_type,
                policy_action_local_data=policy_action_local_data
            )

            if policy_entry:
                output_stream.write(policy_entry)
