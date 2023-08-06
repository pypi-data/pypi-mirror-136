import { GridPlot, Plot, LayoutDOM } from "./models";
import { SizingMode, Location } from "../core/enums";
import { Matrix } from "../core/util/matrix";
export declare type GridPlotOpts = {
    toolbar_location?: Location | null;
    merge_tools?: boolean;
    sizing_mode?: SizingMode;
    width?: number;
    height?: number;
};
export declare function gridplot(children: (LayoutDOM | null)[][] | Matrix<Plot | null>, options?: GridPlotOpts): GridPlot;
//# sourceMappingURL=gridplot.d.ts.map