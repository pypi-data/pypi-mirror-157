(utils) => {
  utils.replaceGetterWithProxy(
    Object.getPrototypeOf(navigator),
    'vendor',
    utils.makeHandler().getterValue(opts.navigator_vendorm)
  )
}, {
  opts: this.opts
}
