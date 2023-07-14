# StegaPY
Steganography using Least Significat Bit Substituation on images.

Messages are embedded using one or more bits across one or all channels. A header at the beginning of the file identifies the settings, length and filetype of the message.

## Installation

To install the required packages, run:

```bash
pip install -r requirements.txt
```

## Usage

```bash
usage: main.py [-h] [-k KEY] [-o OUTPUT] {hide,reveal} input_file [file_to_be_hidden]

SteganoPy - Hide data inside of images

positional arguments:
  {hide,reveal}         Method to execute
  input_file            Filename of medíum
  file_to_be_hidden     (Optional) File to be hidden (only needed when hiding)

optional arguments:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     (Optional) AES key
  -o OUTPUT, --output OUTPUT
                        (Optional) Filename of result
```

## Example

To encode a message in an image, run:

```bash
python main.py hide image.png message.txt -o encoded
```


To decode the message from the encoded image, run:

```bash
python main.py reveal encoded.png -o decoded
```

## Header
Contains information on content-length, nr. of bits per channel, file-extention, encryption and nr. of channels used.

While the lenght can be altered the default assignment is:
|Variable   |Length(bits)   |Range/Values   |
|---|---|---|
|content-length  |24   |up to 2.1MB (including Overhead)|
|file-extention  |24   |1-3 UTF-8 Characters    |
|bits per channel|2    |1-4 Bits per Channel   |
|channels used   |1    |1/3 Channels   |
|encryption  |1    |yes/no   |

The header is always stored using the last bit and accross 3 channels of the (PNG) Image.
Therefore the 52 bits use the first 17 1/3 pixels of the output image.
### Example:
|Size   |Filetype   |Bits   |All Channels|Encryption|
|---|---|---|---|---|
|1474336 bits|P D F|1|No|No|
|000101100111111100100000|01110000 01100100 01100110|00|0|0|