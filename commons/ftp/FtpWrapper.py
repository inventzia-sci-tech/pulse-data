import configparser
import ftplib
import os
import time
import pandas as pd
from datetime import datetime
from logging import Logger
from commons.parametrization.PythonParametrization import PythonParametrization


class FtpWrapperParameters(PythonParametrization):
    '''
        Parametrization of an Ftp wrapper.
    '''

    default_ftp_section: str = 'FTP_DETAILS'
    ftp_section : str = None
    ftp_server  : str = None
    ftp_username: str = None
    ftp_password: str = None
    constant_attempts = 2 # Todo make it a facultative params
    constant_sleep_secs_between_attempts = 5 # Todo make it a facultative params


    def __init__(self, config_ini_file: str = None,
                 config_parser: configparser = None,
                 config_df: pd.DataFrame = None,
                 ftp_section: str = None, # If none will use the default
                 ):
        if ftp_section is not None:
            self.ftp_section = ftp_section
        else:
            self.ftp_section = self.default_ftp_section
        super().__init__(config_ini_file, config_parser, config_df)


    def parse_parameters(self, config_parser : configparser):
        self.ftp_server = config_parser.get(self.ftp_section, 'ftp_server')
        self.ftp_username = config_parser.get(self.ftp_section, 'ftp_username')
        self.ftp_password = config_parser.get(self.ftp_section, 'ftp_password')


    def add_required_sections_and_parameters_in_lists(self):
        self.add_required_section_parameter(self.ftp_section, 'ftp_server')
        self.add_required_section_parameter(self.ftp_section, 'ftp_username')
        self.add_required_section_parameter(self.ftp_section, 'ftp_password')



