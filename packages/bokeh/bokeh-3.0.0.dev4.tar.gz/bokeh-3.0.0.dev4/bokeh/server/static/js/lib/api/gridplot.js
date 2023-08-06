import { GridPlot, Plot, ProxyToolbar, Toolbar } from "./models";
import { Matrix } from "../core/util/matrix";
export function gridplot(children, options = {}) {
    const toolbar_location = options.toolbar_location;
    const merge_tools = options.merge_tools ?? true;
    const sizing_mode = options.sizing_mode;
    const matrix = Matrix.from(children);
    const items = [];
    const tools = [];
    for (const [item, row, col] of matrix) {
        if (item == null)
            continue;
        if (item instanceof Plot) {
            if (merge_tools) {
                tools.push(...item.toolbar.tools);
                item.toolbar_location = null;
            }
        }
        if (options.width != null)
            item.width = options.width;
        if (options.height != null)
            item.height = options.height;
        items.push([item, row, col]);
    }
    const toolbar = (() => {
        if (!merge_tools)
            return new Toolbar({ tools });
        else
            return new ProxyToolbar({ tools });
    })();
    return new GridPlot({ children: items, sizing_mode, toolbar, toolbar_location });
}
//# sourceMappingURL=gridplot.js.map