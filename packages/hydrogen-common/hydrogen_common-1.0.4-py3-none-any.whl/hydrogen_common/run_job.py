"""
run_job.py

    Define functions to start an asynchonous job and to execute a job
    through an SSH tunnel from a client such as the API.
"""

import os
import asyncio
import logging
import json
import time
import requests

from .directory_paths import update_domain_state
from .use_message_bus import send_publish_message


def start_async_job(job_name, user_id, domain_directory, parameters=None):
    """Start an asyncrounous job to run in background."""

    job_server = os.environ.get("JOB_SERVER", None)
    job_server_port = os.environ.get("JOB_SERVER_PORT", None)
    nats_port = os.environ.get("NATS_PORT", None)

    if job_server and job_server_port:
        # An ssh tunnel is configured so use it to execute remote jobs
        pid = os.fork()
        if pid == 0:
            # This is the child process
            try:
                logging.info(
                    "Sent http request '%s' for '%s' of user '%s'.",
                    job_name,
                    domain_directory,
                    user_id,
                )
                run_remote_job(job_name, user_id, domain_directory, parameters)
            except Exception:
                logging.exception("Error when trying to run remote job")
                error_message = f"Unable to run job '{job_name}"
                domain_state = {
                    "user_id": user_id,
                    "domain_directory": domain_directory,
                    "state": "error",
                    "error_message": error_message,
                }
                update_domain_state(domain_state)
    elif nats_port:
        # A NATS port is configured to send a NATS message to Argo to execute remote job
        try:
            message = {"user_id": user_id, "domain_directory": domain_directory}
            if parameters:
                for key in parameters.keys():
                    value = parameters.get(key, None)
                    message[key] = value
            asyncio.run(send_publish_message(message, job_name))
            logging.info(
                "Published '%s' to NATS bus using '%s' for user '%s'",
                job_name,
                domain_directory,
                user_id,
            )
            logging.info(message)
        except Exception:
            logging.exception("Error when trying to run remote Argo job")
            error_message = f"Unable to run job '{job_name}"
            domain_state = {
                "user_id": user_id,
                "domain_directory": domain_directory,
                "state": "error",
                "error_message": error_message,
            }
            update_domain_state(domain_state)


def run_remote_job(job_name, user_id, domain_directory, parameters=None):
    """Start an job on a remote server using an ssh tunnel."""

    job_server = os.environ.get("JOB_SERVER", None)
    job_server_port = os.environ.get("JOB_SERVER_PORT", None)
    if job_server and job_server_port:
        url = f"http://{job_server}:{job_server_port}/run_job/{user_id}/{domain_directory}/{job_name}"
        if parameters:
            parameter_values = [
                f"{key}={parameters.get(key)}" for key in parameters.keys()
            ]
            url = url + "?" + "&".join(parameter_values)
        logging.info(url)
        start_time = time.time()
        response = requests.get(url)
        if not response.status_code == 200:
            message = response.text
            raise Exception("Job {job_name} failed with error: {message}")
        if response.text:
            response_json = json.loads(response.text)
            if response_json.get("status", None) == "fail":
                message = response_json.get("message", None)
                raise Exception(f"Job {job_name} failed with error: {message}")
        duration = round(time.time() - start_time, 2)
        logging.info("Completed '%s' job in %s seconds", job_name, duration)
    else:
        raise Exception("No configuration for executing remote job.")
