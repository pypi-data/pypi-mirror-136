import { equals } from "../core/util/eq";
import { serialize } from "../core/serializer";
export class DocumentEvent {
    constructor(document) {
        this.document = document;
    }
    get [Symbol.toStringTag]() {
        return this.constructor.__name__;
    }
    [equals](that, cmp) {
        return cmp.eq(this.document, that.document);
    }
}
DocumentEvent.__name__ = "DocumentEvent";
export class DocumentEventBatch extends DocumentEvent {
    constructor(document, events) {
        super(document);
        this.events = events;
    }
    [equals](that, cmp) {
        return super[equals](that, cmp) &&
            cmp.eq(this.events, that.events);
    }
}
DocumentEventBatch.__name__ = "DocumentEventBatch";
export class DocumentChangedEvent extends DocumentEvent {
}
DocumentChangedEvent.__name__ = "DocumentChangedEvent";
export class MessageSentEvent extends DocumentChangedEvent {
    constructor(document, msg_type, msg_data) {
        super(document);
        this.msg_type = msg_type;
        this.msg_data = msg_data;
    }
    [equals](that, cmp) {
        return super[equals](that, cmp) &&
            cmp.eq(this.msg_type, that.msg_type) &&
            cmp.eq(this.msg_data, that.msg_data);
    }
    [serialize](serializer) {
        const value = this.msg_data;
        const value_serialized = serializer.to_serializable(value);
        return {
            kind: "MessageSent",
            msg_type: this.msg_type,
            msg_data: value_serialized,
        };
    }
}
MessageSentEvent.__name__ = "MessageSentEvent";
export class ModelChangedEvent extends DocumentChangedEvent {
    constructor(document, model, attr, old, new_, hint) {
        super(document);
        this.model = model;
        this.attr = attr;
        this.old = old;
        this.new_ = new_;
        this.hint = hint;
    }
    [equals](that, cmp) {
        return super[equals](that, cmp) &&
            cmp.eq(this.model, that.model) &&
            cmp.eq(this.attr, that.attr) &&
            cmp.eq(this.old, that.old) &&
            cmp.eq(this.new_, that.new_) &&
            cmp.eq(this.hint, that.hint);
    }
    [serialize](serializer) {
        if (this.hint != null)
            return serializer.to_serializable(this.hint);
        const value = this.new_;
        const value_serialized = serializer.to_serializable(value);
        if (this.model != value) {
            // we know we don't want a whole new copy of the obj we're
            // patching unless it's also the value itself
            serializer.remove_def(this.model);
        }
        return {
            kind: "ModelChanged",
            model: this.model.ref(),
            attr: this.attr,
            new: value_serialized,
        };
    }
}
ModelChangedEvent.__name__ = "ModelChangedEvent";
export class ColumnsPatchedEvent extends DocumentChangedEvent {
    constructor(document, column_source, patches) {
        super(document);
        this.column_source = column_source;
        this.patches = patches;
    }
    [equals](that, cmp) {
        return super[equals](that, cmp) &&
            cmp.eq(this.column_source, that.column_source) &&
            cmp.eq(this.patches, that.patches);
    }
    [serialize](_serializer) {
        return {
            kind: "ColumnsPatched",
            column_source: this.column_source,
            patches: this.patches,
        };
    }
}
ColumnsPatchedEvent.__name__ = "ColumnsPatchedEvent";
export class ColumnDataChangedEvent extends DocumentChangedEvent {
    constructor(document, column_source, new_, cols) {
        super(document);
        this.column_source = column_source;
        this.new_ = new_;
        this.cols = cols;
    }
    [equals](that, cmp) {
        return super[equals](that, cmp) &&
            cmp.eq(this.column_source, that.column_source) &&
            cmp.eq(this.new_, that.new_) &&
            cmp.eq(this.cols, that.cols);
    }
    [serialize](_serializer) {
        return {
            kind: "ColumnDataChanged",
            column_source: this.column_source,
            new: this.new_,
            cols: this.cols,
        };
    }
}
ColumnDataChangedEvent.__name__ = "ColumnDataChangedEvent";
export class ColumnsStreamedEvent extends DocumentChangedEvent {
    constructor(document, column_source, data, rollover) {
        super(document);
        this.column_source = column_source;
        this.data = data;
        this.rollover = rollover;
    }
    [equals](that, cmp) {
        return super[equals](that, cmp) &&
            cmp.eq(this.column_source, that.column_source) &&
            cmp.eq(this.data, that.data) &&
            cmp.eq(this.rollover, that.rollover);
    }
    [serialize](_serializer) {
        return {
            kind: "ColumnsStreamed",
            column_source: this.column_source,
            data: this.data,
            rollover: this.rollover,
        };
    }
}
ColumnsStreamedEvent.__name__ = "ColumnsStreamedEvent";
export class TitleChangedEvent extends DocumentChangedEvent {
    constructor(document, title) {
        super(document);
        this.title = title;
    }
    [equals](that, cmp) {
        return super[equals](that, cmp) &&
            cmp.eq(this.title, that.title);
    }
    [serialize](_serializer) {
        return {
            kind: "TitleChanged",
            title: this.title,
        };
    }
}
TitleChangedEvent.__name__ = "TitleChangedEvent";
export class RootAddedEvent extends DocumentChangedEvent {
    constructor(document, model) {
        super(document);
        this.model = model;
    }
    [equals](that, cmp) {
        return super[equals](that, cmp) &&
            cmp.eq(this.model, that.model);
    }
    [serialize](serializer) {
        return {
            kind: "RootAdded",
            model: serializer.to_serializable(this.model),
        };
    }
}
RootAddedEvent.__name__ = "RootAddedEvent";
export class RootRemovedEvent extends DocumentChangedEvent {
    constructor(document, model) {
        super(document);
        this.model = model;
    }
    [equals](that, cmp) {
        return super[equals](that, cmp) &&
            cmp.eq(this.model, that.model);
    }
    [serialize](_serializer) {
        return {
            kind: "RootRemoved",
            model: this.model.ref(),
        };
    }
}
RootRemovedEvent.__name__ = "RootRemovedEvent";
//# sourceMappingURL=events.js.map