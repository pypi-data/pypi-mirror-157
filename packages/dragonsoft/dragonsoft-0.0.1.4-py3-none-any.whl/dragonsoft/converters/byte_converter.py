from functools import partial

class ByteConverter:
    def __init__(self):
        self.set_int_conversion()
        self.set_hex_conversion()
        self.set_str_conversion()
        
    def set_hex_conversion(self, pad_with_zero:bool=True, capitalize:bool=True,
                           default_bytesize:int=8):
        self._hex_pad_with_zero = pad_with_zero
        self._hex_capitalize = capitalize
        self._hex_default_bytesize = default_bytesize
        hex_format = "X" if self._hex_capitalize else "x"
        if self._hex_pad_with_zero:
            format_str = "{{int_value:0{{bytesize}}{hex_format}}}".format(hex_format=hex_format)
        else:
            format_str = "{{int_value:{hex_format}}}".format(hex_format=hex_format)
        self._hex_converter = partial(format_str.format, bytesize=self._hex_default_bytesize)
        
    def set_str_conversion(self, codec:str="mbcs"):
        self._str_codec = codec
        self._str_converter = lambda x: x.decode(self._str_codec)
    
    def set_int_conversion(self, byteorder:str="little"):
        self._byteorder = byteorder
        self._int_converter = partial(int.from_bytes, byteorder=self._byteorder)
    
    def to_int(self, byte_value):
        return self._int_converter(byte_value)
    
    def to_hex(self, byte_value, bytesize:int=8):
        int_value = self.to_int(byte_value)
        return self._hex_converter(int_value=int_value, bytesize=bytesize)
    
    def to_str(self, byte_value):
        return self._str_converter(byte_value)
    
    def int2hex(self, int_value:int, bytesize:int=8):
        return self._hex_converter(int_value=int_value, bytesize=bytesize)