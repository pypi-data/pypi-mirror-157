if (opts.max_touch_points) {
    Object.defineProperty(Object.getPrototypeOf(navigator), 'maxTouchPoints', {
        get: () => opts.max_touch_points,
    })
}
