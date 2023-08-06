from typing import Optional

from ctypes import *
from ctypes.wintypes import *

OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

from dragonsoft.converters import ByteConverter

class ProcessMemoryScanner:
    def __init__(self, PID:int):
        self.processHandle = None
        self.open_process(PID)
        self.converter = ByteConverter()
    
    def open_process(self, PID:int):
        if self.processHandle is not None:
            self.close_handle()
        PROCESS_ALL_ACCESS = 0x1F0FFF
        processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, PID)
        self.processHandle = processHandle
    
    def close_handle(self):
        if self.processHandle is None:
            return None
        CloseHandle(self.processHandle)
        self.processHandle = None
        
    def get_bytes(self, lpBaseAddress:int, nSize:int=4):
        lpBuffer            = ctypes.create_string_buffer(nSize)
        lpNumberOfBytesRead = c_ulong(0)
        success = ReadProcessMemory(self.processHandle, lpBaseAddress, lpBuffer, nSize, byref(lpNumberOfBytesRead))
        if success:
            return lpBuffer.value
        else:
            print(f'ERROR: Failed to read memory from address "{self.converter.int2hex(lpBaseAddress)}"')
            return None
    
    def get_zero_terminated_bytes(self, lpBaseAddress:int, maxSize:int=36):
        byte_value = b""
        for i in range(maxSize):
            value = self.get_bytes(lpBaseAddress + i, nSize=1)
            if not value:
                break
            byte_value += value
        return byte_value
        
    def get_int(self, lpBaseAddress:int, nSize:int=4):
        byte_value = self.get_bytes(lpBaseAddress, nSize=nSize)
        if byte_value is not None:
            return self.converter.to_int(byte_value)
        return None
    
    def get_hex(self, lpBaseAddress:int, nSize:int=4):
        byte_value = self.get_bytes(lpBaseAddress, nSize=nSize)
        if byte_value is not None:
            return self.converter.to_hex(byte_value)
        return None
    
    def get_str(self, lpBaseAddress:int, maxSize:int=36):
        byte_value = self.get_zero_terminated_bytes(lpBaseAddress, maxSize=maxSize)
        return self.converter.to_str(byte_value)