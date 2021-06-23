# BINANCE_TRACKER

## Introduction

The BINANCE_TRACKER is a program that operates on the Google Cloud Platform and pull historical market data from the Binance API. The first launching of the algorithm will download all historical data for each specified pair. Then it will activates once everyday and will pull the missing market data of the day. That is why the first activation of the algorithm can be particularly long but most of the other working phase will are pretty short.

## Local install

Install all dependencies
``` sh
poetry install
```

## Usage

To run the algorithm on your computer, run
``` sh
make run-local
```

To run it and write the files in a bucket, run
``` sh
make run-bucket
```

## Deploy

First, add your GCP project ID, service account and bucket in Makefile.
``` Makefile
GCP_PROJECT_ID="<YOUR_PROJECT_ID>"
GCP_SERVICE_ACCOUNT="<YOUR_SERVICE_ACCOUNT>"
GCP_BUCKET="<YOUR_BUCKET>"
GCP_REGION="<LOCATION>"
SCHEDULE="0 */1 * * *"
```
Make sure the *SCHEDULE* parameter respects the cron syntax and that it corresponds to the *TIMEFRAME* set in the config.py file.

Then run
``` sh
make deploy
```
