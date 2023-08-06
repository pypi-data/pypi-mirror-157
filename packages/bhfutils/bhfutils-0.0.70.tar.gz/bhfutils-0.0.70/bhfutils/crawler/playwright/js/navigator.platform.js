(utils) => {
  utils.replaceGetterWithProxy(
    Object.getPrototypeOf(navigator),
    'platform',
    utils.makeHandler().getterValue(opts.navigator_platform)
  )
}, {
  opts: this.opts
}
