from datetime import UTC, datetime, timedelta
from logging import getLogger
from threading import Thread

from packaging.version import InvalidVersion, parse
from pydantic import RootModel, ValidationError
from requests import RequestException

from src._state import PATH, AppConstants, AppEnvironment
from src.gui.qml.models.plugin_updater_model import PluginUpdaterModel
from src.gui.qml.models.template_updater_model import TemplateUpdaterModel
from src.utils.adobe import PhotoshopHandler
from src.utils.asynchronic import async_to_sync
from src.utils.data_structures import dump_model, parse_model
from src.utils.fonts import check_app_fonts
from src.utils.github import get_github_releases
from src.utils.hexapi import get_api_key, update_hexproof_cache
from src.utils.threading import ThreadInitializedInstance

_logger = getLogger(__name__)


def photoshop_checks(app: PhotoshopHandler) -> None:
    # Check Photoshop connection
    result = app.refresh_app()
    if result:
        # Photoshop test failed
        _logger.exception(
            "Photoshop connection failed. Can't test fonts without Photoshop.",
            exc_info=result,
        )
        return

    # Photoshop test passed
    _logger.info("Connected to Photoshop.")

    # Check for missing or outdated fonts
    missing, outdated = check_app_fonts(app, [PATH.FONTS])

    # Font test passed
    if not missing and not outdated:
        _logger.debug("All essential fonts are installed.")
        return

    # Missing fonts
    if missing:
        _logger.warning(
            f"The following fonts aren't installed:<br>{
                '<br>'.join(
                    [details['name'] for details in missing.values() if details['name']]
                )
            }"
        )
    if outdated:
        _logger.warning(
            f"The following fonts are outdated and have to be reinstalled:<br>{
                '<br>'.join(
                    [
                        details['name']
                        for details in outdated.values()
                        if details['name']
                    ]
                )
            }"
        )


def check_app_update(env: AppEnvironment) -> None:
    """Check if app has updates available."""
    if env.APP_UPDATES_REPO:
        try:
            releases = get_github_releases(env.APP_UPDATES_REPO, per_page=1)
            if len(releases) > 0:
                latest = releases[0].tag_name
                try:
                    update_available = parse(env.VERSION.lstrip("v")) < parse(
                        latest.lstrip("v")
                    )
                except InvalidVersion:
                    update_available = env.VERSION < latest
                if update_available:
                    _logger.info(
                        f'A newer version of Proxyshop is available: {
                            latest
                        }. <a href="https://github.com/{
                            env.APP_UPDATES_REPO
                        }/releases">Download</a>'
                    )
        except RequestException, ValidationError:
            _logger.exception("Failed to check app updates")


def check_plugin_updates(plugin_updater: PluginUpdaterModel):
    try:
        if plugin_updater.handle_fetch_data():
            _logger.info(
                "Plugin updates are available. Open the Plugins window to download them."
            )
    except Exception:
        _logger.exception("Failed to check plugin updates")


def check_template_updates(template_updater: TemplateUpdaterModel):
    try:
        if async_to_sync(template_updater.handle_fetch_data()):
            _logger.info(
                "Template updates are available. Open the Updater window to download them."
            )
    except Exception:
        _logger.exception("Failed to check template updates")


def update_set_data(con: AppConstants) -> None:
    # Update set data if needed
    updated, error = update_hexproof_cache()
    if updated:
        con.reload()
        _logger.info("Hexproof API data update was applied.")
    if error:
        _logger.error(f"Failed to update Hexproof API data: {error}")


def check_api_keys(env: AppEnvironment) -> None:
    # Check if API keys are valid
    if not env.API_GOOGLE:
        env.API_GOOGLE = get_api_key("proxyshop.google.drive")
    if not env.API_AMAZON:
        env.API_AMAZON = get_api_key("proxyshop.amazon.s3")
    keys = {
        "Google Drive": env.API_GOOGLE,
        "Amazon S3": env.API_AMAZON,
    }
    if keys_missing := [k for k, v in keys.items() if not v]:
        _logger.warning(f"Failed to retrieve API keys for: {', '.join(keys_missing)}")
    else:
        _logger.debug(f"Retrieved keys for: {', '.join(keys)}")


def run_startup_checks(
    env: AppEnvironment,
    con: AppConstants,
    photoshop_initializer: ThreadInitializedInstance[PhotoshopHandler],
    plugin_updater: PluginUpdaterModel,
    template_updater: TemplateUpdaterModel,
) -> None:
    photoshop_initializer.initialize()
    if photoshop_initializer.ready:
        photoshop_checks(photoshop_initializer.instance)
    else:
        photoshop_initializer.add_listener(photoshop_checks)

    checks = [
        lambda: update_set_data(con),
        lambda: check_api_keys(env),
    ]

    timestamp_model = RootModel[datetime]
    previous_check_datetime: datetime | None = None
    if PATH.SRC_DATA_PREVIOUS_UPDATE_CHECK.is_file():
        try:
            previous_check_datetime = parse_model(
                PATH.SRC_DATA_PREVIOUS_UPDATE_CHECK, timestamp_model
            ).root
        except Exception as exc:
            _logger.warning(
                f"Failed to parse timestamp for previous update check. Deleting '{PATH.SRC_DATA_PREVIOUS_UPDATE_CHECK}' in order to avoid this problem next time.",
                exc_info=exc,
            )
            PATH.SRC_DATA_PREVIOUS_UPDATE_CHECK.unlink(missing_ok=True)

    # Limit update check interval
    if not previous_check_datetime or previous_check_datetime < datetime.now(
        UTC
    ) - timedelta(hours=env.UPDATE_CHECK_INTERVAL):
        dump_model(
            PATH.SRC_DATA_PREVIOUS_UPDATE_CHECK, timestamp_model(datetime.now(UTC))
        )
        checks.extend(
            (
                lambda: check_app_update(env),
                lambda: check_plugin_updates(plugin_updater),
                lambda: check_template_updates(template_updater),
            )
        )

    for check in checks:
        Thread(target=check).start()
