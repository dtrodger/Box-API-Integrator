from __future__ import annotations
import logging
import time
import os
from typing import AnyStr

import watchdog.observers.polling as wd_file_system_event_observer

import prometheus.box_client as prometheus_box_client
import prometheus.file_system.directory.directory as prometheus_directory
import prometheus.file_system.files.config_file as sentine_config_file
import prometheus.utils as bc_utils


log = logging.getLogger(__name__)


def fs_monitor_demo(env_alias: AnyStr) -> None:
    config_file = sentine_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start(
        "running fs_kkr_scanner_proxy", env_alias=env_alias
    )

    box_client = prometheus_box_client.prometheusBoxClient(config_file)
    user = box_client.user("9676033041")

    demo_box_folder = box_client.as_user(user).folder("97519158057").create_subfolder(bc_utils.instant_str())

    monitored_directory_path = os.path.join(
        os.path.dirname(__file__), config_file["file_system"]["demo_monitor_directory"]
    )
    monitored_directory = prometheus_directory.PrometheusDirectory(
        monitored_directory_path, ignored_files=[".DS_Store", ".gitkeep"]
    )

    archive_directory_path = os.path.join(
        os.path.dirname(__file__), config_file["file_system"]["demo_archive_directory"]
    )

    # Watchdog file system event observer and handlers
    # https://pythonhosted.org/watchdog/

    # Reference line 317 watchdog.events.FileSystemEventHandler
    # https://github.com/gorakhargosh/watchdog/blob/master/src/watchdog/events.py

    # Setup a Watchdog file system event observer and schedule the scanned doc and scan report directories for
    # monitoring.
    file_system_event_observer = wd_file_system_event_observer.PollingObserver()

    file_system_event_observer.schedule(
        monitored_directory, monitored_directory.file_system_path, recursive=True
    )

    # Start monitoring file system events
    file_system_event_observer.start()

    try:
        while True:

            # Iterate the Box upload files that were monitored in kkr_box_upload_directory
            for prometheus_file in monitored_directory.prometheus_files:

                # Check if the files failed upload to Box
                # For a file to be have failed Box upload
                #    enough time has elapsed since the file was initially monitored and the file is still on disk

                if prometheus_file.upload_to_box_failed():

                    # Move the scan_file into the archive directory and remove it from the virtual scan_dump_directory
                    log.info(f"File {str(prometheus_file)} failed Box upload")
                    prometheus_file.move_directories(archive_directory_path)
                    monitored_directory.remove_file(prometheus_file)

                # Check if the file is ready to upload to Box
                # For a file to be ready to upload it
                #    has been associated with a Box folder ID from XML path for upload
                #    has been associated with a Box user ID from XML to upload as_user
                #    has been completely written to disk
                if prometheus_file.is_ready_for_box_upload():

                    # Upload file to Box with Files API
                    # upload_to_box_as_user returns
                    #    a True boolean if the upload was successful
                    #    a string containing Box API errors if the upload failed
                    uploaded_to_box = prometheus_file.upload_to_box(
                        box_client,
                        box_upload_folder_id=demo_box_folder.response_object["id"],
                        box_user=user,
                    )

                    # uploaded_to_box = True
                    # # Delete the file if it was uploaded to Box
                    # if uploaded_to_box is True:
                    #     prometheus_file.delete()
                    #     monitored_directory.remove_file(prometheus_file)

            time.sleep(5)

    # Log why the process stopped
    except KeyboardInterrupt:
        log.info("user terminated process")
    except Exception as e:
        log.critical(f"process failure {str(e)}")

    box_client.as_user(user).folder(demo_box_folder.response_object["id"]).delete()

    # Stop the file system event observer's threads safely
    file_system_event_observer.stop()
    file_system_event_observer.join()
