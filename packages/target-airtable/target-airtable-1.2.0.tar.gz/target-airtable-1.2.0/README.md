# target-airtable

![Release-Publish](https://github.com/ednarb29/target-airtable/actions/workflows/automatic-releases.yml/badge.svg)

This is a [Singer](https://singer.io) target that reads JSON-formatted data from stdin
following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md) and
persists it to [Airtable](https://airtable.com/).

## Install

Implemented and tested with Python 3.9.0. It is recommented to install this target into a
separate virtual environment to avoid dependency conflicts. Clone the repository and install
it from source:

```bash
› pip install target-airtable
```

## Use

target-airtable takes two types of input:

1. A config file containing
   - **api_token** (from your Airtable account)
   - **base** (the Airtable base id)
   - **max_batch_size** (according to your Airtable API rate limits)
   - **endpoint** (optional, default="https://api.airtable.com/v0", the Airtable API endpoint)
   - **typecast** (optional, default=True, tries to cast types according to your Airtable table schema)
2. A stream of Singer-formatted data on stdin

target-airtable replicates the incomming streams from a tap into Airtable tables with the same name as the
stream. Make sure that these tables and the fields exist in your selected Airtable base.


Create a config file with your configuration data:

```json
{
  "api_token": "my_token",
  "base": "my_base",
  "max_batch_size": 10,
  "endpoint": "https://api.airtable.com/v0",
  "typecast": true
}
```
```bash
› tap-some-api | target-airtable --config config.json
```

where `tap-some-api` is a [Singer Tap](https://singer.io).

# Want to help?
Fork, improve and PR.
