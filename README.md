[![License][license-shield]](LICENSE.md)

[![hacs][hacsbadge]](hacs)
![Project Maintenance][maintenance-shield]


# Prosenic Home Assistant component
A full featured Homeassistant component to control Prosenic vacuum cleaner locally without the cloud. 
This component is based on the underlying PyTuya library available [here](https://github.com/clach04/python-tuya).

## Towards Homeassistant official integration
My personal goal is to make this component fully compliant with Homeassistant, so 
that it may be added as the official library to handle Prosenic vacuum cleaners. 
However, before pushing a PullRequest to the official Homeassistant repository, I would like to share it to some users.
In this way we can test it massively, check it for any bug and make it **robust enough** to be seamlessly integrated 
with Homeassistant.

For now, the component has been integrated as a custom component into [HACS](hacs).

## Installation & configuration
You can install this component in two ways: via HACS or manually.
HACS is a nice community-maintained components manager, which allows you to install git-hub hosted components in a few clicks.
If you have already HACS installed on your HomeAssistant, it's better to go with that.
On the other hand, if you don't have HACS installed or if you don't plan to install it, then you can use manual installation.


[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-CUSTOM-inactive?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/edenhaus/ha-prosenic?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/Maintainer-Robert%20Resch-blue?style=for-the-badge
