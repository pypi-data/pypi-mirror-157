import argparse
import multiprocessing
import threading
import sys
import time
import os.path
import signal
import traceback

import numpy as np
import pandas as pd
import yaml

import logging
import logging.config
from scicam.constants import LOGGING_CONFIG

with open(LOGGING_CONFIG, 'r') as filehandle:
    config = yaml.load(filehandle, yaml.SafeLoader)
    logging.config.dictConfig(config)


from EasyROI import EasyROI

from scicam.io.cameras.__main__ import get_parser as flir_parser
from scicam.io.cameras.__main__ import setup as setup_camera
from scicam.io.cameras.basler.parser import get_parser as basler_parser
from scicam.io.cameras import CAMERAS
from scicam.constants import CAMERA_INDEX
from scicam.io.recorders.parser import get_parser as recorder_parser
from scicam.web_utils.sensor import setup as setup_sensor
from scicam.core.monitor import Monitor
from scicam.core.monitor import run as run_monitor
from scicam.exceptions import ServiceExit
from scicam.utils import load_config, service_shutdown


logger = logging.getLogger(__name__)


def get_parser(ap=None):

    if ap is None:
        ap = argparse.ArgumentParser(conflict_handler="resolve")

    ap.add_argument(
        "--cameras",
        nargs="+",
        required=True,
        choices=CAMERAS,
        default=None,
    )
    ap.add_argument(
        "--flir-exposure",
        dest="flir_exposure",
        type=int,
        default=9900,
        help="Exposure time in microseconds of the Flir camera",
    )
    ap.add_argument(
        "--basler-exposure",
        dest="basler_exposure",
        type=int,
        default=25000,
        help="Exposure time in microseconds of the Basler camera",
    )
    ap.add_argument(
        "--flir-framerate",
        type=int,
        default=100,
        help="Frames Per Second of the Flir camera",
    )
    ap.add_argument(
        "--basler-framerate",
        type=int,
        default=30,
        help="Frames Per Second of the Basler camera",
    )
    ap.add_argument(
        "--sensor",
        type=int,
        default=9000,
        help="Port of environmental sensor",
    )
    ap.add_argument(
        "--select-rois",
        default=False,
        action="store_true",
        dest="select_rois",
        help="""
        Whether a region of interest (ROI)
        of the input should be cropped or not.
        In that case, a pop up will show for the user to select it
        """,
    )
    ap.add_argument(
        "--rois",
        default=None,
        type=str
    )
    return ap


def get_queue(process, queues):
    if process in queues and not queues[process].empty():
        timestamp, frame = queues[process].get()
        return timestamp, frame
    else:
        return (None, np.uint8())

def get_config_file():
    if os.path.exists("/etc/flyhostel.conf"):
        return "/etc/flyhostel.conf"
    else:
        return os.path.join(os.environ["HOME"], ".config", "flyhostel.conf")



def separate_process(
    camera_name,
    output,
    format,
    sensor=None,
    stop_queue=None,
    process_id=0,
    rois=None,
    camera_idx=0,
    start_time=None,
    chunk_duration=300,
):
    logger.info("multiprocess.Process - scicam.bin.__main__.separate _process")

    monitor = Monitor(
        camera_name=camera_name,
        camera_idx=camera_idx,
        path=output,
        format=format,
        start_time=start_time,
        stop_queue=stop_queue,
        sensor=sensor,
        rois=rois,
        select_rois=False,
        chunk_duration=chunk_duration,
    )


    logger.info(f"Monitor start time: {start_time}")

    monitor.process_id = process_id
    try:
       run_monitor(monitor)
    except Exception as error:
        logger.error(error)
        logger.error(traceback.print_exc())
    # kwargs to to monitor.open


def setup_and_run(args):
    sensor = setup_sensor(args.sensor)
    config = load_config()
    import queue

    Job = threading.Thread
    queue_function = queue.Queue

    processes = {}
    stop_queues = []
    root_output = os.path.join(config["videos"]["folder"], args.output)

    # this start time will be shared by all cameras running in parallel
    start_time = time.time()

    try:
        with open(CAMERA_INDEX, "r") as filehandle:
            camera_index = yaml.load(filehandle, yaml.SafeLoader)
    except Exception as error:
        logger.warning(error)
     
    roi_helper = EasyROI(verbose=True)

    for i, camera_name in enumerate(args.cameras):
        camera_idx = camera_index[camera_name]
        queue = multiprocessing.Queue(maxsize=1)

        if camera_name == "FlirCamera":
            output = os.path.join(root_output, "lowres")
        else:
            output = root_output

        if args.select_rois:

            camera = CAMERAS[camera_name](
                start_time=start_time,
                roi_helper=roi_helper,
                resolution_decrease=args.resolution_decrease,
                idx=camera_idx,
            )

            logger.info(f"Selecting rois for {camera}")
            if args.select_rois:
                rois = camera.select_ROIs()
            # save the roi and somehow give it to the next instance
            camera.close()

        elif args.rois is not None:
            # TODO Make a function out of this
            roi_data = pd.read_csv(args.rois)
            assert all([col in roi_data.columns for col in ["x", "y", "w", "h", "camera_name"]])
            roi_data = roi_data.loc[roi_data["camera_name"] == camera_name]
            rois = [(row.x, row.y, row.w, row.h) for i, row in roi_data.iterrows()]

        else:
            rois = None

        # kwargs = {"recorder": recorder, "format": args.format, "path": output}
        stop_queue = queue_function(maxsize=1)
        
        
        kwargs = {
            "sensor": sensor,
            "stop_queue": stop_queue,
            "process_id": i,
            "rois": rois,
            "camera_idx": camera_idx,
            "start_time": start_time,
            "chunk_duration": args.chunk_duration
        }

        p = Job(
            target=separate_process,
            name=camera_name,
            args=(camera_name, output, args.format),
            kwargs=kwargs,
            daemon=True,
        )
        processes[camera_name] = p
        stop_queues.append(stop_queue)

    try:
        logger.debug(f"Starting {len(processes)} processes")
        run_processes(processes, stop_queues)
    except KeyboardInterrupt:
        return


def run_processes(processes, stop_queues):

    if "FlirCamera" in processes:
        processes["FlirCamera"].start()
    # give time for the Flir process to start
    # before Basler does.
    # Otherwise Basler starts before and crashes when Flir does

    if "FlirCamera" in processes and "BaslerCamera" in processes:
        time.sleep(5)
    if "BaslerCamera" in processes:
        processes["BaslerCamera"].start()
    time.sleep(1)

    try:
        for p in processes.values():
            p.join()
    except ServiceExit:
        print(
            """
          Service Exit captured.
          Please wait until processes finish
        """
        )
        for stop_queue in stop_queues:
            stop_queue.put("STOP")

        for p in processes.values():
            p.join()
        sys.exit(0)

    if all([not p.is_alive() for p in processes.values()]):
        sys.exit(0)


def main(args=None, ap=None):

    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    if args is None:
        if ap is None:
            ap = get_parser()
            ap = basler_parser(ap=ap)
            ap = flir_parser(ap=ap)
            ap = recorder_parser(ap)
        args = ap.parse_args()

    setup_and_run(args)


if __name__ == "__main__":
    main()
