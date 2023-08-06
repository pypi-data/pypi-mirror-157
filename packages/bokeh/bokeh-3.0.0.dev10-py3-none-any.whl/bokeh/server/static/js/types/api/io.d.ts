import { Document } from "../document";
import { ViewOf } from "../core/view";
import { HasProps } from "../core/has_props";
import { LayoutDOM } from "../models/layouts/layout_dom";
export declare function show<T extends LayoutDOM>(obj: T, target?: HTMLElement | string): Promise<ViewOf<T>>;
export declare function show<T extends LayoutDOM>(obj: T[], target?: HTMLElement | string): Promise<ViewOf<T>[]>;
export declare function show(obj: Document, target?: HTMLElement | string): Promise<ViewOf<HasProps>[]>;
export declare function show(obj: LayoutDOM | Document, target?: HTMLElement | string): Promise<ViewOf<HasProps> | ViewOf<HasProps>[]>;
//# sourceMappingURL=io.d.ts.map