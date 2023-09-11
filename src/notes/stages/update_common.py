"""Update files common to all vaults."""


from shutil import copy, copytree

from notes.models.params import PARAMS

SETTINGS = dict(
    zip(
        PARAMS.paths.settings_sources,
        PARAMS.paths.settings_destinations,
        strict=True,
    )
)
PLUGIN_SETTINGS = dict(
    zip(
        PARAMS.paths.plugin_settings_sources,
        PARAMS.paths.plugin_settings_destinations,
        strict=True,
    )
)


def main():
    for destination in [PARAMS.paths.grad, PARAMS.paths.personal]:
        copytree(PARAMS.paths.common, destination, dirs_exist_ok=True)
    for destination in [PARAMS.paths.grad_obsidian, PARAMS.paths.personal_obsidian]:
        copytree(PARAMS.paths.obsidian_common, destination, dirs_exist_ok=True)
    for settings_source, settings_destination in SETTINGS.items():
        copy(settings_source, settings_destination)
    for plugin_settings_source, plugin_settings_destination in PLUGIN_SETTINGS.items():
        copy(plugin_settings_source, plugin_settings_destination)


if __name__ == "__main__":
    main()
