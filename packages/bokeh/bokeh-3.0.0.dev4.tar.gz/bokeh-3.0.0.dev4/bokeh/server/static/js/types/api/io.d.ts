import { ViewOf } from "../core/view";
import { LayoutDOM } from "../models/layouts/layout_dom";
export declare function show<T extends LayoutDOM>(obj: T, target?: HTMLElement | string): Promise<ViewOf<T>>;
export declare function show<T extends LayoutDOM>(obj: T[], target?: HTMLElement | string): Promise<ViewOf<T>[]>;
//# sourceMappingURL=io.d.ts.map