#!/usr/bin/env python3

import importlib
import random
import time
from collections import defaultdict
from pymongo import UpdateOne

from farm.config import config
from farm.models import Flag, Flag_Status, SubmitResult
from farm.database import db
from fastapi_utilities import repeat_every

def get_fair_share(groups, limit):
    if not groups:
        return []

    groups = sorted(groups, key=len)
    places_left = limit
    group_count = len(groups)
    fair_share = places_left // group_count

    result = []
    residuals = []
    for group in groups:
        if len(group) <= fair_share:
            result += group

            places_left -= len(group)
            group_count -= 1
            if group_count > 0:
                fair_share = places_left // group_count
            # The fair share could have increased because the processed group
            # had a few elements. Sorting order guarantees that the smaller
            # groups will be processed first.
        else:
            selected = random.sample(group, fair_share + 1)
            result += selected[:-1]
            residuals.append(selected[-1])
    result += random.sample(residuals, min(limit - len(result), len(residuals)))

    random.shuffle(result)
    return result


def submit_flags(flags):
    module = importlib.import_module('server.protocols.' + config.SYSTEM_PROTOCOL)

    try:
        return list(module.submit_flags(flags, config))
    except Exception as e:
        raise e
        message = '{}: {}'.format(type(e).__name__, str(e))
        print('Exception on submitting flags')
        return [SubmitResult(item.flag, Flag_Status.QUEUED, message) for item in flags]

@repeat_every(seconds=config.SUBMIT_PERIOD)
def submit():
    print('trying to submit flags...')
    submit_start_time = time.time()

    # Calculate skip_time
    skip_time = round(submit_start_time - config.FLAG_LIFETIME)
    
    # Update flags where status is 'QUEUED' and time is less than skip_time
    db['flags'].update_many(
        {"status": Flag_Status.QUEUED.name, "time": {"$lt": skip_time}},
        {"$set": {"status": Flag_Status.SKIPPED.name}}
    )
    # Query all flags where status is 'QUEUED'
    queued_flags = list(db['flags'].find({"status": Flag_Status.QUEUED.name}, {'_id': False}))
    # Convert MongoDB documents to Flag objects (assuming a Flag class exists)
    queued_flags = [Flag(**item) for item in queued_flags]
    if queued_flags:
        # Group flags by (sploit, team) using defaultdict
        grouped_flags = defaultdict(list)
        for item in queued_flags:
            grouped_flags[(item.sploit, item.team)].append(item)
        # Get fair share of flags, respecting the limit defined in config
        flags = get_fair_share(grouped_flags.values(), config.SUBMIT_FLAG_LIMIT)
        print('Submitting %s flags (out of %s in queue)', len(flags), len(queued_flags))
        # Submit flags and get results
        results = submit_flags(flags)
        # Prepare bulk update for MongoDB
        bulk_updates = []
        for result in results:
            bulk_updates.append(
                UpdateOne(
                    filter={"flag": result.flag},
                    update= {
                        "$set": {
                            "status": result.status.name,
                            "checksystem_response": result.checksystem_response
                        }
                    }
                )
            )
        # Execute bulk update in MongoDB
        if bulk_updates:
            db['flags'].bulk_write(bulk_updates)

def run_loop():
    print('Starting submit loop')
    
    while True:
        submit_start_time = time.time()

        # Calculate skip_time
        skip_time = round(submit_start_time - config.FLAG_LIFETIME)

        # Calculate the time spent and sleep if necessary
        submit_spent = time.time() - submit_start_time
        if config.SUBMIT_PERIOD > submit_spent:
            time.sleep(config.SUBMIT_PERIOD - submit_spent)

if __name__ == "__main__":
    run_loop()