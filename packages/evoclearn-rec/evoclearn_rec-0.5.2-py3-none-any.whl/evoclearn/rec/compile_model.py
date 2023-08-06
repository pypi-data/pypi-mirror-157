#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bz2
import json

import click
import dill
from tensorflow.keras.models import load_model
from evoclearn.core import log

from . import Ac2Vec


@click.command()
@click.option("--max_feat_len", default=121, show_default=True, type=int)
@click.option("--batchsize", default=32, show_default=True, type=int)
@click.option("--unittype", default="CV", show_default=True, type=str)
@click.option("--segdims", type=str, help="comma-separated ints")
@click.option("--outlabs", type=str, help="comma-separated strings")
@click.option("--samplerate", default=16000, show_default=True, type=int)
@click.argument("featsettingsfile", type=click.File("r"))
@click.argument("featnormfuncfile", type=click.File("rb"))
@click.argument("vec2symfuncfile", type=click.File("rb"))
@click.argument("modelfile", type=click.Path(exists=True))
@click.argument("outputfile", type=click.Path())
def main(max_feat_len,
         batchsize,
         unittype,
         segdims,
         outlabs,
         samplerate,
         featsettingsfile,
         featnormfuncfile,
         vec2symfuncfile,
         modelfile,
         outputfile):
    logger = log.getLogger("evl.rec.compile")

    featsettings = json.load(featsettingsfile)
    model = load_model(modelfile)
    featnormfunc = dill.load(featnormfuncfile)
    vec2symfunc = dill.load(vec2symfuncfile)
    segdims = list(map(int, segdims.split(","))) if segdims is not None else segdims
    outlabs = outlabs.split(",") if outlabs is not None else outlabs
    ac2vec = Ac2Vec(max_feat_len,
                    batchsize,
                    featsettings,
                    featnormfunc,
                    vec2symfunc.keywords["veclabels"],
                    vec2symfunc,
                    model,
                    unittype,
                    segdims,
                    outlabs,
                    samplerate)
    ac2vec.to_file(outputfile)


if __name__ == "__main__":
    main()
