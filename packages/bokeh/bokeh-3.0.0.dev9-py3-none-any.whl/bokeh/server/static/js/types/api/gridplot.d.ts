import { GridPlot } from "../models/plots";
import { Tool } from "../models/tools/tool";
import { ToolLike } from "../models/tools/tool_proxy";
import { LayoutDOM } from "../models/layouts/layout_dom";
import { SizingMode, Location } from "../core/enums";
import { Matrix } from "../core/util/matrix";
export declare type GridPlotOpts = {
    toolbar_location?: Location | null;
    merge_tools?: boolean;
    sizing_mode?: SizingMode;
    width?: number;
    height?: number;
};
export declare function group_tools(tools: ToolLike<Tool>[]): ToolLike<Tool>[];
export declare function gridplot(children: (LayoutDOM | null)[][] | Matrix<LayoutDOM | null>, options?: GridPlotOpts): GridPlot;
//# sourceMappingURL=gridplot.d.ts.map