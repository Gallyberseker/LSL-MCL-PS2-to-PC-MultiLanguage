"""Interface des services de traitement des images pour Larry MCL."""
from LSL_MCL_IMAGE_CLASSEMENT import ClassementImages
from LSL_MCL_IMAGE_VALIDATION import ValidationImages
from LSL_MCL_IMAGE_SCAN import ScannerImages
from LSL_MCL_IMAGE_BMP import CodecBmp
from LSL_MCL_IMAGE_DXT import CodecDxt
from LSL_MCL_IMAGE_ENCODAGE import EncodageImages


class LSL_MCL_Images(ClassementImages, ValidationImages, ScannerImages, CodecBmp, CodecDxt, EncodageImages):
    """Expose le classement, la validation, le scan et les codecs d'images."""
