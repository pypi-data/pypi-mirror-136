# jomiel

[![pypi-pyversions](https://img.shields.io/pypi/pyversions/jomiel?color=%230a66dc)][pypi]
[![pypi-v](https://img.shields.io/pypi/v/jomiel?color=%230a66dc)][pypi]
[![pypi-wheel](https://img.shields.io/pypi/wheel/jomiel?color=%230a66dc)][pypi]
[![pypi-status](https://img.shields.io/pypi/status/jomiel?color=%230a66dc)][pypi]
[![code-style](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi]: https://pypi.org/project/jomiel
[black]: https://pypi.org/project/black

`jomiel` is the meta inquiry middleware for distributed systems. It
returns data about content on [video-sharing] websites (e.g. YouTube).
Two technologies form the basis for `jomiel`:

- [ZeroMQ] (also known as ØMQ, 0MQ, or zmq) looks like an embeddable
  networking library but acts like a concurrency framework

- [Protocol Buffers] is a language-neutral, platform-neutral,
  extensible mechanism for serializing structured data

`jomiel` is a spiritual successor to (now defunct) [libquvi].

[libquvi]: https://github.com/guendto/libquvi

![Example: jomiel and yomiel working together](./docs/demo.svg)

## Features

- **Language and platform neutral**. It communicates using [Protocol
  Buffers] and [ZeroMQ]. There are plenty of [client demos]. Pick your
  favorite language.

- **Secure**. It can authenticate and encrypt connections using [CURVE]
  and [SSH].

- **Extensible**. It has a plugin architecture.

[protocol buffers]: https://developers.google.com/protocol-buffers/
[ssh]: https://en.wikipedia.org/wiki/Ssh
[zeromq]: https://zeromq.org/
[curve]: http://curvezmq.org/

## Getting started

[![pypi-pyversions](https://img.shields.io/pypi/pyversions/jomiel?color=%230a66dc)][pypi]

Install from [PyPI]:

[pypi]: https://pypi.org/

```shell
pip install jomiel
```

Install from the repository, e.g. for development:

```shell
git clone https://github.com/guendto/jomiel.git
cd jomiel
pip install -e .  # Install a project in editable mode
```

Or, if you'd rather not install in "editable mode":

```shell
pip install git+https://github.com/guendto/jomiel
```

Try sending inquiries to `jomiel` with:

- the [client demos] written in different modern programming languages
- [yomiel] - the pretty printer for `jomiel` messages

Be sure to check out:

- [changes](./CHANGES.md)
- [howto](./docs/HOWTO.md#howto-jomiel)

[client demos]: https://github.com/guendto/jomiel-client-demos/
[yomiel]: https://github.com/guendto/jomiel-yomiel/

## Usage

```text
usage: jomiel [-h] [--version] [-v] [--config-file FILE] [-D] [-E] [-P]
              [--logger-config FILE] [-L] [--logger-idents-verbose] [-l IDENT]
              [-p] [-m] [--debug-sensitive] [-F] [--http-user-agent STRING]
              [--http-timeout TIME] [--http-debug] [-I] [-r ADDR] [-d ADDR]
              [-w [1-64]] [--curve-enable] [--curve-public-key-dir DIR]
              [--curve-server-key-file FILE] [--curve-domain DOMAIN]
              [--curve-allow ADDR]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v, --version-long    show version information about program's environment
                        and exit (default: False)
  --config-file FILE    Read configuration from the specified file [env var:
                        CONFIG_FILE] (default: None)
  -D, --print-config    Show the configuration values and exit (default:
                        False)
  -E, --report-config   Report keys, values and where they were set (default:
                        False)
  -P, --config-paths    Print default configuration file paths (default:
                        False)
  -p, --plugin-list     Display the found plugins and exit (default: False)

logger:
  --logger-config FILE  Logger configuration file to read [env var:
                        LOGGER_CONFIG] (default: None)
  -L, --logger-idents   Print logger identities and exit (default: False)
  --logger-idents-verbose
                        Print logger identities in detail, use together with
                        --logger-idents (default: False)
  -l IDENT, --logger-ident IDENT
                        Use the logger identity [env var: LOGGER_IDENT]
                        (default: default)

debug:
  -m, --debug-minify-json
                        Minify JSON messages in the logger (default: False)
  --debug-sensitive     Log sensitive data, e.g. input URIs, serialized
                        messages (default: False)

http:
  -F, --http-allow-redirects
                        Follow HTTP redirections (default: False)
  --http-user-agent STRING
                        Identify as STRING to the HTTP server (default:
                        Mozilla/5.0)
  --http-timeout TIME   Time in seconds allowed for the connection to the HTTP
                        server to take (default: 5)
  --http-debug          Enable verbose HTTP output (default: False)

broker:
  -I, --broker-input-allow-any
                        Disable input URI validation (default: False)
  -r ADDR, --broker-router-endpoint ADDR
                        Bind the frontend (router) socket to the local
                        endpoint [env var: BROKER_ROUTER_ENDPOINT] (default:
                        tcp://*:5514)
  -d ADDR, --broker-dealer-endpoint ADDR
                        Bind the backend (dealer) socket to the local endpoint
                        [env var: BROKER_DEALER_ENDPOINT] (default:
                        inproc://workers)
  -w [1-64], --broker-worker-threads [1-64]
                        Number of worker threads in the pool waiting for
                        client connections (default: 5)

curve:
  --curve-enable        Enable CURVE support (default: False)
  --curve-public-key-dir DIR
                        Directory that holds all public client key files
                        (default: .curve/)
  --curve-server-key-file FILE
                        Secret CURVE key file for the server (default:
                        .curve/server.key_secret)
  --curve-domain DOMAIN
                        Configure CURVE authentication for a given domain
                        (default: *)
  --curve-allow ADDR    Allow (whitelist IP addresses) (default: 127.0.0.1)

 If an arg is specified in more than one place, then commandline values
override environment variables which override defaults.
```

## Website coverage

```shell
jomiel --plugin-list  # The current coverage is very limited
```

See the `src/jomiel/plugin/` directory for the existing plugins. The
plugin architecture is extensible. When you are contributing new
plugins, make sure that the website is **not**:

- dedicated to copyright infringement (whether they host the media or
  only link to it)

- [NSFW]

[video-sharing]: https://en.wikipedia.org/wiki/Video_hosting_service
[python]: https://www.python.org/about/gettingstarted/
[nsfw]: https://en.wikipedia.org/wiki/NSFW

## License

`jomiel` is licensed under the [Apache License version 2.0][aplv2].

[aplv2]: https://www.tldrlegal.com/l/apache2

## Acknowledgements

- [pre-commit] is used for linting and reformatting, see the
  [.pre-commit-config.yaml] file

[.pre-commit-config.yaml]: https://github.com/guendto/jomiel/blob/master/.pre-commit-config.yaml
[pre-commit]: https://pre-commit.com/
