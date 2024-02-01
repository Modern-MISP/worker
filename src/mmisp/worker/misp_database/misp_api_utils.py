from typing import Any

from requests import Response, JSONDecodeError

from mmisp.worker.exceptions.misp_api_exceptions import InvalidAPIResponse


class MispAPIUtils:

    @staticmethod
    def decode_json_response(response: Response) -> dict:
        response_dict: dict
        try:
            response_dict = response.json()
        except JSONDecodeError as json_error:
            raise InvalidAPIResponse(f"Invalid API response: {json_error}")

        return response_dict

    @staticmethod
    def translate_dictionary(dictionary: dict, translation_dict: dict[str, str]) -> dict:
        translated_dict: dict = {}
        for key in dictionary.keys():
            if key in translation_dict:
                new_key: str = translation_dict[key]
                translated_dict[new_key] = dictionary[key]
            else:
                translated_dict[key] = dictionary[key]

        return translated_dict
