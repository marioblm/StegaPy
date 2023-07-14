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


    def encode_header(self,content_length, filetype, bits_per_pixel, use_all_channels, encrypted):
        """
        Encodes the header to be embedded in the medium.

        :param content_length: The length of the message.
        :param filetype: The filetype.
        :param bits_per_pixel: The number of bits used per pixel.
        :param use_all_channels: Whether or not to use all channels.
        :param encrypted: Whether or not the message is encrypted.

        :return: The encoded header data.
        """
        pass


    def decode_header(self, header):
        """
        Decodes the header data for later extraction of content.

        :param header: The encoded header.

        :return: A tuple containing the length of the message, the filetype,
                the number of bits per pixel, whether or not to use all channels,
                and whether or not the image is encrypted.
        """
        pass
