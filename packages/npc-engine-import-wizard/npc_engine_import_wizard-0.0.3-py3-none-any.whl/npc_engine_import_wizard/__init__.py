#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa

"""Import wizard CLI for converting popular deep learning library models into NPC Engine services."""

from .version import __version__, __release__


from loguru import logger

try:
    from npc_engine_import_wizard.import_wizards.hf_chatbot_import_wizard import (
        HfChatbotImportWizard,
    )

    logger.info("HfChatbotImportWizard is available")
except ImportError as e:
    raise e

try:
    from npc_engine_import_wizard.import_wizards.hf_classifier_import_wizard import (
        HfClassifierImportWizard,
    )

    logger.info("HfClassifierImportWizard is available")
except ImportError:
    pass

try:
    from npc_engine_import_wizard.import_wizards.hf_similarity_import_wizard import (
        HfSimilarityImportWizard,
    )

    logger.info("HfSimilarityImportWizard is available")
except ImportError:
    pass

try:
    from npc_engine_import_wizard.import_wizards.flowtron_import_wizard import (
        FlowtronImportWizard,
    )

    logger.info("FlowtronImportWizard is available")
except ImportError:
    pass
