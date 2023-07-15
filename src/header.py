from .bitutils import *

class HeaderUtils:
    _instance = None
    
    def __init__(self, cl_bits=24, ft_bytes=3, bpp=2):
        """
        Initializes a new instance of the HeaderUtils class.

        :param cl_bits: The number of bits used to represent the content length.
        :param ft_bytes: The number of bytes used to represent the filetype.
        :param bpp: The number of bits used to represent the bits per pixel.
        """
        self.filetype_bytes = ft_bytes
        self.content_length_bits = cl_bits
        self.bits_per_pixel = bpp

        self.max_bits_per_pixel = 2**self.bits_per_pixel
        self.max_filesize = 2**self.content_length_bits - 1
        self.header_length = cl_bits + ft_bytes * 8 + bpp + 2


    @classmethod
    def instance(cls, cl_bits=24, ft_bytes=3, bpp=2):
        """
        Returns the instance of the Singleton class if it exists, otherwise creates a new instance.

        :param cl_bits: The number of bits used to represent the content length.
        :param ft_bytes: The number of bytes used to represent the filetype.
        :param bpp: The number of bits used to represent the bits per pixel.

        :return: The instance of the Singleton class.
        """
        if cls._instance is None:
            cls._instance = cls(cl_bits, ft_bytes, bpp)
        return cls._instance


    def check_compatibility(self, content_length, filetype, bits_per_pixel):
        """ 
        Checks if the input parameters are compatible with the header format.

        :param content_length: The length of the message.
        :param filetype: The filetype.
        :param bits_per_pixel: The number of bits used per pixel.

        :raises: TypeError if any of the parameters are the wrong type.
        :raises: OverflowError if any of the parameters are out of range.
        """
        if not isinstance(content_length, int):
            raise TypeError("content_length should be an int")
        if not isinstance(bits_per_pixel, int):
            raise TypeError("bits_per_pixel should be an int")
        if not isinstance(filetype, str):
            raise TypeError("filetype should be a string")
        if self.filetype_bytes == 0 or len(filetype) > self.filetype_bytes:
            raise OverflowError("Filetype too long for header, max is {} bytes - was given {}".format(self.filetype_bytes, len(filetype)))
        if self.content_length_bits == 0 or content_length > self.max_filesize:
            raise OverflowError("Content too large for header, max is {} bits - was given {}".format(self.max_filesize, content_length))
        if bits_per_pixel == 0 or bits_per_pixel > self.max_bits_per_pixel:
            raise OverflowError("Unsupported bits per pixel, was given {} - range is [1,{}]".format(bits_per_pixel, self.max_bits_per_pixel))


    def encode_header(self, content_length, filetype, bits_per_pixel, use_all_channels, encrypted):
        """
        Encodes the header to be embedded in the medium.

        :param content_length: The length of the message.
        :param filetype: The filetype.
        :param bits_per_pixel: The number of bits used per pixel.
        :param use_all_channels: Whether or not to use all channels.
        :param encrypted: Whether or not the message is encrypted.

        :return: The encoded header data.
        """
        self.check_compatibility(content_length, filetype, bits_per_pixel)
        length = "{0:b}".format(content_length).zfill(self.content_length_bits)
        filetype = ''.join(string2bits(filetype)).zfill(self.filetype_bytes * 8)
        bits = "{0:b}".format((bits_per_pixel-1)).zfill(self.bits_per_pixel)
        header = length + filetype + bits
        header += "1" if use_all_channels else "0"
        header += "1" if encrypted else "0"
        return header


    def decode_header(self, header):
        """
        Decodes the header data for later extraction of content.

        :param header: The encoded header.

        :return: A tuple containing the length of the message, the filetype,
                the number of bits per pixel, whether or not to use all channels,
                and whether or not the image is encrypted.
        """
        all_binary = all(c in '01' for c in header)
        if not all_binary:
            raise ValueError("Invalid characters in header")
        if len(header) != self.header_length:
            raise ValueError("Mismatched header size")
        length = int(header[:self.content_length_bits], 2)
        filetype = bits2string(header[self.content_length_bits:self.content_length_bits + self.filetype_bytes * 8])
        # remove null character (present on shorter filetypes)
        filetype = filetype.replace('\x00', '')
        bits = int(header[-(self.bits_per_pixel + 2):-2], 2) + 1
        all_channels = header[-2] == '1'
        encrypted = header[-1] == '1'
        return length, filetype, bits, all_channels, encrypted
