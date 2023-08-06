import { Document } from "../document";
import * as embed from "../embed";
import { dom_ready } from "../core/dom";
import { isString, isArray } from "../core/util/types";
export async function show(obj, target) {
    const doc = new Document();
    for (const item of isArray(obj) ? obj : [obj])
        doc.add_root(item);
    await dom_ready();
    let element;
    if (target == null) {
        element = document.body;
    }
    else if (isString(target)) {
        const found = document.querySelector(target);
        if (found != null && found instanceof HTMLElement)
            element = found;
        else
            throw new Error(`'${target}' selector didn't match any elements`);
    }
    else if (target instanceof HTMLElement) {
        element = target;
    }
    else if (typeof $ !== "undefined" && target instanceof $) {
        element = target[0];
    }
    else {
        throw new Error("target should be HTMLElement, string selector, $ or null");
    }
    const views = await embed.add_document_standalone(doc, element);
    return new Promise((resolve, _reject) => {
        const result = isArray(obj) ? views : views[0];
        if (doc.is_idle)
            resolve(result);
        else
            doc.idle.connect(() => resolve(result));
    });
}
//# sourceMappingURL=io.js.map