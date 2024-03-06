#!/bin/bash

rm .env
mv .env.test .env
pytest -v ./tests
