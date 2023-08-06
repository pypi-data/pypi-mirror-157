#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is the entry point for the command-line interface for NPC Engine's import wizards."""
import sys
import os
import logging


logging.basicConfig(level=logging.ERROR)
import shutil
from npc_engine.services.utils.config import (
    get_model_type_name,
    validate_local_model,
)

import click
from huggingface_hub import snapshot_download
from loguru import logger

from npc_engine_import_wizard.version import __version__


@click.group()
@click.option("--verbose/--silent", "-v", default=False, help="Enable verbose output.")
def cli(verbose: bool):
    """NPC Engine import wizard CLI for converting popular deep learning library models into services."""
    logger.remove()
    if verbose:
        logger.add(
            sys.stdout, format="{time} {level} {message}", level="DEBUG", enqueue=True
        )
        click.echo(
            click.style(
                "Verbose logging is enabled. (LEVEL=DEBUG)",
                fg="yellow",
            )
        )
    else:
        logger.add(
            sys.stdout, format="{time} {level} {message}", level="WARNING", enqueue=True
        )


@cli.command("list-wizards")
def list_wizards():
    """Import the model."""
    from npc_engine_import_wizard.import_wizards.base_import_wizard import ImportWizard

    import_wizards = ImportWizard.get_import_wizards()
    click.echo("Available import wizards:")
    for i, import_wizard in enumerate(import_wizards):
        click.echo(f"-- {import_wizard.long_description()}")


@cli.command("import")
@click.option(
    "--models-path",
    default=os.environ.get(
        "NPC_ENGINE_MODELS_PATH",
        "./models",
    ),
    help="The path to the folder with service configs.",
)
@click.argument("model_id")
def import_model(models_path: str, model_id: str, remove_source: bool = False):
    """Import the model."""
    from npc_engine_import_wizard.import_wizards.base_import_wizard import ImportWizard

    logger.info("Downloading source model {}", model_id)
    if os.path.exists(model_id):
        source_path = model_id
    else:
        source_path = snapshot_download(
            repo_id=model_id, revision="main", cache_dir=models_path
        )
        remove_source = True
    export_path = os.path.join(
        models_path,
        "converted-" + model_id.replace("\\", "/").split("/")[-1],
    )
    os.makedirs(export_path, exist_ok=True)

    logger.info("Exporting model {} to {}", model_id, export_path)
    import_wizards = ImportWizard.get_import_wizards()
    click.echo("Available import wizards:")
    for i, import_wizard in enumerate(import_wizards):
        click.echo(f"{i+1}. {import_wizard.description()}")
    exporter_id = click.prompt("Please select an import wizard", type=int)
    import_wizard = import_wizards[exporter_id - 1]
    import_wizard.convert(source_path, export_path)
    import_wizard.create_config(export_path)
    if remove_source:
        shutil.rmtree(source_path)


@cli.command()
@click.option(
    "--models-path",
    default=os.environ.get("NPC_ENGINE_MODELS_PATH", "./models"),
    help="The path to the folder with service configs.",
)
@click.argument("model_id")
def test_model(models_path: str, model_id: str):
    """Send test request to the model and print reply."""
    from npc_engine_import_wizard.import_wizards.base_import_wizard import ImportWizard

    if not validate_local_model(models_path, model_id):
        click.echo(
            click.style(
                f"{(model_id)} is not a valid npc-engine model.",
                fg="red",
            )
        )
        return 1
    model_type = get_model_type_name(models_path, model_id)
    exporters = ImportWizard.get_import_wizards()
    for exporter in exporters:
        if exporter.get_model_name() == model_type:
            exporter.test_model(models_path, model_id)
            return 0


@cli.command()
def version():
    """Get the npc engine version."""
    click.echo(click.style(f"{__version__}", bold=True))


if __name__ == "__main__":
    cli()
