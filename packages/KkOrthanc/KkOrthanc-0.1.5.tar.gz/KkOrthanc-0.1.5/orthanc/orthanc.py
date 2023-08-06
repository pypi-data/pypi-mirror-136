import json
from typing import List, Dict, Union, Any, Optional
import requests


class Orthanc:
    """
    Wrapper around Orthanc REST API
    """
    def __init__(self, orthanc_url: str) -> None:
        """
        Constructor

        Parameters
        ----------
        orthanc_url
            Orthanc server address
            Use Mozilla Firefox at URL http://localhost:8042/ to interact with Orthanc

        Returns
        -------
        None
            __init__ function does not have returns
        """
        self._orthanc_url = orthanc_url

    @staticmethod
    def _get_request(url: str, params: Optional[Dict] = None, return_as_bytes: bool = False) -> Any:
        """
        Get from specified url

        Parameters
        ----------
        url
            HTTP URL
        params
            Parameters if needed in the HTTP GET request
        return_as_bytes
            If True, returns the content as bytes

        Returns
        -------
        Any
            Response of the HTTP GET request converted to json format
        """
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                if return_as_bytes:
                    return response.content

                try:
                    return response.json()
                except ValueError:
                    return response.content
            response.raise_for_status()
        except requests.HTTPError as httpError:
            print(httpError)
        except Exception as otherError:
            print(otherError)

    @staticmethod
    def _post_request(url: str, data: Optional[Union[Dict, str, int, bytes]] = None, return_as_bytes: bool = False) -> \
            Union[Dict, str, bytes, int]:
        """
        Post to specified url

        Parameters
        ----------
        url
            HTTP URL
        data
            Dictionary to post in the body of request
        return_as_bytes
            If True, returns the content as bytes

        Returns
        -------
        Union[Dict, str, bytes, int]
            Response of the HTTP POST request converted to json format
        """
        if type(data) != bytes:
            data = json.dumps(data)

        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                if return_as_bytes:
                    return response.content

                try:
                    return response.json()
                except ValueError:
                    return response.content
            response.raise_for_status()
        except requests.HTTPError as httpError:
            print(httpError)
        except Exception as otherError:
            print(otherError)

    @staticmethod
    def _put_request(url: str, data: Optional[Union[Dict, str, int, bytes]] = None) -> None:
        """
        Put to specified url

        Parameters
        ----------
        url
            HTTP URL
        data
            Dictionary to post in the body of request

        Returns
        -------
        None
            Nothing, raise if an error occurs
        """
        try:
            response = requests.put(url, data=data)
            if response.status_code == 200:
                return
            response.raise_for_status()
        except requests.HTTPError as httpError:
            print(httpError)
        except Exception as otherError:
            print(otherError)

    @staticmethod
    def _delete_request(url: str) -> bool:
        """
        DELETE to specified route

        Parameters
        ----------
        url
            HTTP route.

        Returns
        -------
        bool
            True if the HTTP DELETE request succeeded (status_code 200)
        """
        try:
            response = requests.delete(url)
            if response.status_code == 200:
                return True
            response.raise_for_status()
        except requests.HTTPError as httpError:
            print(httpError)
            return False
        except Exception as otherError:
            print(otherError)
            return False

    def get_patients(self) -> List[str]:
        """
        Get all the patients identifiers

        Returns
        -------
        List[str]
            List of patient identifiers
        """
        return self._get_request(self._orthanc_url + '/patients')

    def get_studies(self) -> List[str]:
        """
        Get all the studies identifiers

        Returns
        -------
        List[str]
            List of studies identifiers
        """
        return self._get_request(self._orthanc_url + '/studies')

    def get_series(self) -> List[str]:
        """
        Get all the series identifiers

        Returns
        -------
        List[str]
            List of series identifiers
        """
        return self._get_request(self._orthanc_url + '/series')

    def get_instances(self) -> List[str]:
        """
        Get all the instances identifiers

        Returns
        -------
        List[str]
            List of instances identifiers
        """
        return self._get_request(self._orthanc_url + '/instances')

    def get_patients_info(self, patient_identifier: str) -> Dict:
        """
        Get specified patient information

        Parameters
        ----------
        patient_identifier
            patient identifier

        Returns
        -------
        Dict
            Patient main information in the form of a dictionary
        """
        return self._get_request(self._orthanc_url + '/patients/' + patient_identifier)

    def get_studies_info(self, study_identifier: str) -> Dict:
        """
        Get specified study information

        Parameters
        ----------
        study_identifier
            study identifier

        Returns
        -------
        Dict
            Study main information in the form of a dictionary
        """
        return self._get_request(self._orthanc_url + '/studies/' + study_identifier)

    def get_series_info(self, series_identifier: str) -> Dict:
        """
        Get specified series information

        Parameters
        ----------
        series_identifier
            series identifier

        Returns
        -------
        Dict
            Series main information in the form of a dictionary
        """
        return self._get_request(self._orthanc_url + '/series/' + series_identifier)

    def get_instances_info(self, instance_identifier: str) -> Dict:
        """
        Get specified instance information

        Parameters
        ----------
        instance_identifier
            instance identifier

        Returns
        -------
        Dict
            Instance main information in the form of a dictionary
        """
        return self._get_request(self._orthanc_url + '/instances/' + instance_identifier)

    def post_instances(self, data: Optional[Union[Dict, str, int, bytes]] = None) -> Union[Dict, str, bytes, int]:
        """
        Post instances
        Add the new DICOM file given in the POST body

        Parameters
        ----------
        data
            POST HTTP request's data

        Returns
        -------
        Union[Dict, str, bytes, int]
            Response of the HTTP POST request converted to json format
        """
        return self._post_request(self._orthanc_url + '/instances', data)

    def delete_study(self, study_identifier) -> bool:
        """
        DELETE the specified study identifier

        Parameters
        ----------
        study_identifier
            study identifier

        Returns
        -------
        bool
            True if the HTTP DELETE request succeeded (status_code 200)
        """
        return self._delete_request(self._orthanc_url + '/studies/' + study_identifier)

    def delete_instance(self, instance_identifier) -> bool:
        """
        DELETE the specified instance identifier

        Parameters
        ----------
        instance_identifier
            instance identifier

        Returns
        -------
        bool
            True if the HTTP DELETE request succeeded (status_code 200)
        """
        return self._delete_request(self._orthanc_url + '/instances/' + instance_identifier)
