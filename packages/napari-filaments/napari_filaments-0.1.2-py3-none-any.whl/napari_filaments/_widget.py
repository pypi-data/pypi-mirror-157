import re
from pathlib import Path
from typing import TYPE_CHECKING, List, Set, Tuple, Union

import numpy as np
from magicclass import (
    MagicTemplate,
    bind_key,
    do_not_record,
    field,
    magicclass,
    magicmenu,
    magictoolbar,
    nogui,
    set_design,
    set_options,
    vfield,
)
from magicclass.types import Bound, Optional
from magicclass.widgets import Figure, Table
from napari.layers import Image, Shapes

from . import _optimizer as _opt
from ._spline import Spline
from ._types import weight

if TYPE_CHECKING:
    from magicclass.fields import MagicValueField
    from magicgui.widgets import ComboBox

ICON_DIR = Path(__file__).parent / "_icon"
ICON_KWARGS = dict(text="", min_width=42, min_height=42)
TARGET_IMG_LAYERS = "target-image-layer"
ROI_ID = "ROI-ID"


@magicclass
class FilamentAnalyzer(MagicTemplate):
    target_filament: "MagicValueField[ComboBox, Shapes]" = vfield(Shapes)
    target_image: "MagicValueField[ComboBox, Image]" = vfield(Image)

    # fmt: off
    @magictoolbar
    class Tools(MagicTemplate):
        @magicmenu
        class Layers(MagicTemplate):
            def open_image(self): ...
            def add_filament_layer(self): ...
            def create_total_intensity(self): ...

        @magicmenu
        class Parameters(MagicTemplate):
            lattice_width = vfield(17, options={"min": 5, "max": 49}, record=False)  # noqa
            dx = vfield(5.0, options={"min": 1, "max": 50.0}, record=False)
            sigma_range = vfield((0.5, 3.0), record=False)

        @magicmenu
        class Others(MagicTemplate):
            def create_macro(self): ...

    @magicclass(widget_type="tabbed")
    class Tabs(MagicTemplate):
        @magicclass(layout="horizontal")
        class Spline(MagicTemplate):
            def __post_init__(self):
                self.margins = (2, 2, 2, 2)

            @magicclass(widget_type="groupbox")
            class Left(MagicTemplate):
                def extend_left(self): ...
                def extend_and_fit_left(self): ...
                def clip_left(self): ...
                def clip_left_at_inflection(self): ...

            @magicclass(widget_type="frame")
            class Both(MagicTemplate):
                def fit_current(self): ...
                def delete_current(self): ...
                def undo_spline(self): ...
                def clip_at_inflections(self): ...

            @magicclass(widget_type="groupbox")
            class Right(MagicTemplate):
                def extend_right(self): ...
                def extend_and_fit_right(self): ...
                def clip_right(self): ...
                def clip_right_at_inflection(self): ...

        @magicclass(widget_type="scrollable")
        class Measure(MagicTemplate):
            def measure_length(self): ...
            def measure_length_all(self): ...
            def plot_profile(self): ...
            def plot_curvature(self): ...

    # fmt: on

    @magicclass
    class Output(MagicTemplate):
        plt = field(Figure)

        def __post_init__(self):
            self._xdata = []
            self._ydata = []
            self.min_height = 200

        @do_not_record
        def view_data(self):
            xlabel = self.plt.ax.get_xlabel() or "x"
            ylabel = self.plt.ax.get_ylabel() or "y"
            if isinstance(self._ydata, list):
                data = {xlabel: self._xdata}
                for i, y in enumerate(self._ydata):
                    data[f"{ylabel}-{i}"] = y
            else:
                data = {xlabel: self._xdata, ylabel: self._ydata}
            view_in_table(data, self)

        def _plot(self, x, y, clear=True, **kwargs):
            if clear:
                self.plt.cla()
            self.plt.plot(x, y, **kwargs)
            self._xdata = x
            if clear:
                self._ydata = y
            else:
                if isinstance(self._ydata, list):
                    self._ydata.append(y)
                else:
                    self._ydata = [self._ydata, y]

        def _set_labels(self, x: str, y: str):
            self.plt.xlabel(x)
            self.plt.ylabel(y)

    def __init__(self):
        self.layer_paths: Shapes = None
        self._last_target_filament: Shapes = None
        self._color_default = np.array([0.973, 1.000, 0.412, 1.000])
        self._last_data: np.ndarray = None

    def _get_idx(self, w=None) -> Union[int, Set[int]]:
        if self.layer_paths is None:
            return 0
        sel = self.layer_paths.selected_data
        if len(sel) == 0:
            return self.layer_paths.nshapes - 1
        return sel

    @target_filament.connect
    def _on_change(self):
        if self._last_target_filament in self.parent_viewer.layers:
            _toggle_target_images(self._last_target_filament, False)

        elif self._last_target_filament is not None:
            self._last_target_filament = None

        self.layer_paths = self.target_filament
        self._last_target_filament = self.target_filament
        self._last_data = None
        _toggle_target_images(self._last_target_filament, True)
        self.parent_viewer.layers.selection = {self.target_filament}

    @Tools.Layers.wraps
    def open_image(self, path: Path):
        """Open a TIF."""
        path = Path(path)
        from tifffile import TiffFile

        with TiffFile(path) as tif:
            series0 = tif.series[0]
            axes = getattr(series0, "axes", "")
            img: np.ndarray = tif.asarray()

        if "C" in axes:
            ic = axes.find("C")
            nchn = img.shape[ic]
            img_layers: List[Image] = self.parent_viewer.add_image(
                img,
                channel_axis=ic,
                name=[f"[C{i}] {path.stem}" for i in range(nchn)],
            )
        else:
            _layer = self.parent_viewer.add_image(img, name=path.stem)
            img_layers = [_layer]

        axis_labels = [c for c in axes if c != "C"]
        self.add_filament_layer(self.parent_viewer.layers[-1], path.stem)
        self.layer_paths.metadata[TARGET_IMG_LAYERS] = img_layers
        ndim = self.parent_viewer.dims.ndim
        if ndim == len(axis_labels):
            self.parent_viewer.dims.set_axis_label(
                list(range(ndim)), axis_labels
            )
        self.target_filament = self.layer_paths

    @Tools.Layers.wraps
    @set_options(name={"text": "Use default name."})
    def add_filament_layer(
        self, target_image: Image, name: Optional[str] = None
    ):
        """Add a Shapes layer for the target image."""
        if name is None:
            name = target_image.name
            if mactched := re.findall(r"\[.*\](.+)", name):
                name = mactched[0]
        layer_paths = self.parent_viewer.add_shapes(
            ndim=target_image.ndim,
            edge_color=self._color_default,
            name=f"[F] {name}",
            edge_width=0.5,
            properties={ROI_ID: 0},
            text=dict(string="[{" + ROI_ID + "}]", color="white", size=8),
        )
        layer_paths.mode = "add_path"

        @layer_paths.events.set_data.connect
        def _on_data_changed(e):
            # delete undo history
            self._last_data = None

            # update current filament ROI ID
            props = layer_paths.current_properties
            all_ids = layer_paths.features[ROI_ID]
            if all_ids.size > 0:
                next_id = np.max(all_ids) + 1
            else:
                next_id = 0
            props[ROI_ID] = next_id
            layer_paths.current_properties = props

        layer_paths.current_properties = {ROI_ID: 0}
        self.layer_paths = layer_paths
        return layer_paths

    def _update_paths(
        self, idx: int, spl: Spline, current_slice: Tuple[int, ...] = ()
    ):
        if idx < 0:
            idx += self.layer_paths.nshapes
        sampled = spl.sample(interval=1.0)
        if current_slice:
            sl = np.stack([np.array(current_slice)] * sampled.shape[0], axis=0)
            sampled = np.concatenate([sl, sampled], axis=1)

        hist = self.layer_paths.data[idx]
        self._replace_data(idx, sampled)
        self._last_data = hist

    def _fit_i_2d(self, width, img, coords) -> Spline:
        spl = Spline.fit(coords, degree=1, err=0.0)
        length = spl.length()
        interv = min(8.0, length / 4)
        rough = spl.fit_filament(
            img, width=width, interval=interv, spline_error=0.0
        )
        return rough.fit_filament(img, width=7, spline_error=3e-2)

    @Tabs.Spline.Both.wraps
    @bind_key("T")
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "fit.png")
    def fit_current(
        self,
        image: Bound[target_image],
        idx: Bound[_get_idx] = -1,
        width: Bound[Tools.Parameters.lattice_width] = 9,
    ):
        """Fit current spline to the image."""
        if not isinstance(image, Image):
            raise TypeError("'image' must be a Image layer.")
        self.layer_paths._finish_drawing()
        indices = _arrange_selection(idx)
        for i in indices:
            data: np.ndarray = self.layer_paths.data[i]
            current_slice, data = _split_slice_and_path(data)
            fit = self._fit_i_2d(width, image.data[current_slice], data)
            self._update_paths(i, fit, current_slice)

    def _get_slice_and_spline(
        self, idx: int
    ) -> Tuple[Tuple[int, ...], Spline]:
        data: np.ndarray = self.layer_paths.data[idx]
        current_slice, data = _split_slice_and_path(data)
        if data.shape[0] < 4:
            data = Spline.fit(data, degree=1, err=0).sample(interval=1.0)
        spl = Spline.fit(data, err=0.0)
        return current_slice, spl

    @Tabs.Spline.Both.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "undo.png")
    def undo_spline(self):
        """Undo the last spline fit."""
        if self._last_data is None:
            return
        idx = self.layer_paths.nshapes - 1
        self._replace_data(idx, self._last_data)

    def _replace_data(self, idx: int, new_data: np.ndarray):
        """Replace the idx-th data to the new one."""
        id = self.layer_paths.features[ROI_ID][idx]
        props = self.layer_paths.current_properties
        props.update({ROI_ID: id})
        self.layer_paths.current_properties = props
        self.layer_paths.add(new_data, shape_type="path")
        self.layer_paths.selected_data = {idx}
        self.layer_paths.remove_selected()
        self._last_data = None

    @Tabs.Spline.Left.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "ext_l.png")
    def extend_left(
        self, idx: Bound[_get_idx] = -1, dx: Bound[Tools.Parameters.dx] = 5.0
    ):
        """Extend spline at the starting edge."""
        idx = _assert_single_selection(idx)
        current_slice, spl = self._get_slice_and_spline(idx)
        out = spl.extend_left(dx)
        self._update_paths(idx, out, current_slice)

    @Tabs.Spline.Right.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "ext_r.png")
    def extend_right(
        self, idx: Bound[_get_idx] = -1, dx: Bound[Tools.Parameters.dx] = 5.0
    ):
        """Extend spline at the ending edge."""
        idx = _assert_single_selection(idx)
        current_slice, spl = self._get_slice_and_spline(idx)
        out = spl.extend_right(dx)
        self._update_paths(idx, out, current_slice)

    @Tabs.Spline.Left.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "extfit_l.png")
    def extend_and_fit_left(
        self,
        image: Bound[target_image],
        idx: Bound[_get_idx] = -1,
        dx: Bound[Tools.Parameters.dx] = 5.0,
    ):
        """Extend spline and fit to the filament at the starting edge."""
        idx = _assert_single_selection(idx)
        current_slice, spl = self._get_slice_and_spline(idx)
        fit = spl.extend_filament_left(
            image.data[current_slice], dx, width=11, spline_error=3e-2
        )
        self._update_paths(idx, fit, current_slice)

    @Tabs.Spline.Right.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "extfit_r.png")
    def extend_and_fit_right(
        self,
        image: Bound[target_image],
        idx: Bound[_get_idx] = -1,
        dx: Bound[Tools.Parameters.dx] = 5.0,
    ):
        """Extend spline and fit to the filament at the ending edge."""
        idx = _assert_single_selection(idx)
        current_slice, spl = self._get_slice_and_spline(idx)
        fit = spl.extend_filament_right(
            image.data[current_slice], dx, width=11, spline_error=3e-2
        )
        self._update_paths(idx, fit, current_slice)

    @Tabs.Spline.Left.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "clip_l.png")
    def clip_left(
        self, idx: Bound[_get_idx] = -1, dx: Bound[Tools.Parameters.dx] = 5.0
    ):
        """Clip spline at the starting edge."""
        idx = _assert_single_selection(idx)
        current_slice, spl = self._get_slice_and_spline(idx)
        start = dx / spl.length()
        fit = spl.clip(start, 1.0)
        self._update_paths(idx, fit, current_slice)

    @Tabs.Spline.Right.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "clip_r.png")
    def clip_right(
        self, idx: Bound[_get_idx] = -1, dx: Bound[Tools.Parameters.dx] = 5.0
    ):
        """Clip spline at the ending edge."""
        idx = _assert_single_selection(idx)
        current_slice, spl = self._get_slice_and_spline(idx)
        stop = 1.0 - dx / spl.length()
        fit = spl.clip(0.0, stop)
        self._update_paths(idx, fit, current_slice)

    @Tabs.Spline.Left.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "erf_l.png")
    def clip_left_at_inflection(
        self,
        image: Bound[target_image],
        idx: Bound[_get_idx] = -1,
    ):
        """Clip spline at the inflection point at starting edge."""
        idx = _assert_single_selection(idx)
        current_slice, spl = self._get_slice_and_spline(idx)
        fit = spl.clip_at_inflection_left(
            image.data[current_slice],
            callback=self._show_fitting_result,
        )
        self._update_paths(idx, fit, current_slice)

    @Tabs.Spline.Right.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "erf_r.png")
    def clip_right_at_inflection(
        self,
        image: Bound[target_image],
        idx: Bound[_get_idx] = -1,
    ):
        """Clip spline at the inflection point at ending edge."""
        idx = _assert_single_selection(idx)
        current_slice, spl = self._get_slice_and_spline(idx)
        fit = spl.clip_at_inflection_right(
            image.data[current_slice],
            callback=self._show_fitting_result,
        )
        self._update_paths(idx, fit, current_slice)

    @Tabs.Spline.Both.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "erf2.png")
    def clip_at_inflections(
        self,
        image: Bound[target_image],
        idx: Bound[_get_idx] = -1,
    ):
        """Clip spline at the inflection points at both ends."""
        indices = _arrange_selection(idx)
        for i in indices:
            current_slice, spl = self._get_slice_and_spline(i)
            out = spl.clip_at_inflections(
                image.data[current_slice],
                callback=self._show_fitting_result,
            )
            self._update_paths(i, out, current_slice)

    def _show_fitting_result(self, opt: _opt.Optimizer, prof: np.ndarray):
        """Callback function for error function fitting"""
        sg_min, sg_max = self.Tools.Parameters.sigma_range
        if isinstance(opt, (_opt.GaussianOptimizer, _opt.ErfOptimizer)):
            valid = sg_min <= opt.params.sg <= sg_max
        elif isinstance(opt, _opt.TwosideErfOptimizer):
            valid0 = sg_min <= opt.params.sg0 <= sg_max
            valid1 = sg_min <= opt.params.sg1 <= sg_max
            valid = valid0 and valid1
        else:
            raise NotImplementedError
        ndata = prof.size
        xdata = np.arange(ndata)
        ydata = opt.sample(xdata)
        self.Output._plot(xdata, prof, color="gray", alpha=0.7, lw=1)
        self.Output._plot(xdata, ydata, clear=False, color="red", lw=2)
        if not valid:
            self.Output.plt.text(
                0, np.min(ydata), "Sigma out of range.", color="crimson"
            )
        self.Output._set_labels("Data points", "Intensity")

    @Tabs.Measure.wraps
    def measure_length(self, idx: Bound[_get_idx] = -1):
        _, spl = self._get_slice_and_spline(idx)
        print(spl.length())

    @Tabs.Measure.wraps
    def measure_length_all(self):
        data = []
        for idx in range(self.layer_paths.nshapes):
            _, spl = self._get_slice_and_spline(idx)
            data.append(spl.length())
        view_in_table({"length": data}, self)

    @Tabs.Measure.wraps
    def plot_curvature(
        self,
        idx: Bound[_get_idx] = -1,
    ):
        """Plot curvature of filament."""
        _, spl = self._get_slice_and_spline(idx)
        length = spl.length()
        x = np.linspace(0, 1, int(spl.length()))
        cv = spl.curvature(x)
        self.Output._plot(x * length, cv)
        self.Output._set_labels("Position (px)", "Curvature")

    @Tabs.Measure.wraps
    def plot_profile(
        self,
        image: Bound[target_image],
        idx: Bound[_get_idx] = -1,
    ):
        """Plot intensity profile."""
        current_slice, spl = self._get_slice_and_spline(idx)
        prof = spl.get_profile(image.data[current_slice])
        length = spl.length()
        x = np.linspace(0, 1, int(length)) * length
        self.Output._plot(x, prof)
        self.Output._set_labels("Position (px)", "Intensity")

    @Tools.Layers.wraps
    @set_options(wlayers={"layout": "vertical", "label": "weight x layer"})
    def create_total_intensity(self, wlayers: List[Tuple[weight, Image]]):
        """Create a total intensity layer from multiple images."""
        weights = [t[0] for t in wlayers]
        imgs = [t[1].data for t in wlayers]
        names = [t[1].name for t in wlayers]
        tot = sum(w * img for w, img in zip(weights, imgs))

        outs = set()
        for name in names:
            matched = re.findall(r"\[.*\] (.+)", name)
            if matched:
                outs.add(matched[0])
        if len(outs) == 1:
            new_name = f"[Total] {outs.pop()}"
        else:
            new_name = f"[Total] {outs.pop()} etc."
        self.parent_viewer.add_image(tot, name=new_name, visible=False)

    @Tabs.Spline.Both.wraps
    @set_design(**ICON_KWARGS, icon_path=ICON_DIR / "del.png")
    def delete_current(self, idx: Bound[_get_idx]):
        """Delete selected (or the last) path."""
        if isinstance(idx, int):
            idx = {idx}
        self.layer_paths.selected_data = idx
        self.layer_paths.remove_selected()

    @Tools.Others.wraps
    @do_not_record
    def create_macro(self):
        """Create an executable Python script."""
        import macrokit as mk

        new = self.macro.widget.duplicate()
        v = mk.Expr("getattr", [mk.symbol(self), "parent_viewer"])
        new.value = self.macro.format([(mk.symbol(self.parent_viewer), v)])
        new.show()
        return None

    @nogui
    @do_not_record
    def get_spline(self, idx: int) -> Spline:
        _, spl = self._get_slice_and_spline(idx)
        return spl


def _split_slice_and_path(
    data: np.ndarray,
) -> Tuple[Tuple[int, ...], np.ndarray]:
    if data.shape[1] == 2:
        return (), data
    sl: np.ndarray = np.unique(data[:, :-2], axis=0)
    if sl.shape[0] != 1:
        raise ValueError("Spline is not in 2D")
    return tuple(sl.ravel().astype(np.int64)), data[:, -2:]


def view_in_table(data: dict, parent: MagicTemplate):
    table = Table(data)
    table.native.setParent(parent.native, table.native.windowFlags())
    table.show()


def _toggle_target_images(shapes: Shapes, visible: bool):
    """Set target images to visible or invisible."""
    img_layers: List[Image] = shapes.metadata.get(TARGET_IMG_LAYERS, [])
    for img_layer in img_layers:
        img_layer.visible = visible


def _assert_single_selection(idx: Union[int, Set[int]]) -> int:
    if isinstance(idx, set):
        if len(idx) != 1:
            raise ValueError("Multiple selection")
        return idx.pop()
    return idx


def _arrange_selection(idx: Union[int, Set[int]]) -> List[int]:
    if isinstance(idx, int):
        return [idx]
    else:
        return sorted(list(idx), reverse=True)
