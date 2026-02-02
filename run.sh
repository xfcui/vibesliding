#!/bin/bash

rm -rf output/*
python3 -m src.cli --outline examples/outline.md --style examples/style.png --copy 4 --article examples/article.md $@

