# Changelog

All notable changes to Weather for Roku are documented here.

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
