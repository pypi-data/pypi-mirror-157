""""
directory_paths

Define functions to get common hydrogen directory paths.
"""
import os
import json
import datetime
import logging

def get_hydrodata_directory():
    """Returns the full path of the hydroframe /hydrodata directory containing large files."""
    result = os.environ.get("HYDRODATA", None)
    if not result or not os.path.exists(result):
        # If the HYDRODATA environment variable is not used use default
        result = "/hydrodata"

    return result


def get_hydro_common_directory():
    """Returns the common directory in /home/HYDROAPP/common that contains common static files for all users."""

    # The 'standard' place is different depending upon whether code is running on the client, the VM host or a Docker container
    # It is one of the directories specified by these environment variables
    result = None
    hydrocommon = os.environ.get("HYDROCOMMON", "")
    directory_options = [hydrocommon, "/hydrocommon", "/home/HYDROAPP/common"]
    for dirpath in directory_options:
        if os.path.exists(dirpath):
            result = dirpath
            break
    return result


def get_data_directory():
    """Returns the full path name of the data directory where files are stored, or None if not configured."""

    # The 'standard' place is different depending upon whether code is running on the client, the VM host or a Docker container
    # It is one of the directories specified by these environment variables
    result = None
    directory_env_variables = [
        "CONTAINER_HYDRO_DATA_PATH",
        "CLIENT_HYDRO_DATA_PATH",
        "HOST_HYDRO_DATA_PATH",
    ]
    for env_var in directory_env_variables:
        dirpath = os.environ.get(env_var, None)
        if dirpath is not None and os.path.exists(dirpath):
            result = dirpath
            break
    return result


def get_domain_path(message = None, user_id = None, domain_directory=None):
    """
    Returns the full path name to the domain directory.
    Use the user_id and domain_directory values in the message dict.
    """

    if message:
        user_id = message.get("user_id", None)
        domain_directory = message.get("domain_directory", None)

    if user_id is None:
        raise Exception("No user_id provided.")
    if domain_directory is None:
        raise Exception("No domain_directory provided.")
    domain_directory = domain_directory.lower()
    data_dir = get_data_directory()
    domain_path = f"{data_dir}/{user_id}/{domain_directory}"
    return domain_path


def get_domain_state(message = None, user_id = None, domain_directory=None):
    """
    Return the contents of the domain_state.json object of the domain directory.
    Use the user_id and domain_directory values in the message dict.
    """

    result = None
    if message:
        user_id = message.get("user_id", None)
        domain_directory = message.get("domain_directory", None)
    domain_path = get_domain_path(user_id=user_id, domain_directory=domain_directory)
    domain_state_name = f"{domain_path}/domain_state.json"
    database_name = f"{domain_path}/database.json"
    if os.path.exists(domain_state_name):
        with open(domain_state_name, "r") as stream:
            database = stream.read()
            result = json.loads(database)
    elif os.path.exists(database_name):
        # This is for backward compatibility until file name is changed
        with open(database_name, "r") as stream:
            database = stream.read()
            result = json.loads(database)
    # In case the directory was copied or moved put the actual user and directory in the returned state
    if result:
        result["user_id"] = user_id
        result["domain_directory"] = domain_directory
    return result

def update_domain_state(domain_state):
    """
        Update the domain state in the user domain directory with the attributes in the domain_state object.
        The domain_state object must contain at least the 'user_id' and 'domain_directory' attributes.
        Other attributes in the object are replaced in the domain state in the user domain directory.
        Attributes not provided in the domain_state object are unchanged in the user domain directory.
    """

    lock_file_name = ""
    try:
        user_id = domain_state.get("user_id", None)
        domain_directory = domain_state.get("domain_directory", None)
        if not user_id:
            raise Exception("No user_id in the domain state")
        if not domain_directory:
            # for backward compatibiilty with legacy domain_states
            domain_directory = domain_state.get("directory_name", None)
        if not domain_directory:
            raise Exception("No domain_directory in the domain state")
        domain_path = get_domain_path(user_id=user_id, domain_directory=domain_directory)
        database_name = f"{domain_path}/domain_state.json"
        lock_file_name = f"{database_name}.lck"
        database = {}

        # Create a lock file to protect against two processes writing at the same time
        with open(lock_file_name, "w+") as lock_stream:
            # Lock the lock file before we write the database file
            if not os.name == "nt":
                # fcntl only works on linux so no locking on windows...
                try:
                    import fcntl

                    fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except Exception as e:
                    raise Exception("Database was locked. Unable to save") from e

            if os.path.exists(database_name):
                # Read the previous contents of the database file first
                with open(database_name, "r") as read_stream:
                    contents = read_stream.read()
                    if contents:
                        database = json.loads(contents)
            with open(database_name, "w+") as write_stream:
                # Update the attributes from the incoming message, leave the rest alone
                if (
                    database.get("state", None) == "deleted"
                    and database.get("state_before_deleted", None)
                    and domain_state.get("state", None) == "new"
                ):
                    # When un-deleting a domain restore the previous state
                    domain_state["state"] = database.get("state_before_deleted", None)
                for attribute_name in [
                    "name",
                    "description",
                    "public",
                    "state",
                    "state_before_deleted",
                    "trained_date",
                    "notes",
                    "shape_regions",
                    "wgs84_bounds",
                    "grid_bounds",
                    "generated_scenarios",
                    "collected_observations",
                    "collected_current_conditions",
                    "error_message",
                    "conus1_bounds",
                    "conus2_bounds",
                    "visualizations"
                ]:
                    new_value = domain_state.get(attribute_name, None)
                    if new_value is not None and new_value != "":
                        database[attribute_name] = new_value
                if not database.get("state", None):
                    # If there is no state for the domain then set the state to 'new'
                    database["state"] = "new"
                if not database.get("created_date", None):
                    database["created_date"] = datetime.datetime.utcnow().strftime(
                        "%b %d %Y %H:%M:%S GMT-0000"
                    )

                # Put the actual directory name into the database
                database["directory_name"] = domain_directory
                database["domain_directory"] = domain_directory
                database["user_id"] = user_id
                # Save the updated file
                write_stream.write(json.dumps(database, indent=2))
        if os.path.exists(lock_file_name):
            os.remove(lock_file_name)
        return database
    except Exception as e:
        logging.exception("Unable to save domain database")
        if os.path.exists(lock_file_name):
            os.remove(lock_file_name)
        raise Exception("Unable to save domain database") from e


def get_domain_database(message):
    """
    Return the contents of the databse.json object of the domain directory.
    Use the user_id and domain_directory values in the message dict.
    This is deprecated. use get_domain_state() instead.
    """

    return get_domain_state(message)


def get_widget(message):
    """
    Return the visualization widget from the domain database associated with the
    domain and widget_id defined by the user_id, domain_directory and widget_id from
    the message dict.
    """

    result = None
    widget_id = message.get("widget_id", None)
    database = get_domain_database(message)
    if database is not None:
        for vis_index, vis in enumerate(database.get("visualizations", [])):
            for w_index, w in enumerate(vis.get("widgets", [])):
                if f"{vis_index}.{w_index}" == widget_id:
                    result = w
                    break
            if result:
                break
    return result
