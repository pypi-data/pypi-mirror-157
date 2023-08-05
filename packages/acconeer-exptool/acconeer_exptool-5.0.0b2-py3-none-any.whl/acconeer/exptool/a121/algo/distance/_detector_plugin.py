from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Optional

import attrs
import numpy as np
import qtawesome as qta

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

import pyqtgraph as pg

import acconeer.exptool as et
from acconeer.exptool import a121
from acconeer.exptool.a121.algo._plugins import (
    DetectorBackendPluginBase,
    DetectorPlotPluginBase,
    DetectorViewPluginBase,
)
from acconeer.exptool.app.new import (
    BUTTON_ICON_COLOR,
    AppModel,
    BusyMessage,
    ConnectionState,
    DataMessage,
    IdleMessage,
    KwargMessage,
    Message,
    OkMessage,
    Plugin,
    PluginFamily,
    PluginGeneration,
    PluginState,
    Task,
)
from acconeer.exptool.app.new.ui.plugin import (
    AttrsConfigEditor,
    GridGroupBox,
    PidgetFactoryMapping,
    pidgets,
)

from ._detector import (
    Detector,
    DetectorConfig,
    DetectorContext,
    DetectorResult,
    PeakSortingMethod,
    ThresholdMethod,
)


log = logging.getLogger(__name__)


@attrs.mutable(kw_only=True)
class SharedState:
    config: DetectorConfig = attrs.field()
    context: DetectorContext = attrs.field(factory=DetectorContext)

    @property
    def has_recorded_threshold(self) -> bool:
        # TODO: Implement in detector
        return self.context.recorded_thresholds is not None

    @property
    def has_close_range_calibration(self) -> bool:
        # TODO: Implement in detector
        return self.context.phase_jitter_comp_reference is not None


class BackendPlugin(DetectorBackendPluginBase[SharedState]):
    def __init__(self, callback: Callable[[Message], None], key: str) -> None:
        super().__init__(callback=callback, key=key)

        self._started: bool = False
        self._client: Optional[a121.Client] = None

        self._detector_instance: Optional[Detector] = None

        self.shared_state = SharedState(config=DetectorConfig())

        self.broadcast(sync=True)

    def broadcast(self, sync: bool = False) -> None:
        super().broadcast()

        if sync:
            self.callback(OkMessage("sync", recipient="view_plugin"))

    def idle(self) -> bool:
        if self._started:
            self.__execute_get_next()
            return True
        else:
            return False

    def attach_client(self, *, client: Any) -> None:
        self._client = client

    def detach_client(self) -> None:
        self._client = None

    def execute_task(self, *, task: Task) -> None:
        task_name, task_kwargs = task
        if task_name == "start_session":
            self.__execute_start()
        elif task_name == "stop_session":
            self.__execute_stop()
        elif task_name == "record_threshold":
            self.__execute_record_threshold()
        elif task_name == "calibrate_close_range":
            self.__execute_calibrate_close_range()
        elif task_name == "update_config":
            config = task_kwargs["config"]
            assert isinstance(config, DetectorConfig)
            self.shared_state.config = config
            self.broadcast()
        else:
            raise RuntimeError

    def teardown(self) -> None:
        self.detach_client()

    def load_from_file(self, *, path: Path) -> None:
        raise NotImplementedError

    def __execute_start(self) -> None:
        if self._started:
            raise RuntimeError

        if self._client is None:
            raise RuntimeError

        if not self._client.connected:
            raise RuntimeError

        self._detector_instance = Detector(
            client=self._client,
            sensor_id=1,
            detector_config=self.shared_state.config,
            context=self.shared_state.context,
        )

        self._detector_instance.start()

        self._started = True

        self.broadcast()

        self.callback(
            KwargMessage(
                "setup",
                dict(num_curves=len(self._detector_instance.processor_specs)),
                recipient="plot_plugin",
            )
        )
        self.callback(BusyMessage())

    def __execute_stop(self) -> None:
        if not self._started:
            raise RuntimeError

        if self._detector_instance is None:
            raise RuntimeError

        self._detector_instance.stop()

        self._started = False

        self.broadcast()

        self.callback(IdleMessage())

    def __execute_get_next(self) -> None:
        if not self._started:
            raise RuntimeError

        if self._detector_instance is None:
            raise RuntimeError

        result = self._detector_instance.get_next()

        self.callback(DataMessage("plot", result, recipient="plot_plugin"))

    def __execute_record_threshold(self) -> None:
        if self._started:
            raise RuntimeError

        if self._client is None:
            raise RuntimeError

        if not self._client.connected:
            raise RuntimeError

        self.callback(BusyMessage())

        self._detector_instance = Detector(
            client=self._client,
            sensor_id=1,
            detector_config=self.shared_state.config,
            context=self.shared_state.context,
        )
        self._detector_instance.record_threshold()
        self.shared_state.context = self._detector_instance.context

        self.callback(IdleMessage())
        self.broadcast()

    def __execute_calibrate_close_range(self) -> None:
        if self._started:
            raise RuntimeError

        if self._client is None:
            raise RuntimeError

        if not self._client.connected:
            raise RuntimeError

        self.callback(BusyMessage())

        self._detector_instance = Detector(
            client=self._client,
            sensor_id=1,
            detector_config=self.shared_state.config,
            context=self.shared_state.context,
        )
        self._detector_instance.calibrate_close_range()
        self.shared_state.context = self._detector_instance.context

        self.callback(IdleMessage())
        self.broadcast()


