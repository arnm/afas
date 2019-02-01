
# AFAS

AFAS, "Anoying Friends About Sports", is a bot which automatically
notifies your friends, or enemies, when a rival team scores.

## Setup

1. Install Python:
```sh
brew install python
```

2. Install pipenv:
```sh
brew install pipenv
```

3. Install ffmpeg (InstagramAPI dependecy):
```sh
brew install ffmpeg
```

3. In project root, install dependencies:
```
pipenv install
```

## Usage

1. Create and update `config.json`:
```sh
mv config.example.json config.json
```

2. Run
```sh
pipenv run python afas.py --help
```