# Crackme Template

Provided a github access token and a crackme-id (`https://crackmes.one/crackme/{crackme_id}`) as input, a github repository will be setup that intialises the template which includes the binary from the crackme.

## Usage

```sh
pip install crackme-template
crackme_template --crackme-id 5ec1a37533c5d449d91ae535 --github-access-token YOUR_TOKEN
```

Example of initialised repo: <https://github.com/nymann/crackme-baby-ransom/>

Note if `--github-access-token` is omitted the program will try to read it from the `GITHUB_ACCESS_TOKEN` environment variable.

## Development

For help getting started developing check [DEVELOPMENT.md](DEVELOPMENT.md)
