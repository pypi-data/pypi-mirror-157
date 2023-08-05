import base64
import mmh3
import re

from datetime import datetime
from bitarray import bitarray
from typing import Optional, List

COMBINATIONS = [
    ('ssn', 'first_name', 'last_name'),
    ('ssn', 'last_name', 'date_of_birth'),
    ('ssn', 'last_name', 'phone_number'),
    ('ssn', 'last_name', 'email_address'),
    ('ssn', 'date_of_birth', 'phone_number'),
    ('ssn', 'date_of_birth', 'email_address'),
    ('last4ssn', 'last_name', 'date_of_birth'),
    ('last4ssn', 'last_name', 'phone_number'),
    ('last4ssn', 'last_name', 'email_address'),
    ('last_name', 'date_of_birth', 'phone_number'),
    ('last_name', 'date_of_birth', 'email_address'),
    ('date_of_birth', 'phone_number', 'email_address'),
]

BIT_ARRAY_SIZE = 60
HAMMING_WEIGHT = 30

class InputError(BaseException):
    pass


class FintechFraudDAOHashing:

    def __init__(self, first_name: Optional[str] = None,
                 last_name: Optional[str] = None,
                 date_of_birth: Optional[datetime] = None,
                 phone_number: Optional[str] = None,
                 email_address: Optional[str] = None,
                 ssn: Optional[str] = None,
                 last4ssn: Optional[str] = None) -> None:

        self.first_name = first_name and first_name.lower().strip() or None
        self.last_name = last_name and last_name.lower().strip() or None
        self.date_of_birth = date_of_birth and date_of_birth.strftime('%Y-%m-%d') or None
        self.phone_number = phone_number and ''.join(re.findall(r'\d+', phone_number.split('x')[0])) or None
        self.email_address = email_address and email_address.lower().strip() or None
        if ssn:
            self.ssn = ''.join(re.findall(r'\d+', ssn))
            if len(self.ssn) != 9:
                raise InputError('ssn should be 9 digits')
        else:
            self.ssn = None
        if last4ssn:
            self.last4ssn = ''.join(re.findall(r'\d+', last4ssn))
            if len(last4ssn) != 4:
                raise InputError('last4ssn should be 4 digits')
        else:
            self.last4ssn = None
        if ssn and not last4ssn:
            self.last4ssn = ssn[-4:]

    @staticmethod
    def _generate_hash(value: str) -> str:
        bf = bitarray(BIT_ARRAY_SIZE)
        bf.setall(0)
        for seed in range(HAMMING_WEIGHT):
            result = mmh3.hash(value, seed) % BIT_ARRAY_SIZE
            bf[result] = 1
        return base64.b64encode(bf.tobytes()).decode('utf8')

    def generate_hashes(self) -> List[str]:
        result = []
        for c in COMBINATIONS:
            if all(self.__getattribute__(v) for v in c):
                result.append(self._generate_hash(''.join([self.__getattribute__(v) for v in c])))
        return result