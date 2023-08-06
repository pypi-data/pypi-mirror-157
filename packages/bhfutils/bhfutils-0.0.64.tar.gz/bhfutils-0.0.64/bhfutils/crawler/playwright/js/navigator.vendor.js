Object.defineProperty(Object.getPrototypeOf(navigator), 'vendor', {
    get: () => 'Apple Computer, Inc.',
})
