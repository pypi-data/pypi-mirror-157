import skvideo
import cv2
import sys
import imgstore
import yaml
import os
import os.path
import logging
import json
import scicam
from scicam.exceptions import ServiceExit

logger = logging.getLogger(__name__)

def parse_protocol(x):

    supported_protocols = ["tcp", "udp"]
    res = x.split("://")
    if len(res) == 2:
        protocol, url = res
    else:
        return None

    if protocol in supported_protocols:
        return (protocol, url)

    else:
        raise Exception(f"Protocol {protocol} not supported")


def read_config_yaml(path):
    with open(path, "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
    return config


def document_for_reproducibility():

    metadata = {
        "python-version": sys.version,
        "scicam-version": scicam.__version__,
        "imgstore-version": imgstore.__version__,  # for imgstore writer
        "skvideo-version": skvideo.__version__,  # for ffmpeg writer
        "cv2-version": cv2.__version__,
    }

    return metadata


def get_config_file():
    if os.path.exists("/etc/flyhostel.conf"):
        selected = "/etc/flyhostel.conf"
    else:
        selected = os.path.join(os.environ["HOME"], ".config", "flyhostel.conf")

    logger.info(f"Using configuration saved in {selected}")
    return selected


def load_config():
    with open(get_config_file(), "r") as fh:
        config = json.load(fh)

    return config



def service_shutdown(signum, frame):
    print("Caught signal %d" % signum)
    raise ServiceExit
