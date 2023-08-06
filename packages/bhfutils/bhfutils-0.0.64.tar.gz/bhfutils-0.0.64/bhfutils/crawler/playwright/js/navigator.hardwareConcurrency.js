// Set the hardwareConcurrency to 4 (optionally configurable with hardwareConcurrency)
(utils) => {
  utils.replaceGetterWithProxy(
    Object.getPrototypeOf(navigator),
    'hardwareConcurrency',
    utils.makeHandler().getterValue(-1)
  )
}, {
  opts: this.opts
}