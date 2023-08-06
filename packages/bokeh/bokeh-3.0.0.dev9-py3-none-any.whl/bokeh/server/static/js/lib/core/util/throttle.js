export function throttle(func, wait) {
    let timeout = null;
    let previous = 0;
    let pending = false;
    return function () {
        return new Promise((resolve, reject) => {
            const later = function () {
                previous = Date.now();
                timeout = null;
                pending = false;
                try {
                    func();
                    resolve();
                }
                catch (error) {
                    reject(error);
                }
            };
            const now = Date.now();
            const remaining = wait - (now - previous);
            if (remaining <= 0 && !pending) {
                if (timeout != null) {
                    clearTimeout(timeout);
                }
                pending = true;
                requestAnimationFrame(later);
            }
            else if (timeout == null && !pending) {
                timeout = setTimeout(() => requestAnimationFrame(later), remaining);
            }
            else {
                resolve();
            }
        });
    };
}
//# sourceMappingURL=throttle.js.map