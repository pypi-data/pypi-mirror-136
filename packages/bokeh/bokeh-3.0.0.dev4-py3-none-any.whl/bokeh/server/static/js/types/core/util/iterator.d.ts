export declare function enumerate<T>(seq: Iterable<T>): Iterable<[T, number]>;
export declare function join<T>(seq: Iterable<Iterable<T>>, separator?: () => T): Iterable<T>;
export declare function flat_map<T, U>(iterable: Iterable<T>, fn: (item: T, i: number) => Iterable<U>): Iterable<U>;
export declare function interleave<T>(seq: Iterable<T>, separator: () => T): Iterable<T>;
export declare function combinations<T>(seq: T[], r: number): Iterable<T[]>;
export declare function subsets<T>(seq: T[]): Iterable<T[]>;
//# sourceMappingURL=iterator.d.ts.map