import { View } from "./view";
import { createElement, remove, empty, style } from "./dom";
import base_css from "../styles/base.css";
const has_adopted_stylesheets = "adoptedStyleSheets" in ShadowRoot.prototype;
export class DOMView extends View {
    get children_el() {
        return this.shadow_el ?? this.el;
    }
    initialize() {
        super.initialize();
        this.el = this._createElement();
    }
    remove() {
        remove(this.el);
        super.remove();
    }
    css_classes() {
        return [];
    }
    styles() {
        return [];
    }
    render() { }
    renderTo(element) {
        element.appendChild(this.el);
        this.render();
        this._has_finished = true;
        this.notify_finished();
    }
    _createElement() {
        return createElement(this.constructor.tag_name, { class: this.css_classes() });
    }
}
DOMView.__name__ = "DOMView";
DOMView.tag_name = "div";
export class DOMComponentView extends DOMView {
    constructor() {
        super(...arguments);
        this.stylesheet_els = [];
    }
    initialize() {
        super.initialize();
        this.shadow_el = this.el.attachShadow({ mode: "open" });
        if (has_adopted_stylesheets) {
            const sheets = [];
            for (const style of this.styles()) {
                const sheet = new CSSStyleSheet();
                sheet.replaceSync(style);
                sheets.push(sheet);
            }
            this.shadow_el.adoptedStyleSheets = sheets;
        }
        else {
            for (const style_ of this.styles()) {
                const stylesheet_el = style({}, style_);
                this.stylesheet_els.push(stylesheet_el);
                this.shadow_el.appendChild(stylesheet_el);
            }
        }
    }
    styles() {
        return [base_css];
    }
    empty() {
        empty(this.shadow_el);
        for (const stylesheet_el of this.stylesheet_els) {
            this.shadow_el.appendChild(stylesheet_el);
        }
    }
}
DOMComponentView.__name__ = "DOMComponentView";
//# sourceMappingURL=dom_view.js.map