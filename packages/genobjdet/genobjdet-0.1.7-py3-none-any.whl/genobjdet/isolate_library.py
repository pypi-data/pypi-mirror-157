import base64
import json
import boto3
import requests
import cv2
class dataException(Exception):
    pass

def request(image="", api_key="", prompt="", write_to_file=False):
    """
    This function is used to request the image bounding coordinates from the server.
    :param api_key: The necessary API key to access the server.
    :param image: directory of the image to be processed
    :param prompt: prompt for the server to analyze the image for
    :param write_to_file: Write bounding box coordinates directly to the image
    :return:
    """
    assert type(image) == type("") and image != "", "Please input an image directory"
    assert type(prompt) == type("") and prompt != "", "Please input a prompt"
    assert type(api_key) == type("") and api_key != "", "Please input an API key"
    try:
        image_data = open(image, "rb").read()
    except:
        raise dataException("Please insert a valid image directory")
    encoded = base64.b64encode(image_data)
    # url = "https://general-object-detection-v2.p.rapidapi.com/get_json"
    encoded = str(encoded)
    encoded = encoded[2::]
    encoded = encoded[:-1:]
    payload = {
    "image": encoded,
    "prompt": prompt
    }
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "general-object-detection-v2.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    aws_api_key="OskMT12umo1vyYTSLLc0J72B0ndgYRfdeclxwY70"
    response = requests.post("https://e61cclu2ga.execute-api.us-east-1.amazonaws.com/prod2/get_json", json=payload, headers={"x-api-key":aws_api_key})
    try:
        coordinates = json.loads(response.text)
        coordinates = coordinates["bounding_coords"]
    except Exception as e1:
        raise dataException(str(response.text)+"\nPlease retry your request or use another image")
    print(coordinates[0])
    if write_to_file:
        coordinate_writer(image=image, coordinates=coordinates[0])
        return
    return coordinates


def coordinate_writer(image, coordinates):
    """
    This function is used to write the bounding coordinates to the image.
    :param image: directory of the image to be processed
    :param coordinates: list of coordinates to be written to the image as a bounding box
    :return:
    """
    assert type(image) == type("") and image != '', 'Please input an image directory'
    assert coordinates is not None, 'Please input image coordinates to write'
    directory = image
    image = cv2.imread(image)
    color = (255, 0, 0)  # blue
    thickness = 2
    image = cv2.rectangle(image, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]), color,
                          thickness=thickness)
    cv2.imwrite(directory, image)
    return