class PlotPlugin(DetectorPlotPluginBase):
    def __init__(self, *, plot_layout: pg.GraphicsLayout, app_model: AppModel) -> None:
        super().__init__(plot_layout=plot_layout, app_model=app_model)

    def setup_from_message(self, message: Message) -> None:
        assert isinstance(message, KwargMessage)
        self.setup(**message.kwargs)

    def update_from_message(self, message: Message) -> None:
        assert isinstance(message, DataMessage)
        self.update(message.data)

    def setup(self, num_curves: int) -> None:
        self.num_curves = num_curves
        self.distance_history = [np.NaN] * 100

        win = self.plot_layout

        self.sweep_plot = win.addPlot(row=0, col=0)
        self.sweep_plot.setMenuEnabled(False)
        self.sweep_plot.showGrid(x=True, y=True)
        self.sweep_plot.addLegend()
        self.sweep_plot.setLabel("left", "Amplitude")
        self.sweep_plot.setLabel("bottom", "Distance (m)")
        self.sweep_plot.addItem(pg.PlotDataItem())

        pen = et.utils.pg_pen_cycler(0)
        brush = et.utils.pg_brush_cycler(0)
        symbol_kw = dict(symbol="o", symbolSize=1, symbolBrush=brush, symbolPen="k")
        feat_kw = dict(pen=pen, **symbol_kw)
        self.sweep_curves = [self.sweep_plot.plot(**feat_kw) for _ in range(self.num_curves)]

        pen = et.utils.pg_pen_cycler(1)
        brush = et.utils.pg_brush_cycler(1)
        symbol_kw = dict(symbol="o", symbolSize=1, symbolBrush=brush, symbolPen="k")
        feat_kw = dict(pen=pen, **symbol_kw)
        self.threshold_curves = [self.sweep_plot.plot(**feat_kw) for _ in range(self.num_curves)]

        self.dist_history_plot = win.addPlot(row=1, col=0)
        self.dist_history_plot.setMenuEnabled(False)
        self.dist_history_plot.showGrid(x=True, y=True)
        self.dist_history_plot.addLegend()
        self.dist_history_plot.setLabel("left", "Estimated distance (m)")
        self.dist_history_plot.addItem(pg.PlotDataItem())
        self.dist_history_plot.setXRange(0, len(self.distance_history))

        pen = et.utils.pg_pen_cycler(0)
        brush = et.utils.pg_brush_cycler(0)
        symbol_kw = dict(symbol="o", symbolSize=5, symbolBrush=brush, symbolPen="k")
        feat_kw = dict(pen=pen, **symbol_kw)
        self.dist_history_curve = self.dist_history_plot.plot(**feat_kw)

    def update(self, result: DetectorResult) -> None:
        assert result.distances is not None

        self.distance_history.pop(0)
        self.distance_history.append(result.distances[0])

        for idx, processor_result in enumerate(result.processor_results):
            assert processor_result.extra_result.used_threshold is not None
            assert processor_result.extra_result.distances_m is not None

            threshold = processor_result.extra_result.used_threshold
            self.sweep_curves[idx].setData(
                processor_result.extra_result.distances_m, processor_result.extra_result.abs_sweep
            )
            self.threshold_curves[idx].setData(
                processor_result.extra_result.distances_m, threshold
            )

        if np.any(~np.isnan(self.distance_history)):
            self.dist_history_curve.setData(self.distance_history)
        else:
            self.dist_history_curve.setData([])


