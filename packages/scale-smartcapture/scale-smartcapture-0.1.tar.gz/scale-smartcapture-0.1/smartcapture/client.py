import base64
import requests
from .trigger import Trigger
import pickle
import json
from .constants import SMARTCAPTURE_ENDPOINT


class SmartCaptureClient:
    def __init__(self, api_key, device_name):
        self.api_key = api_key
        self.encoded_key = base64.b64encode((self.api_key + ":").encode()).decode()
        self.device_name = device_name
        self.device_id = self._get_device_id()
        self.triggers = []

    def _get_device_id(self):
        resp = requests.get(
            f"{SMARTCAPTURE_ENDPOINT}/all_devices",
            headers={"Authorization": "Basic " + self.encoded_key},
        )
        for device in resp.json():
            if device["name"] == self.device_name:
                return device["id"]
        raise Exception("Device not registered on smart capture")

    def load(self, trigger_config_path="demo"):
        """
        Create triggers from json file on device.

        For the demo, we will call the get device endpoint to get a list of trigger ids.
        We will then call the get trigger endpoint to get predicates. We scan the predicate for
        autotag ids and fetch the relevant data.
        """
        if trigger_config_path == "demo_pref":
            resp = requests.get(
                f"{SMARTCAPTURE_ENDPOINT}/device/{self.device_id}/triggers",
                headers={"Authorization": "Basic " + self.encoded_key},
            ).json()
            autotags = resp.get("autotags")
            autotag_metadata = {}
            if autotags:
                for autotag in autotags:
                    model = pickle.loads(bytes(autotag["svm"]["data"]))
                    autotag_metadata[autotag["id"]] = model.coef_[0]
            triggers = resp["triggers"]
            for trigger in triggers:
                metadata = {"sample_rate": trigger["sample_rate"]}
                metadata["autotags"] = autotag_metadata
                self.triggers.append(
                    Trigger(trigger["id"], json.dumps(trigger["predicate"]), metadata)
                )
        if trigger_config_path == "demo":
            data = json.load(open(self.device_id + ".json"))
            last_activations = {
                trigger.trigger_id: trigger.last_activation for trigger in self.triggers
            }
            self.triggers = []
            for trigger in data:
                self.triggers.append(
                    Trigger(
                        trigger,
                        json.dumps(data[trigger]["predicate"]),
                        data[trigger]["metadata"],
                    )
                )
                if trigger in last_activations:
                    self.triggers[-1].last_activation = last_activations[trigger]

    def evaluate(self, state):
        return [
            (trigger.trigger_id, trigger.evaluate(state), trigger.dataset_id)
            for trigger in self.triggers
        ]
