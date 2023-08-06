import requests, json, pickle
from importlib.machinery import SourceFileLoader
from termcolor import colored
import os
import rich
from .utils import *

# hide warnings from tensorflow
import warnings

warnings.filterwarnings("ignore")


class Model:
    """
    Make sure model file and weights are in current directory
    Parameters: modelname

    modelname: model file name eg: vggnet, if file name is vggnet.py

    """

    def __init__(self, modelname, token, weights=False, url=""):
        self.__modelname = ""
        self.__model_path = ""
        self.__weights_path = ""
        self.__get_paths(modelname)
        self.__token = token
        self.weights = weights
        self.__url = url + "upload/"
        # self.__url = 'http://127.0.0.1:8000/upload/'
        self.__recievedModelname = self.upload()

    def __get_paths(self, path):
        """
        take path provided by user as modelname
        updates model path, weights path and model name
        """
        # check if user provided a filename
        if "/" not in path:
            path = "./" + path
        # check if user provided path with .py extension
        root, ext = os.path.splitext(path)
        if ext:
            # assign the provided path to model's path
            self.__model_path = path
            # get weights path --> remove .py from the given path and add _weights.pkl after it
            self.__weights_path = path.rsplit(".", 1)[0] + "_weights.pkl"
            # get model name --> get model name from given path
            self.__modelname = path.rsplit(".", 1)[0].split("/")[-1]
        else:
            # get models path --> add .py at the end of given path
            self.__model_path = path + ".py"
            # get weights path --> add _weights.pkl after given path
            self.__weights_path = path + "_weights.pkl"
            # get model name --> get filename from given path
            self.__modelname = path.split("/")[-1]

    def getNewModelId(self):
        if self.__recievedModelname is not None:
            return self.__recievedModelname, self.__modelname

    def checkModel(self):
        # load model from current directory
        try:
            model_file = open(f"{self.__model_path}", "rb")
            model_file.close()

            # check if file contains MyModel
            stat, model = check_MyModel(self.__modelname, self.__model_path)
            # print(stat, f": check_mymodel, check_layers shape of model:{stat}")
            if not stat:
                text = colored(model, "red")
                print(text, "\n")
                # text_upload = colored(f"'{self.__modelname}' upload Failed.", "red")
                # print(text_upload, "\n")
                return False

            # check model API used supported
            stat = is_model_supported(model)
            # print(stat, ": is_model_supported API")
            if not stat:
                text = colored(
                    "Model file not provided as per docs: unsupported API used for Model",
                    "red",
                )
                print(text, "\n")
                # text_upload = colored(f"'{self.__modelname}' upload Failed.", "red")
                # print(text_upload, "\n")
                return False

            # check model layers supported
            stat = layer_instance_check(model)
            # print(stat, ": layers used in model supported check")
            if not stat:
                text = colored("Layers in Model are not supported by Tensorflow", "red")
                print(text, "\n")
                # text_upload = colored(f"'{self.__modelname}' upload Failed.", "red")
                # print(text_upload, "\n")
                return False

            # mock dataset for small training
            # classes = 10  # get output classes from model
            # ds_train = mock_dataset(classes)
            # print(ds_train, ": mocked dataset check")
            # # train on mock data to test model
            # stat_training = small_training_loop(model, ds_train)
            # print(stat_training, ": Training on mocked dataset check")
            # if not stat_training:
            #     text = colored(
            #         "Model doses-nt support training on image classification dataset.",
            #         "red",
            #     )
            #     print(text, "\n")
            #     # text_upload = colored(f"'{self.__modelname}' upload Failed.", "red")
            #     # print(text_upload, "\n")
            #     return False

            # check for model channels to be 3
            model = SourceFileLoader(
                self.__modelname, f"{self.__model_path}"
            ).load_module()
            model_channel = model.MyModel()
            if model_channel.input_shape[3] != 3:
                text = colored(
                    "Please provide model input shape with 3 channels", "red"
                )
                print(text, "\n")
                return False

            if self.weights:
                w = self.checkWeights()
                return w
            return True
        except FileNotFoundError:
            text = colored(
                f"Upload failed. There is no model with the name '{self.__modelname}' in your folder '{os.getcwd()}'.",
                "red",
            )
            print(text, "\n")
            rich.print(
                "For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs[/link]"
            )
            return False

    def checkWeights(self):
        # load model weights from current directory
        try:
            weights_file = open(self.__weights_path, "rb")
        except FileNotFoundError:
            text = colored(
                f"Weights Upload failed. No weights file found with the name '{self.__modelname}_weights.pkl' in path '{os.getcwd()}'.",
                "red",
            )
            print(text, "\n")
            rich.print(
                "For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs[/link]"
            )
            return False
        # Load weights to check if it works
        try:
            we = pickle.load(weights_file)
            model = SourceFileLoader(
                self.__modelname, f"{self.__modelname}.py"
            ).load_module()
            model = model.MyModel()
            model.set_weights(we)
            weights_file.close()
            return True
        except ValueError:
            weights_file.close()
            text = colored(
                "Weights upload failed. Provide weights compatible with provided model.",
                "red",
            )
            print(text, "\n")
            print(
                "For more information check the docs 'https://docs.tracebloc.io/weights'"
            )
            return False

    def upload(self):
        m = self.checkModel()
        if m:
            if self.weights:
                model_file = open(self.__model_path, "rb")
                weights_file = open(self.__weights_path, "rb")
                files = {"upload_file": model_file, "upload_weights": weights_file}
                values = {"model_name": self.__modelname, "setWeights": True}
            else:
                model_file = open(self.__model_path, "rb")
                files = {"upload_file": model_file}
                values = {"model_name": self.__modelname, "setWeights": False}
            # upload on the server
            header = {"Authorization": f"Token {self.__token}"}
            r = requests.post(self.__url, headers=header, files=files, data=values)
            if r.status_code == 202:
                body_unicode = r.content.decode("utf-8")
                content = json.loads(body_unicode)
                return content["model_name"]
            else:
                return None
        else:
            return None