class ViewPlugin(DetectorViewPluginBase):
    def __init__(self, app_model: AppModel, view_widget: QWidget) -> None:
        super().__init__(app_model=app_model, view_widget=view_widget)

        self.view_layout = QVBoxLayout(self.view_widget)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        self.view_widget.setLayout(self.view_layout)

        # TODO: Fix parents

        self.start_button = QPushButton(
            qta.icon("fa5s.play-circle", color=BUTTON_ICON_COLOR),
            "Start measurement",
            self.view_widget,
        )
        self.start_button.clicked.connect(self._send_start_request)
        self.stop_button = QPushButton(
            qta.icon("fa5s.stop-circle", color=BUTTON_ICON_COLOR),
            "Stop",
            self.view_widget,
        )
        self.stop_button.clicked.connect(self._send_stop_request)

        self.record_threshold_button = QPushButton(
            qta.icon("fa.video-camera", color=BUTTON_ICON_COLOR),
            "Record threshold",
            self.view_widget,
        )
        self.record_threshold_button.clicked.connect(self._on_record_threshold)

        self.close_range_calibration_button = QPushButton(
            qta.icon("mdi.adjust", color=BUTTON_ICON_COLOR),
            "Calibrate close range",
            self.view_widget,
        )
        self.close_range_calibration_button.clicked.connect(self._on_close_range_calibration)

        self.record_threshold_status = QLabel(self.view_widget)
        self.close_range_calibration_status = QLabel(self.view_widget)

        button_group = GridGroupBox("Controls", parent=self.view_widget)
        button_group.layout().addWidget(self.start_button, 0, 0)
        button_group.layout().addWidget(self.stop_button, 0, 1)
        button_group.layout().addWidget(self.close_range_calibration_button, 1, 0)
        button_group.layout().addWidget(self.record_threshold_button, 1, 1)
        button_group.layout().addWidget(self.close_range_calibration_status, 2, 0, 1, -1)
        button_group.layout().addWidget(self.record_threshold_status, 3, 0, 1, -1)
        self.view_layout.addWidget(button_group)

        self.config_editor = AttrsConfigEditor[DetectorConfig](
            title="Detector parameters",
            factory_mapping=self._get_pidget_mapping(),
            parent=self.view_widget,
        )
        self.config_editor.sig_update.connect(self._on_config_update)
        self.view_layout.addWidget(self.config_editor)

        self.view_layout.addStretch(1)

    @classmethod
    def _get_pidget_mapping(cls) -> PidgetFactoryMapping:
        return {
            "start_m": pidgets.FloatParameterWidgetFactory(
                name_label_text="Range start",
                suffix=" m",
                decimals=3,
            ),
            "end_m": pidgets.FloatParameterWidgetFactory(
                name_label_text="Range end",
                suffix=" m",
                decimals=3,
            ),
            "max_step_length": pidgets.OptionalIntParameterWidgetFactory(
                name_label_text="Max step length",
                checkbox_label_text="Set",
                limits=(1, None),
                init_set_value=12,
            ),
            "max_profile": pidgets.EnumParameterWidgetFactory(
                name_label_text="Max profile",
                enum_type=a121.Profile,
                label_mapping={
                    a121.Profile.PROFILE_1: "1 (shortest)",
                    a121.Profile.PROFILE_2: "2",
                    a121.Profile.PROFILE_3: "3",
                    a121.Profile.PROFILE_4: "4",
                    a121.Profile.PROFILE_5: "5 (longest)",
                },
            ),
            "num_frames_in_recorded_threshold": pidgets.IntParameterWidgetFactory(
                name_label_text="Num frames in rec. thr.",
                limits=(1, None),
            ),
            "threshold_method": pidgets.EnumParameterWidgetFactory(
                name_label_text="Threshold method",
                enum_type=ThresholdMethod,
                label_mapping={
                    ThresholdMethod.CFAR: "CFAR",
                    ThresholdMethod.FIXED: "Fixed",
                    ThresholdMethod.RECORDED: "Recorded",
                },
            ),
            "peaksorting_method": pidgets.EnumParameterWidgetFactory(
                name_label_text="Peak sorting method",
                enum_type=PeakSortingMethod,
                label_mapping={
                    PeakSortingMethod.STRONGEST: "Strongest",
                    PeakSortingMethod.CLOSEST: "Closest",
                    PeakSortingMethod.HIGHEST_RCS: "Highest RCS",
                },
            ),
            "fixed_threshold_value": pidgets.FloatParameterWidgetFactory(
                name_label_text="Fixed threshold value",
                decimals=1,
                limits=(0, None),
            ),
            "threshold_sensitivity": pidgets.FloatParameterWidgetFactory(
                name_label_text="Threshold sensitivity",
                decimals=2,
                limits=(0, 1),
            ),
            "cfar_one_sided": pidgets.CheckboxParameterWidgetFactory(
                name_label_text="CFAR one sided",
            ),
        }

    def on_app_model_update(self, app_model: AppModel) -> None:
        self.config_editor.setEnabled(app_model.plugin_state == PluginState.LOADED_IDLE)

        startable = (
            app_model.plugin_state == PluginState.LOADED_IDLE
            and app_model.connection_state == ConnectionState.CONNECTED
        )
        self.start_button.setEnabled(startable)
        self.record_threshold_button.setEnabled(startable)
        self.close_range_calibration_button.setEnabled(startable)

        self.stop_button.setEnabled(app_model.plugin_state == PluginState.LOADED_BUSY)

        if app_model.backend_plugin_state is None:
            self.config_editor.set_data(None)
            self.record_threshold_status.setText("")
            self.close_range_calibration_status.setText("")
        else:
            state = app_model.backend_plugin_state
            assert isinstance(state, SharedState)

            self.config_editor.set_data(state.config)

            text = "Threshold recorded: "
            text += "Yes" if state.has_recorded_threshold else "No"
            self.record_threshold_status.setText(text)

            text = "Close range calibrated: "
            text += "Yes" if state.has_close_range_calibration else "No"
            self.close_range_calibration_status.setText(text)

    # TODO: move to detector base (?)
    def _on_config_update(self, config: DetectorConfig) -> None:
        self.send_backend_task(("update_config", {"config": config}))

    # TODO: move to detector base (?)
    def handle_message(self, message: Message) -> None:
        if message.command_name == "sync":
            log.debug(f"{type(self).__name__} syncing")

            self.config_editor.sync()
        else:
            raise RuntimeError("Unknown message")

    # TODO: move to detector base (?)
    def _send_start_request(self) -> None:
        self.send_backend_task(("start_session", {}))
        self.app_model.set_plugin_state(PluginState.LOADED_STARTING)

    # TODO: move to detector base (?)
    def _send_stop_request(self) -> None:
        self.send_backend_task(("stop_session", {}))
        self.app_model.set_plugin_state(PluginState.LOADED_STOPPING)

    def _on_record_threshold(self) -> None:
        self.send_backend_task(("record_threshold", {}))
        self.app_model.set_plugin_state(PluginState.LOADED_STARTING)

    def _on_close_range_calibration(self) -> None:
        self.send_backend_task(("calibrate_close_range", {}))
        self.app_model.set_plugin_state(PluginState.LOADED_STARTING)

    # TODO: move to detector base (?)
    def teardown(self) -> None:
        self.view_layout.deleteLater()


DISTANCE_DETECTOR_PLUGIN = Plugin(
    generation=PluginGeneration.A121,
    key="distance_detector",
    title="Distance detector",
    description="Easily measure distance to objects.",
    family=PluginFamily.DETECTOR,
    backend_plugin=BackendPlugin,
    plot_plugin=PlotPlugin,
    view_plugin=ViewPlugin,
)
