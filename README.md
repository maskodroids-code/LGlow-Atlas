# LGlow Atlas

[Project website](https://maskodroid.github.io/lglow-atlas/) · [GitHub repository](https://github.com/Maskodroid/lglow-atlas)

LGlow Atlas is a fork of [LGlow](https://github.com/IrvingGuerra/lglow) for LG webOS TVs. It adds weather for a manually selected city and a full-screen framed art screensaver.

## Features

- **City-based weather.** Select the location icon, type a city using the TV keyboard, and choose a search result. The home screen shows the selected city, current temperature, conditions, wind speed, humidity, and UV index.
- **Home layout.** Date and time sit to the left of the top controls. The weather and location icons follow the light or dark theme.
- **Framed art screensaver.** Images retain their proportions and full frame. The screensaver fades between images and displays them without text or overlays. The interval selector offers 30 seconds, 1 minute, 3 minutes, and 5 minutes.
- **Chilean indicators.** The Chile dashboard includes a financial indicators panel. The weather location is configurable independently.

## Compatibility

The adaptations in this repository were developed against the following model and firmware combinations. Check all three fields before choosing a patch.

| LG model | Firmware | Home application |
| --- | --- | --- |
| 43UN7300PSC | 04.64.00 | `com.webos.app.fullhome` |
| 50UP7500PSF | 03.53.45 | `com.webos.app.home` |

See the [firmware notes](CAMBIOS-TV.md) and the original LGlow documentation ([English](README.en.md), [Español](README.upstream.es.md)) for the scope of the upstream installer and the local adaptations.

## Installation

1. Identify the TV model and firmware, then check whether the firmware supports root access. Follow the [root guide](docs/en/01-root.md), read the [Developer Mode notes](docs/en/02-developer-mode-trap.md), and set up [SSH access](docs/en/03-access-and-updates.md).
2. Read the [installation guide](docs/en/04-install-home.md) and [rollback guide](docs/en/07-troubleshooting-and-uninstall.md) before applying changes. Back up the affected files and verify that each patch matches your firmware. If a check fails, stop and follow the [porting guide](docs/en/05-how-it-works.md).
3. Install the compatible LGlow base. Apply the Atlas changes from [adaptaciones/](adaptaciones/) and [herramientas-locales/](herramientas-locales/) using the [firmware notes](CAMBIOS-TV.md). The upstream installer installs the base. The Atlas scripts are references from individual deployments and require review of their paths, target and prerequisites.
4. Add images you have permission to use. The local project includes a separate image collection under `recursos-locales/salvapantallas/Con marco`. For a GitHub checkout, supply your own image files and set the path in the screensaver script.
5. Check that Home opens LGlow. Use the location icon to choose a city, then let the TV idle and verify that the screensaver starts, transitions between images, and retains its settings after restarting.

## Credits and license

LGlow Atlas builds on [LGlow](https://github.com/IrvingGuerra/lglow). Weather and city search use [Open-Meteo](https://open-meteo.com/). See [LICENSE](LICENSE) for the MIT license. Image and icon redistribution permissions are separate from the code license.
