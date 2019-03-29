import pandas as pd
import csv
import json
import logging
from gspread_auth_w_jinja import get_records
from helpers import get_training_week, get_lifts, create_wo_id
from collections import defaultdict # for easy creation of nested dicts
adict = lambda: defaultdict(adict) # usage: newdict = adict()

logging.basicConfig(level=logging.DEBUG, filename='logs/analysis.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

def format_records(records):
    ## MAIN ##
    fname = 'data/TFTNA Log (Responses) - Responses.csv'

    lifts = get_lifts(records)

    workouts_dict = adict()
    # for i,row in df.iterrows():
    for aworkout in records:
        # TODO: How do we want to format this data?
        # format as a new dict under "workouts_dict", 
        ts = aworkout['Timestamp']
        date = ts.split(' ')[0].replace('/','-') # even if no space after date should return date
        wo_type = aworkout.get('Training Type', '') 
        period = aworkout.get('Period', None) # are these going to be strings or what?
        week_pd = aworkout.get('Week in Period', None)
        week_tot = get_training_week(date, start_date = '2-18-2019')
        notes = aworkout.get('Notes')
        grade = aworkout.get('Grade')
        duration = aworkout.get('Duration (min)')
        if aworkout.get('Abs?') == 'Y':
            abs=1
        else:
            abs=0

        name = '{}-{}-{}-{}'.format(date, wo_type.lower(), period.lower(), week_pd)  # date-workout-period-week
        aworkout_dict = dict(zip(['Name','Type', wo_type, 'Week', 'Period','Week in Period', 'Notes', 'Grade', 'Duration', 'Abs'],[name, wo_type, adict(), week_tot, period, week_pd, notes, grade, duration, abs]))

        if wo_type == 'Strength':
            aworkout_dict[wo_type]['Circuits'] = aworkout.get('# Circuits')
            aworkout_dict[wo_type]['Lifts'] = adict()
            for lift, def_reps in lifts: # sub dict {lift: {reps:x, weight:y, progression:z}}

                reps = aworkout.get(lift + " (Reps) [{}]".format(def_reps), 0)  
                wgt = aworkout.get(lift + " (Weight)", 0)
                prog = aworkout.get(lift + " (Progression)", "")
                diff = aworkout.get(lift + " (Difficulty)", "")

                # if one of reps, weight, and prog is not empty str or null, then put the workout in the newly formatted dict:
                # TODO: cannot access multi layer dict KeyError
                if (reps != '') or (wgt != '') or (prog != '') or (diff != ''):
                    aworkout_dict[wo_type]['Lifts'][lift] = adict()
                    aworkout_dict[wo_type]['Lifts'][lift]['Reps']=reps
                    aworkout_dict[wo_type]['Lifts'][lift]['Desired Reps']=def_reps
                    aworkout_dict[wo_type]['Lifts'][lift]['Weight']=wgt
                    aworkout_dict[wo_type]['Lifts'][lift]['Progression']=prog
                    aworkout_dict[wo_type]['Lifts'][lift]['Difficulty']=diff

        if wo_type == 'Aerobic':
            aworkout_dict[wo_type]['Distance'] = aworkout.get('Distance (miles)', '')
            aworkout_dict[wo_type]['Speed'] = aworkout.get('Speed (treadmill)', '')
            aworkout_dict[wo_type]['Pace'] = aworkout.get('Pace (min/mile)', '')
            aworkout_dict[wo_type]['HRZ'] = aworkout.get('HRZ', '')
            aworkout_dict[wo_type]['HR Avg'] = aworkout.get('HR Avg (bpm)', '')

        if wo_type == 'Climbing':
            aworkout_dict[wo_type]['Location'] = aworkout.get('Indoor or Outdoor', None)
            aworkout_dict[wo_type]['Type'] = aworkout.get('Climbing Type', None)
            aworkout_dict[wo_type]['Pitches'] = aworkout.get('# Pitches Total', None)
            aworkout_dict[wo_type]['Pitches 2 Grades Below RP'] = aworkout.get('# Pitches @ 2 grades below RP', None)
            aworkout_dict[wo_type]['Difficulty'] = aworkout.get('Climbing Grades (CSV)', None)

        # if wo_type == 'Aerobic', etc
        logger.debug('week: {}'.format(week_tot))
        id = create_wo_id(workouts_dict, week_tot)
        workouts_dict[id] = aworkout_dict
        logger.debug(aworkout_dict)
    
    logger.debug(workouts_dict)
        
    return workouts_dict


if __name__=="__main__":
    records = get_records()
    newly_formatted = format_records(records)

    with open ( 'newly_formatted.json', 'w') as f:
        json.dump(newly_formatted, f, sort_keys=True)