class FtpWrapper:

    '''
        Parametrization of an Ftp wrapper.Wrap an ftp connection. giving simple functionalities
    '''

    def __init__(self,
                 params : FtpWrapperParameters,
                 logger : Logger = None):
        """
        Initialize FTP wrapper with configuration
        :param params: FtpWrapperParameters object with FTP credentials
        :param ftp_section: Section name in config file
        :raises KeyError: If required config keys are missing
        """
        self.ftp_params = params
        self.ftp_connection = None
        self.logger = logger


    def _log(self, msg : str):
        if self.logger is not None:
            self.logger.info(msg)
        else:
            print(msg)

    def connect_to_ftp(self) -> (bool, str):
        """
        Connects to a FTP server with retry logic
        :return: tuple of (success: bool, message: str)
        """
        # Close existing connection if any
        if self.ftp_connection is not None:
            try:
                self.ftp_connection.quit()
            except:
                pass
            self.ftp_connection = None

        for attempt in range(1, self.ftp_params.constant_attempts + 1):
            try:
                ftp = ftplib.FTP(timeout=300)
                ftp.connect(self.ftp_params.ftp_server)
                ftp.login(self.ftp_params.ftp_username, self.ftp_params.ftp_password)
                self.ftp_connection = ftp
                msg =  f"Successfully connected to {self.ftp_params.ftp_server}"
                self._log(msg)
                return (True,msg)
            except ftplib.all_errors as e:
                error_msg = f"Attempt {attempt}/{self.ftp_params.constant_attempts} failed: {str(e)}"
                if attempt < self.ftp_params.constant_attempts:
                    time.sleep(self.ftp_params.constant_sleep_secs_between_attempts)
                else:
                    msg = f"Failed to connect after {self.ftp_params.constant_attempts} attempts. Last error: {str(e)}"
                    self._log(msg)
                    return (False, msg)

        msg =  "Failed to connect to FTP server"
        self._log(msg)
        return (False, msg)


    def disconnect(self) -> (bool, str):
        """
        Disconnect from FTP server
        :return: tuple of (success: bool, message: str)
        """
        if self.ftp_connection is None:
            return (True, "No active connection to disconnect")

        try:
            self.ftp_connection.quit()
            self.ftp_connection = None
            msg = "Disconnected successfully"
            self._log(msg)
            return (True, msg)
        except Exception as e:
            self.ftp_connection = None
            msg =  f"Error during disconnect: {str(e)}"
            self._log(msg)
            return (False, f"Error during disconnect: {str(e)}")


    def list_ftp_path(self, ftp_path: str) -> dict:
        """
        Returns a list of files/folders in the ftp server at the specified path
        :param ftp_path: Path on FTP server to list
        :return: Dictionary with 'files' and 'dirs' keys containing lists
        """
        # Ensure connection is alive
        success, msg = self._ensure_connection()
        if not success:
            return {'files': [], 'dirs': [], 'error': f'Connection failed: {msg}'}

        if self.ftp_connection is None:
            return {'files': [], 'dirs': [], 'error': 'Not connected to FTP server'}

        try:
            files = []
            dirs = []

            # Get detailed listing
            items = []
            self.ftp_connection.dir(ftp_path, items.append)

            for item in items:
                # Parse the directory listing (Unix-style format)
                parts = item.split(None, 8)
                if len(parts) >= 9:
                    permissions = parts[0]
                    name = parts[8]

                    # Skip . and .. entries
                    if name in ['.', '..']:
                        continue

                    # Check if it's a directory (starts with 'd')
                    if permissions.startswith('d'):
                        dirs.append(name)
                    else:
                        files.append(name)

            return {'files': files, 'dirs': dirs}
        except ftplib.all_errors as e:
            return {'files': [], 'dirs': [], 'error': str(e)}


    def _get_ftp_file_info(self, ftp_path: str) -> dict:
        """
        Get file modification time and size from FTP server
        :param ftp_path: Full path to file on FTP
        :return: dict with 'mtime' and 'size' keys
        """
        # Ensure connection is alive
        self._ensure_connection()
        try:
            # Get modification time
            mdtm_response = self.ftp_connection.sendcmd(f'MDTM {ftp_path}')
            time_str = mdtm_response.split()[1]
            mtime = datetime.strptime(time_str, '%Y%m%d%H%M%S').timestamp()

            # Get file size
            size = self.ftp_connection.size(ftp_path)

            return {'mtime': mtime, 'size': size}
        except:
            return {'mtime': 0, 'size': 0}


    def _should_download_file(self, ftp_path: str, local_path: str) -> bool:
        """
        Check if file should be downloaded based on time and size comparison
        :param ftp_path: Path on FTP server
        :param local_path: Path on local filesystem
        :return: True if file should be downloaded
        """
        if not os.path.exists(local_path):
            return True

        # Get FTP file info
        ftp_info = self._get_ftp_file_info(ftp_path)

        # Get local file info
        local_stat = os.stat(local_path)
        local_mtime = local_stat.st_mtime
        local_size = local_stat.st_size

        # Download if either size or time differs
        if ftp_info['size'] != local_size or ftp_info['mtime'] > local_mtime:
            return True

        return False


    def _ensure_connection(self) -> (bool, str):
        """
        Check if connection is alive and reconnect if needed
        :return: tuple of (success: bool, message: str)
        """
        if self.ftp_connection is None:
            return self.connect_to_ftp()

        try:
            # Send NOOP to check if connection is alive
            self.ftp_connection.voidcmd("NOOP")
            return (True, "Connection is alive")
        except:
            # Connection is dead, reconnect
            return self.connect_to_ftp()


    def dump_all_from_ftp(self,
                          ftp_path: str,
                          local_path: str,
                          download_only_if_newer: bool = True,
                          verbose: bool = True):
        """
        Dump all files from the ftp server at the specified path, to the local path
        :param ftp_path: the path on the ftp server
        :param local_path: the path on the local system where to dump data
        :param download_only_if_newer: download only files that are newer than those already downloaded
        :param verbose: log what you are doing
        :return: tuple of (success: bool, message: str)
        """
        # Ensure connection is alive
        success, msg = self._ensure_connection()
        if not success:
            return (False, f"Connection failed: {msg}")

        if self.ftp_connection is None:
            return (False, "Not connected to FTP server")

        try:
            # Normalize the local path for the current OS
            local_path = os.path.normpath(local_path)
            # Create local directory if it doesn't exist
            if not os.path.exists(local_path):
                try:
                    os.makedirs(local_path, exist_ok=True)
                except OSError as e:
                    return (False, f"Failed to create local directory {local_path}: {str(e)}")

            # Get listing of current directory
            listing = self.list_ftp_path(ftp_path)

            if 'error' in listing:
                return (False, f"Error listing FTP path: {listing['error']}")

            files_downloaded = 0
            files_skipped = 0

            # Download files
            for filename in listing['files']:
                ftp_file_path = f"{ftp_path}/{filename}".replace('//', '/')
                local_file_path = os.path.join(local_path, filename)

                # Check if we should download
                should_download = True
                if download_only_if_newer:
                    should_download = self._should_download_file(ftp_file_path, local_file_path)

                if should_download:
                    if verbose:
                        msg = (f"Downloading: {ftp_file_path} -> {local_file_path}")
                        self._log(msg)

                    with open(local_file_path, 'wb') as local_file:
                        self.ftp_connection.retrbinary(f'RETR {ftp_file_path}', local_file.write)

                    files_downloaded += 1
                else:
                    if verbose:
                        msg = (f"Skipping (up to date): {filename}")
                        self._log(msg)
                    files_skipped += 1

            # Recursively process subdirectories
            for dirname in listing['dirs']:
                ftp_subdir_path = f"{ftp_path}/{dirname}".replace('//', '/')
                local_subdir_path = os.path.join(local_path, dirname)

                if verbose:
                    msg = (f"Entering directory: {dirname}")
                    self._log(msg)

                # Recursive call
                result = self.dump_all_from_ftp(
                    ftp_subdir_path,
                    local_subdir_path,
                    download_only_if_newer,
                    verbose
                )

                if not result[0]:
                    return result

            message = f"Sync complete. Downloaded: {files_downloaded}, Skipped: {files_skipped}"
            if verbose:
                self._log(message)

            return (True, message)

        except Exception as e:
            msg = f"Error during dump: {str(e)}"
            self._log(msg)
            return (False, msg)
