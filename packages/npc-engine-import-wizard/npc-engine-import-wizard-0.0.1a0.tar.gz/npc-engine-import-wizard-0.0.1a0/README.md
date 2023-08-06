# NPC Engine Import Wizard CLI

Python CLI tool for converting models into npc-engine server format.

## Installation

You can install it via pip. Import wizards might have their own extra requirements.

e.g.
```
pip install npc-engine-import-wizard[transformers]
```

## Usage

You can use the CLI tool to convert models from popular libraries into npc-engine services.

To start the wizard, run the following command:

```
npc-engine-import-wizard import --models-path <path-to-models> <model-path-or-id>
```

It will prompt you to select the import wizard for the model. 
Each service has its own set of import wizards for each library.   
It will also omit import wizards that lack their extras installed 
(i.e. with `npc-engine-import-wizard[transformers]` you will only see 
import wizards for [transformers](https://huggingface.co/docs/transformers/main/en/index) library).

```
1. HfChatbotImportWizard
        ImportWizard for converting HF transformer models into text gen services.
2. HfClassifierImportWizard
        ImportWizard for converting HF classification transformer models.
3. HfSimilarityImportWizard
        ImportWizard for converting HF semantic similarity transformer models.
```

You can also list all available import wizards which will also give you detailed readme for each one.

```
npc-engine-import-wizard list-wizards
```

## Supported libraries

- [🤗 Transformers](https://huggingface.co/docs/transformers/main/en/index)  
There are three import wizards for transformers available for different tasks:
```
1. HfChatbotImportWizard
        ImportWizard for converting HF transformer models into text gen services.
2. HfClassifierImportWizard
        ImportWizard for converting HF classification transformer models.
3. HfSimilarityImportWizard
        ImportWizard for converting HF semantic similarity transformer models.
```
- NVIDIA's [Flowtron](https://github.com/NVIDIA/flowtron) + [Waveglow](https://github.com/NVIDIA/waveglow) import wizard for TTS.
- [ESPNet2](https://github.com/espnet/espnet) import wizard thanks to the [espnet_onnx](https://github.com/Masao-Someki/espnet_onnx) project.