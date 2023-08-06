import { ModelResolver } from "../base";
import { HasProps } from "./has_props";
import { ID } from "./types";
import { Struct } from "./util/refs";
import { Buffers } from "./util/serialization";
import { type Document } from "../document";
export declare type RefMap = Map<ID, HasProps>;
export declare class Deserializer {
    static decode(value: unknown): unknown;
    static _instantiate_object(id: string, type: string, resolver: ModelResolver): HasProps;
    static _instantiate_references_json(references_json: Struct[], existing_models: RefMap, resolver: ModelResolver): RefMap;
    static _resolve_refs(value: unknown, old_references: RefMap, new_references: RefMap, buffers: Buffers): unknown;
    static _initialize_references_json(references_json: Struct[], old_references: RefMap, new_references: RefMap, buffers: Buffers, doc: Document | null): void;
}
//# sourceMappingURL=deserializer.d.ts.map