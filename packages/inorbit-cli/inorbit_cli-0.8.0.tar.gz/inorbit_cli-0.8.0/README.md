# InOrbit CLI

Welcome to the InOrbit Command Line Interface.

## Installing

[https://pypi.org/project/inorbit-cli/](https://pypi.org/project/inorbit-cli/)

Make sure you deactivated the development virtual environment or you are using a different one with no `inorbit` python package installed.

```bash
pip install inorbit-cli
```

## Usage

The CLI requires an API key for authenticating against InOrbit's platform. For obtaining it, please go to the [InOrbit developer console](https://console.inorbit.ai/).

```bash
$ export INORBIT_CLI_API_KEY="company_api_key" 
$ inorbit --help
Usage: inorbit [OPTIONS] COMMAND [ARGS]...

  InOrbit Command Line Interface tool

  The InOrbit CLI tool enable roboteers to interact with the InOrbit Cloud
  platform in order to manage robot configuration as code.

Options:
  --help  Show this message and exit.

Commands:
  describe
  get
```

## Contributing

## Publishing

To publish the InOrbit CLI package to the testing package index you'll need a token from [test.pypi.org](https://test.pypi.org). Otherwise you'll need a token from [https://pypi.org](https://pypi.org) (The official python packages index)
To get the token, register a new account and ask for an invite to the project.  
Once you accept the invite, go to your profile and generate a new token for the "InOrbit CLI".  
After that, to publish the package, first set the environment variable 'TWINE_PASSWORD' doing:  

```bash
export TWINE_PASSWORD="your-token-from-pypi.org"
./publish.sh -p
```

NOTE: passing -p to the script means "production", the package will be published in the official package index, if you want to publish it in the test package index just run:

```bash
export TWINE_PASSWORD="your-token-from-test.pypi.org"
./publish.sh -t
```  

See [CONTRIBUTING.md](./CONTRIBUTING.md)
