from requests import JSONDecodeError, Response

from mmisp.worker.exceptions.misp_api_exceptions import InvalidAPIResponse


def decode_json_response(response: Response) -> dict:
    """
    Decodes the JSON response from the MISP API

    :param response: response from the MISP API
    :type response: Response
    :return: returns the decoded JSON response
    :rtype: dict
    """
    response_dict: dict
    try:
        response_dict = response.json()
    except JSONDecodeError as json_error:
        print(response.text)
        raise InvalidAPIResponse(f"Invalid API response: {json_error}")

    return response_dict


def translate_dictionary(dictionary: dict, translation_dict: dict[str, str]) -> dict:
    """
    translates the keys of a dictionary according to the translation dictionary

    :param dictionary: dictionary to be translated
    :type dictionary: dict
    :param translation_dict: translation dictionary including the old key as the key and the new key as the value
    :type translation_dict: dict[str, str]
    :return: returns the translated dictionary
    :rtype: dict
    """
    translated_dict: dict = {}
    for key in dictionary.keys():
        if key in translation_dict:
            new_key: str = translation_dict[key]
            translated_dict[new_key] = dictionary[key]
        else:
            translated_dict[key] = dictionary[key]

    return translated_dict
