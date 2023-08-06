import { ToolbarBase } from "./toolbar_base";
import { Tool } from "./tool";
import { ToolProxy } from "./tool_proxy";
import * as p from "../../core/properties";
export declare namespace ProxyToolbar {
    type Attrs = p.AttrsOf<Props>;
    type Props = ToolbarBase.Props;
}
export interface ProxyToolbar extends ProxyToolbar.Attrs {
}
export declare class ProxyToolbar extends ToolbarBase {
    properties: ProxyToolbar.Props;
    constructor(attrs?: Partial<ProxyToolbar.Attrs>);
    _proxied_tools: (Tool | ToolProxy)[];
    initialize(): void;
    protected _merge_tools(): void;
}
//# sourceMappingURL=proxy_toolbar.d.ts.map