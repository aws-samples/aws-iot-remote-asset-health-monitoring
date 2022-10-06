#This python script runs AWS CLI commands and relies on the permissions on your AWS CLoud9 instance
import time
import json
from collections import namedtuple
import os
import subprocess as sp
import argparse


P4_PB_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id 6ecc0891-69f4-4de0-ab72-5d0841051f4c \
        --hierarchy-id ad577b8d-1d0a-477e-91f6-13c9225ddca2 \
        --child-asset-id {pumpingStation4_pumpB_ID}")
print(P4_PB_asset_association) 