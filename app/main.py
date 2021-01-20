#! /usr/bin/env python

import os

from fastapi import FastAPI
from find_neighborhood import db

app = FastAPI()


@app.get("/sf")
async def find(address: str = ""):
    return db.find(address)
