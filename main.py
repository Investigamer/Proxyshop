"""
* Proxyshop Application Launcher
"""

from pathlib import Path

from PySide6.QtGui import QIcon

from src import APP, CFG, CON, ENV
from src._loader import PluginLibrary, get_template_file_versions
from src.startup import run_startup_checks


def launch_gui(
    plugin_library: PluginLibrary,
):
    """Launch the app in GUI mode."""

    from PySide6 import QtAsyncio
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuickControls2 import QQuickStyle

    from src.gui.qml.models.batch_rendering_model import BatchRenderingModel
    from src.gui.qml.models.console_model import ConsoleModel
    from src.gui.qml.models.file_dialog_model import FileDialogModel
    from src.gui.qml.models.file_path_model import FilePathModel
    from src.gui.qml.models.image_transform_model import ImageTransformModel
    from src.gui.qml.models.message_dialog_content_model import (
        MessageDialogContentModel,
    )
    from src.gui.qml.models.plugin_updater_model import PluginUpdaterModel
    from src.gui.qml.models.render_operations_model import RenderOperationsModel
    from src.gui.qml.models.settings_model import SettingsModel
    from src.gui.qml.models.settings_tree_model import SettingsTreeModel
    from src.gui.qml.models.template_list_model import TemplateListModel
    from src.gui.qml.models.template_updater_model import TemplateUpdaterModel
    from src.gui.qml.models.test_renders_model import TestRendersModel
    from src.render.render_queue import RenderQueue

    app = QGuiApplication(applicationDisplayName="Proxyshop")
    app.setWindowIcon(QIcon("src/img/favicon.ico"))
    engine = QQmlApplicationEngine()

    file_path_model = FilePathModel()
    render_queue = RenderQueue()
    file_dialog_model = FileDialogModel()
    console_model = ConsoleModel()
    render_message_dialog_content_model = MessageDialogContentModel()
    render_operations_model = RenderOperationsModel(
        render_queue, render_message_dialog_content_model
    )
    plugin_updater_model = PluginUpdaterModel(
        app_env=ENV, con=CON, plugin_library=plugin_library
    )
    template_updater_model = TemplateUpdaterModel(
        app_env=ENV, plugin_library=plugin_library
    )
    test_renders_model = TestRendersModel(
        render_queue,
        plugin_library,
        file_dialog_model,
        render_message_dialog_content_model,
        CFG,
    )
    template_list_model = TemplateListModel(
        render_queue,
        file_dialog_model,
        render_message_dialog_content_model,
        plugin_library,
        test_renders_model,
        CFG,
    )
    batch_render_model = BatchRenderingModel(
        file_dialog_model,
        render_message_dialog_content_model,
        render_queue,
        plugin_library,
        test_renders_model,
        CFG,
    )
    settings_tree_model = SettingsTreeModel(
        app_config=CFG, plugin_library=plugin_library
    )
    settings_model = SettingsModel(settings_tree_model)
    image_transform_model = ImageTransformModel(file_dialog_model=file_dialog_model)

    root_context = engine.rootContext()
    root_context.setContextProperty("filePathModel", file_path_model)
    root_context.setContextProperty("fileDialogModel", file_dialog_model)
    root_context.setContextProperty("consoleModel", console_model)
    root_context.setContextProperty(
        "renderMessageDialogContentModel", render_message_dialog_content_model
    )
    root_context.setContextProperty("renderOperationsModel", render_operations_model)
    root_context.setContextProperty("testRendersModel", test_renders_model)
    root_context.setContextProperty("templateUpdaterModel", template_updater_model)
    root_context.setContextProperty("pluginUpdaterModel", plugin_updater_model)
    root_context.setContextProperty("templateListModel", template_list_model)
    root_context.setContextProperty("batchRenderModel", batch_render_model)
    root_context.setContextProperty("settingsTreeModel", settings_tree_model)
    root_context.setContextProperty("settingsModel", settings_model)
    root_context.setContextProperty("imageTransformModel", image_transform_model)
    root_context.setContextProperty(
        "github_url", f"https://github.com/{ENV.APP_UPDATES_REPO}"
    )

    # This points to the extracted bundle directory in a distributable build
    engine.addImportPath(Path(__file__).parent / "src" / "gui")
    QQuickStyle.setStyle("Fusion")
    QQuickStyle.setFallbackStyle("Basic")
    engine.loadFromModule("qml", "App")

    # Ensure that the root context is available at QML destruction
    app.aboutToQuit.connect(engine.deleteLater)

    run_startup_checks(ENV, CON, APP, plugin_updater_model, template_updater_model)

    QtAsyncio.run(handle_sigint=True)


if __name__ == "__main__":
    initial_versions = get_template_file_versions()
    versions = initial_versions.model_copy(deep=True)
    plugin_library = PluginLibrary(
        con=CON, env=ENV, initial_template_file_versions=versions
    )

    launch_gui(plugin_library)
