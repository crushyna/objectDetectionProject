import logging

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials


class CognitiveModel:
    def __init__(self, image_file: str):
        self.subscription_key = "a3747513ff724c229b41274483acb06f"
        self.endpoint = "https://cvision-crushyna.cognitiveservices.azure.com/"
        self.computervision_client = ComputerVisionClient(self.endpoint,
                                                          CognitiveServicesCredentials(self.subscription_key))
        self.image_file = image_file
        self.description = None

    def get_image_desc(self) -> str:
        """
        Describe an Image - remote
        This example describes the contents of an image with the confidence score.
        """
        # print("===== Describe an image - remote =====")
        # Call API
        logging.info("Opening image file as binary file")
        local_image = open(self.image_file, 'rb')

        logging.info("Streaming data to Azure Server")
        description_results = self.computervision_client.describe_image_in_stream(local_image)

        # Get the captions (descriptions) from the response, with confidence level
        if len(description_results.captions) == 0:
            no_desc = "No description detected."
            logging.warning(no_desc)
            self.description = no_desc
            return no_desc
        else:
            for caption in description_results.captions:
                logging.info(f"Description found: {caption.text}")
                desc_found = "'{}' with confidence {:.2f}%".format(caption.text, caption.confidence * 100)
                self.description = desc_found
                return desc_found
