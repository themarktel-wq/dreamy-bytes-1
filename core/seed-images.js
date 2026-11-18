/* Sample photos used for the starter catalogue (free Unsplash stock in assets/img). Replace from Admin → Products. */
(function (root) {
  const I = (n) => 'assets/img/' + n + '.jpg';
  const SEED_IMAGES = {
    'case-leather': I('case-leather'), 'case-carbon': I('case-carbon'),
    charger: I('charger'), cables: I('cables'), airpods: I('airpods'), 'earbuds-blue': I('earbuds-blue'), 'earbuds-dark': I('earbuds-dark'),
    magsafe: I('magsafe'), 'watch-classic': I('watch-classic'),
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = { SEED_IMAGES }; else root.LMSeedImages = SEED_IMAGES;
})(typeof self !== 'undefined' ? self : this);
