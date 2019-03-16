import datetime as dt
import sys
import re
import logging

logging.basicConfig(level=logging.DEBUG, filename='logs/helpers.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

def get_training_week(compare_date, start_date='2-18-2019'):
    """ 
    : compare_date: string e.g. '3-10-1992' 
    : start_date : string e.g. '3-10-1992' 
    : returns : an int signifying week number from start date indexed from 1
    """
    # iso week starts on Monday, the first week of an ISO year is the first Gregorian calendar week containing a thursday
    # week number starts from one, e.g. first day of ISO year 2019 was 12/31/18 since this is the monday, and tuesday is 1/1/19

    # convert start_date (str) to dt.date
    try: 
        dt_start = dt.datetime.strptime(start_date, "%m-%d-%Y") # format as 3/19/2019
        dt_compare = dt.datetime.strptime(compare_date, "%m-%d-%Y") # format as 3/19/2019

    except (ValueError):
        sys.exit('Date Formatting Error input to get_week_in_plan(), should be as mm-dd-yyyy')

    if dt_compare < dt_start:
        sys.exit('Start Date must be before Date to compare. (start_date={}, compare_date={})'.format(start_date, compare_date))

    start_week_num = dt_start.isocalendar()[1] # isocalendar as (year, week, day in week)
    compare_week_num = dt_compare.isocalendar()[1]

    week_num = compare_week_num - start_week_num + 1
    return week_num


def get_lifts(records):
    """ From a flattened list of dict workouts finds and returns the workouts matching a pre defined pattern 
    :records: a list of dictionaries with the keys including some of the workout names
    :returns: a list of workouts from a predefined regex 
    """

    logger.info('Finding Lifts...')
    pattern=re.compile('Turkish*|Split*|Push*|Box*|Pull*|Squat*|Hanging*|Dips*|Wall*|Isometric*|Horizontal*|Deadlift*')

    lift_fields = []
    other_fields = []
    #for col in df.columns:
    for col in records[0].keys(): # TODO: C/RUN here
        if pattern.search(col):
            lift_fields.append(col) # more efficient to parse workout vs reps/wgt here
        else:
            other_fields.append(col)

    # split on parens
    lifts = []
    for i in lift_fields:
        lifts.append(i.split('(')[0].strip())
        # reps.append(i.split('[')[-1].strip())

    lifts = list(set(lifts))
    logger.info('<lifts> = ' + str(lifts))
    return lifts


def to_keyname(_list):
    # usage: lift_keys = to_keyname(lifts)
    newlist = []
    for i in _list:
        newlist.append(str.lower(i).replace(' ', '_'))

    return newlist


def create_wo_id(workouts_dict, X):
    """
    : workouts_dict : dict where the keys are in the form X.Y, where X and Y are both single digit integers
    : X : the integer preceding the dot, signifying e.g. the week 
    """  
    if len(workouts_dict) == 0:
        return '1.1'

    wo_id = ''
    for k in sorted(workouts_dict.keys(), reverse=True): # i.e. 2.2, 2.1, 1.2, 1.1
        logger.debug(k)
        if X > float(k):
            wo_id = '{}.1'.format(X)
            return wo_id

        match = re.search(r'({}).(\d)'.format(X), k)
        if match:
            ndotm = match.groups()
            logger.debug(match)
            logger.debug(ndotm)
            n = ndotm[0]
            m = ndotm[1]
            assert n == str(X), 'Error in Creating Workout Identifier'
            wo_id = '{}.{}'.format(n, int()+1)
            return wo_id
            
    sys.stderr.write('Could not create workout ID, 0.0 being used:')
    return '0.0'


if __name__=="__main__":


    d = {'1.1':{}, '1.2':{}, '1.3':{}, '1.10':{}, '2.1':{}, '2.2':{}, '2.3':{}, '3.1':{}}
    print('testing with week=1')
    print(create_wo_id(d, 1))
    print('testing with week=2')
    print(create_wo_id(d, 2))
    print('testing with week=3')
    print(create_wo_id(d, 3))
    print('testing with week=4')
    print(create_wo_id(d, 4))
    d = {}
    print('testing with week=1')
    print(create_wo_id(d, 1))
    d = {'hello':'a'}
    print('testing with week=1')
    print(create_wo_id(d, 1))