"""
Bitbucket CLI - A command-line interface for Bitbucket repositories.
"""

from .bitbucket import BitBucketClient, BitBucketClientError
from .main import app

__version__ = "1.0.0"
__author__ = "Md Minhazul Haque"
__email__ = "mdminhazulhaque@gmail.com"

__all__ = ["BitBucketClient", "BitBucketClientError", "app"]
