var _a;
import { Model } from "../../model";
import { DOMComponentView } from "../../core/dom_view";
export class UIElementView extends DOMComponentView {
}
UIElementView.__name__ = "UIElementView";
export class UIElement extends Model {
    constructor(attrs) {
        super(attrs);
    }
}
_a = UIElement;
UIElement.__name__ = "UIElement";
(() => {
    _a.define(({ Boolean }) => ({
        visible: [Boolean, true],
    }));
})();
//# sourceMappingURL=ui_element.js.map