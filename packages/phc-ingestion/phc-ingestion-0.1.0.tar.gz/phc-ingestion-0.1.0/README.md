# phc-ingestion

Python package for PHC genomic ingestions. Currently, only processing for Foundation files is supported.

## Developing

This repo uses [PDM](https://pdm.fming.dev/latest/). Install PDM and then install dependencies with `pdm install`.

### A note about running tests

This repository depends on the `bgzip` tool. This tool is included in the `tabix` package. Ubuntu users can install this package with `apt install tabix`.
MacOS users, or Ubuntu users who do not wish to install `tabix`, can run the tests within a Docker container that already has `tabix` installed. Simply use `./pdm-docker.sh run test`.
