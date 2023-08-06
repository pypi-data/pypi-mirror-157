import { GridPlot, Plot } from "../models/plots";
import { ToolProxy } from "../models/tools/tool_proxy";
import { Toolbar } from "../models/tools/toolbar";
import { Matrix } from "../core/util/matrix";
import { is_equal } from "../core/util/eq";
export function group_tools(tools) {
    const by_type = new Map();
    const computed = [];
    for (const tool of tools) {
        if (tool instanceof ToolProxy) {
            computed.push(tool);
        }
        else {
            const attrs = tool.attributes;
            if ("overlay" in attrs)
                delete attrs.overlay;
            const proto = tool.constructor.prototype;
            let values = by_type.get(proto);
            if (values == null)
                by_type.set(proto, values = new Set());
            values.add({ tool, attrs });
        }
    }
    for (const tools of by_type.values()) {
        while (tools.size != 0) {
            const [head, ...tail] = tools;
            tools.delete(head);
            const group = [head.tool];
            for (const item of tail) {
                if (is_equal(item.attrs, head.attrs)) {
                    group.push(item.tool);
                    tools.delete(item);
                }
            }
            if (group.length == 1)
                computed.push(group[0]);
            else
                computed.push(new ToolProxy({ tools: group }));
        }
    }
    return computed;
}
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
    const toolbar = new Toolbar({ tools: !merge_tools ? tools : group_tools(tools) });
    return new GridPlot({ children: items, toolbar, toolbar_location, sizing_mode });
}
//# sourceMappingURL=gridplot.js.map