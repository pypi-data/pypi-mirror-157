if (opts.navigator_platform) {
    Object.defineProperty(Object.getPrototypeOf(navigator), 'platform', {
        get: () => 'iPhone',
    })
}