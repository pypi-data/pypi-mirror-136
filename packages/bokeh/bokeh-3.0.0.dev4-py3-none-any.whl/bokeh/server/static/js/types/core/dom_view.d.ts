import { View } from "./view";
export interface DOMView extends View {
    constructor: Function & {
        tag_name: keyof HTMLElementTagNameMap;
    };
}
export declare abstract class DOMView extends View {
    static tag_name: keyof HTMLElementTagNameMap;
    el: Node;
    shadow_el?: ShadowRoot;
    get children_el(): Node;
    readonly root: DOMView;
    initialize(): void;
    remove(): void;
    css_classes(): string[];
    styles(): string[];
    render(): void;
    renderTo(element: Node): void;
    protected _createElement(): this["el"];
}
export declare abstract class DOMComponentView extends DOMView {
    el: HTMLElement;
    shadow_el: ShadowRoot;
    stylesheet_els: HTMLStyleElement[];
    initialize(): void;
    styles(): string[];
    empty(): void;
}
//# sourceMappingURL=dom_view.d.ts.map