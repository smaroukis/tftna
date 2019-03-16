import pandas as pd
import csv
import logging
from gspread_auth_w_jinja import get_records
from helpers import get_training_week, get_lifts

logging.basicConfig(level=logging.DEBUG, filename='logs/analysis.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

# TODO: How to use logging in multiple files, do I need to pass it?
# TODO: Wihtout pandas

def m():
    ## MAIN ##
    fname = 'data/TFTNA Log (Responses) - Responses.csv'

    # df = pd.read_csv(fname)
    # df = df[df['Training Type'] == 'Strength']
    # logger.debug(df)
    # lifts = get_lifts(df)
    records = get_records()
    lifts = get_lifts(records)

    alistparent = []
    workouts_dict = {}
    # for i,row in df.iterrows():
    for aworkout in records:
        # TODO: How do we want to format this data?
        # format as a new dict under "workouts_dict", 
        ts = aworkout['Timestamp']
        date = ts.split(' ')[0].replace('/','-') # even if no space after date should return date
        wo_type = aworkout.get('Training Type') # error if nothing
        period = aworkout.get('Period')
        week_pd = aworkout.get('Week in Period')
        week_tot = get_training_week(date)

        name = '{}-{}-{}-{}'.format(date, wo_type.lower(), period.lower(), week_pd)  # date-workout-period-week
        aworkout_dict = dict(zip(['name','type', 'week', 'period','week_pd'],[name, wo_type, week_tot, period, week_pd]))

        nf_reps = []
        nf_wgt = []
        nf_prog = []
        for lift in lifts: # adds a new row with the timestamp, lift, and reps
            adictchild = dict()
            adictchild['Timestamp']=ts
            adictchild['Lift']=lift

            str_reps = lift + " (Reps)"
            str_wgt = lift + " (Weight)"
            str_prog = lift + " (Progression)"
            try: 
                # reps = df[df['Timestamp'] == ts][str_reps].values

                adictchild['Reps']=reps
            except (KeyError):
                nf_reps.append(str_reps)
            try: 
                wgt = df[df['Timestamp'] == ts][str_wgt].values
                adictchild['Weight (lbs)']=wgt
            except (KeyError):
                nf_wgt.append(str_wgt)
            try: 
                prog = df[df['Timestamp'] == ts][str_prog].values
                adictchild['Progression']=prog
            except (KeyError):
                nf_prog.append(str_prog)

            logger.debug('variable <adictchild> = ' + str(adictchild))
            alistparent.append(adictchild)
        
        # TODO: Dynamically make a unique key for each workout with <weeknum>.<workoutnum>
        workouts_dict.update('4.1': <dict> )


    logger.warning('Unfound Columns for (Reps): \n' + str(nf_reps))
    logger.warning('Unfound Columns for (Weight): \n' + str(nf_wgt))
    logger.warning('Unfound Columns for (Progression): \n' + str(nf_prog))

    df_liftimize = pd.DataFrame(alistparent)
    logger.debug('Printing <df_liftimize>')
    logger.debug(df_liftimize)

    iterables = [list(reversed(df_liftimize.Timestamp.unique())), df_liftimize.Lift.unique()] # reverse "Timestamp" indices to get most recent date at top
    ix = pd.MultiIndex.from_product(iterables)
    df_liftimize.set_index(ix, inplace=True)

    return df_liftimize


if __name__=="__main__":
    df = m()
    df.to_csv('data/df_liftimize.csv')
