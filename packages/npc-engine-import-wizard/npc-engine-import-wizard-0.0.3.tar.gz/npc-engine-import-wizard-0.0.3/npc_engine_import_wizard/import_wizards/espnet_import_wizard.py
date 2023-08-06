"""ESPNet2 import wizard."""
import os
import click
import yaml
from espnet2.bin.tts_inference import Text2Speech
from espnet_onnx.export import TTSModelExport

from npc_engine_import_wizard.import_wizards.base_import_wizard import ImportWizard


class ESPNetImportWizard(ImportWizard):
    """ImportWizard for the ESPNET2 text to speech models.

    Find models at https://huggingface.co/models?library=espnet
    """

    def convert(self, model_path: str, export_path: str):
        """Convert the model to the desired format.

        Args:
            model_path: Path to the model.
            export_path: Path to the exported model.
        """
        path, model_dir = os.path.split(export_path)
        m = TTSModelExport(path)
        quantize = click.prompt("Quantize model", default=False, type=bool)
        text2speech = Text2Speech.from_pretrained(model_path, quantize=quantize)
        m.export(text2speech, model_dir, quantize=False)

    def create_config(self, export_path: str):
        """Create the config for the model.

        Args:
            export_path: Path to the exported model.
        """
        config_dict = {
            "type": self.get_model_name(),
            "speaker_num": click.prompt("Number of speakers", type=int),
        }
        with open(os.path.join(export_path, "config.yml"), "w") as f:
            yaml.dump(config_dict, f)

    @classmethod
    def get_api(cls) -> str:
        """Get the api for the exporter."""
        return "TextToSpeechAPI"

    @classmethod
    def get_model_name(cls) -> str:
        """Get the model name."""
        return "ESPNetTTS"
