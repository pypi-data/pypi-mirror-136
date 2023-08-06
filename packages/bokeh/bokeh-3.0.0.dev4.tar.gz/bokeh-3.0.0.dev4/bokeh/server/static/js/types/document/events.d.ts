import { Document } from "./document";
import { Data } from "../core/types";
import { HasProps } from "../core/has_props";
import { Ref } from "../core/util/refs";
import { PatchSet } from "../models/sources/column_data_source";
import { equals, Equatable, Comparator } from "../core/util/eq";
import { serialize, Serializable, Serializer } from "../core/serializer";
export declare type ModelChanged = {
    kind: "ModelChanged";
    model: Ref;
    attr: string;
    new: unknown;
    hint?: unknown;
};
export declare type MessageSent = {
    kind: "MessageSent";
    msg_type: string;
    msg_data?: unknown;
};
export declare type TitleChanged = {
    kind: "TitleChanged";
    title: string;
};
export declare type RootAdded = {
    kind: "RootAdded";
    model: Ref;
};
export declare type RootRemoved = {
    kind: "RootRemoved";
    model: Ref;
};
export declare type ColumnDataChanged = {
    kind: "ColumnDataChanged";
    column_source: Ref;
    new: Data;
    cols?: string[];
};
export declare type ColumnsStreamed = {
    kind: "ColumnsStreamed";
    column_source: Ref;
    data: Data;
    rollover?: number;
};
export declare type ColumnsPatched = {
    kind: "ColumnsPatched";
    column_source: Ref;
    patches: PatchSet<unknown>;
};
export declare type DocumentChanged = ModelChanged | MessageSent | TitleChanged | RootAdded | RootRemoved | ColumnDataChanged | ColumnsStreamed | ColumnsPatched;
export declare abstract class DocumentEvent implements Equatable {
    readonly document: Document;
    constructor(document: Document);
    get [Symbol.toStringTag](): string;
    [equals](that: this, cmp: Comparator): boolean;
}
export declare class DocumentEventBatch<T extends DocumentChangedEvent> extends DocumentEvent {
    readonly events: T[];
    constructor(document: Document, events: T[]);
    [equals](that: this, cmp: Comparator): boolean;
}
export declare abstract class DocumentChangedEvent extends DocumentEvent implements Serializable {
    abstract [serialize](serializer: Serializer): DocumentChanged;
}
export declare class MessageSentEvent extends DocumentChangedEvent {
    readonly msg_type: string;
    readonly msg_data: unknown;
    constructor(document: Document, msg_type: string, msg_data: unknown);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](serializer: Serializer): DocumentChanged;
}
export declare class ModelChangedEvent extends DocumentChangedEvent {
    readonly model: HasProps;
    readonly attr: string;
    readonly old: unknown;
    readonly new_: unknown;
    readonly hint?: DocumentChangedEvent | undefined;
    constructor(document: Document, model: HasProps, attr: string, old: unknown, new_: unknown, hint?: DocumentChangedEvent | undefined);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](serializer: Serializer): DocumentChanged;
}
export declare class ColumnsPatchedEvent extends DocumentChangedEvent {
    readonly column_source: Ref;
    readonly patches: PatchSet<unknown>;
    constructor(document: Document, column_source: Ref, patches: PatchSet<unknown>);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): ColumnsPatched;
}
export declare class ColumnDataChangedEvent extends DocumentChangedEvent {
    readonly column_source: Ref;
    readonly new_: Data;
    readonly cols?: string[] | undefined;
    constructor(document: Document, column_source: Ref, new_: Data, cols?: string[] | undefined);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): ColumnDataChanged;
}
export declare class ColumnsStreamedEvent extends DocumentChangedEvent {
    readonly column_source: Ref;
    readonly data: Data;
    readonly rollover?: number | undefined;
    constructor(document: Document, column_source: Ref, data: Data, rollover?: number | undefined);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): ColumnsStreamed;
}
export declare class TitleChangedEvent extends DocumentChangedEvent {
    readonly title: string;
    constructor(document: Document, title: string);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): TitleChanged;
}
export declare class RootAddedEvent extends DocumentChangedEvent {
    readonly model: HasProps;
    constructor(document: Document, model: HasProps);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](serializer: Serializer): RootAdded;
}
export declare class RootRemovedEvent extends DocumentChangedEvent {
    readonly model: HasProps;
    constructor(document: Document, model: HasProps);
    [equals](that: this, cmp: Comparator): boolean;
    [serialize](_serializer: Serializer): RootRemoved;
}
//# sourceMappingURL=events.d.ts.map