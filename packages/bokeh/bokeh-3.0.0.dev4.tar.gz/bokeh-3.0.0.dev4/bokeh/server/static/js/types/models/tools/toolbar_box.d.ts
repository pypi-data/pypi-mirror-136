import * as p from "../../core/properties";
import { Location } from "../../core/enums";
import { ToolbarBase, ToolbarBaseView } from "./toolbar_base";
import { LayoutDOM, LayoutDOMView } from "../layouts/layout_dom";
export declare class ToolbarBoxView extends LayoutDOMView {
    model: ToolbarBox;
    initialize(): void;
    get toolbar_view(): ToolbarBaseView;
    connect_signals(): void;
    get child_models(): LayoutDOM[];
    _update_layout(): void;
    after_layout(): void;
}
export declare namespace ToolbarBox {
    type Attrs = p.AttrsOf<Props>;
    type Props = LayoutDOM.Props & {
        toolbar: p.Property<ToolbarBase>;
        toolbar_location: p.Property<Location>;
    };
}
export interface ToolbarBox extends ToolbarBox.Attrs {
}
export declare class ToolbarBox extends LayoutDOM {
    properties: ToolbarBox.Props;
    __view_type__: ToolbarBoxView;
    constructor(attrs?: Partial<ToolbarBox.Attrs>);
}
//# sourceMappingURL=toolbar_box.d.ts.map