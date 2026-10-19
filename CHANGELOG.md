# Changelog

All notable changes to Weather for Roku are documented here.

## [Unreleased]

### Added
- **7-day free trial.** The first 7 days after install are completely free
  with no purchase prompt; the monetization flow only begins once the trial
  expires. The install date is recorded on first launch, and the app stays in
  the trial if the device clock is missing or invalid.
- Declared `rsg_version=1.3` in the manifest (required for Channel Store
  submission).

### Changed
- **Entitlement gate is now catalog-first and fails open.** On launch the app
  checks the store catalog: if the product and its price can't be retrieved,
  the full app runs for free (no paywall). If they can, it checks for an
  existing purchase — owners get the full app, everyone else sees the purchase
  flow. A short safety timeout unlocks the app if the store never responds, so
  users are never trapped on a loading screen.

### Fixed
- Paywall price no longer falls back to an unrelated `$0.00` placeholder
  product; it trusts only the configured product's price.
- Em dash in the paywall subtitle now renders correctly (BrightScript doesn't
  support `\u` escapes).
- Suppressed a spurious "Order failed" status the store observer emits on
  launch before any purchase is attempted.
- **Entitlement race on slow networks.** A late `getPurchases` response that
  arrived after the safety timeout had already unlocked the app could pop the
  paywall over the running app (or re-launch it). Late store responses are now
  ignored once the gate is resolved, while user-initiated "Restore purchase"
  still works.
- The safety timeout is now re-armed for the purchase-lookup step so a slow
  catalog followed by a slow purchases lookup no longer unlocks the app for
  free prematurely.
- "Restore purchase" now clears its in-progress flag on success.

## [1.1.0] — 2026-07-15

### Added
- **Today's hourly outlook** — an always-on strip below the 7-day forecast
  showing the next 7 hours (time, conditions, and temperature). It's styled in
  the Today-tile color and expands from the Today tile, with each hour aligned
  under its matching day.

### Fixed
- ZIP entry keypad no longer jumps back to `1` after each digit; the highlight
  stays on the last selected key.

## [1.0.0] — 2026-07-13

Initial release.

- 7-day forecast with daily highs, lows, conditions, and chance of rain.
- Enter a US ZIP code once — it's saved locally and reused on every launch.
- Change location anytime by pressing `*` on the remote.
- On-device ZIP-to-location lookup (bundled Census data); no geocoding service.
- Forecast data from the U.S. National Weather Service.
- Custom weather art for each condition and a clean, minimal UI.
