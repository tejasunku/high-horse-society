This is an evolving document for code standards in this repo. 

* All code must be async by default. 
* Tests should be written for a feature before the feature itself. 
* If a structure/task is used in at least 3 places, turn it into a schema or a generic function
* It should always be possible to develop and test solely in a local environment.
* Setting up a local environment must be done via make commands and compose files. 
* All behavior/functionality should be the same when run locally vs on the cloud
* Use the following package managers. For python, use uv. For JS/TS use pnpm. For Rust, use cargo. 
* Always pin versions. We should always start by using the latest stable release for each dependency. Don't autogenerate this, please check for the latest version before setting or just set the package list first and then pin the versions after initial installation.
* All maintananance and deploys must be done via github actions. For example, if we want to auto update versions, it must be a regularly scheduled github action that checks for latest versions and regression tests. 
* Github repo structure is in three parts. A main branch for the current deployed version. A staging branch where the latest stable features are, and feature branches where all new features/refactors are created and tested. Code moves from feature branches -> dev -> main
* As much as possible, automatic actions should enforce best practices