# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.3] - 2025-05-28

### Added
- Support for NumPy 2.0 compatibility

### Fixed
- Fixed path check functionality (#84) - Thanks to @hykilpikonna
- Updated package requirements to support NumPy 2.0 (#85)

### Contributors
- @hykilpikonna - Fixed path check functionality

## [0.4.2] - 2023-11-24

### Fixed
- Fixed sample rate conversion support - `mus = musdb.DB(download=True, subsets="test", sample_rate=16000)` now correctly resamples audio on-the-fly 