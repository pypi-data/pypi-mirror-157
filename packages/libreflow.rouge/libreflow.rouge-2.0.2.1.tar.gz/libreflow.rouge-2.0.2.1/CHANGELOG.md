# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)[^1].

<!---
Types of changes

- Added for new features.
- Changed for changes in existing functionality.
- Deprecated for soon-to-be removed features.
- Removed for now removed features.
- Fixed for any bug fixes.
- Security in case of vulnerabilities.

-->

## [Unreleased]

## [2.0.2] - 2022-06-30

### Added

* New runners to edit PaLaS and Houdoo scenes, and their associated file extensions in the list of supported extensions in the default applications.

### Removed

* The sequence level: shots are now lying right under a film.

## [2.0.1] - 2022-06-08

### Changed

* The existing types defining the main entities of the project (films, sequences, shots, tracked files and folders, revisions) have been redefined to integrate the last features provided in libreflow 2.1.0.
* Tracked files and folders are created by default with the path format specified in the contextual dictionary (in the `settings` context) of the project.

### Added

* Each shot now holds a list of tasks, which can be parameterised in the task manager available in the project settings.

## [2.0.0] - 2022-03-15

Setting up a basic project.