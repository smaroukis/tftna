import pandas as pd
import csv
import re
import logging

logging.basicConfig(level=logging.DEBUG, filename='analysis.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

# TODO: Force int or str in weights / reps / progression 

def get_lifts(df):

    logger.info('Finding Lifts...')
    pattern=re.compile('Turkish*|Split*|Push*|Box*|Pull*|Squat*|Hanging*|Dips*|Wall*|Isometric*|Horizontal*|Deadlift*')

    lift_fields = []
    other_fields = []
    for col in df.columns:
        if pattern.search(col):
            lift_fields.append(col) # more efficient to parse workout vs reps/wgt here
        else:
            other_fields.append(col)

    # split on parens
    lifts = []
    for i in lift_fields:
        lifts.append(i.split('(')[0].strip())

    lifts = list(set(lifts))
    logger.info('<lifts> = ' + str(lifts))
    return lifts


def to_keyname(_list):
    # usage: lift_keys = to_keyname(lifts)
    newlist = []
    for i in _list:
        newlist.append(str.lower(i).replace(' ', '_'))

    return newlist

def m():
    ## MAIN ##
    fname = 'strength_sandbox.csv'

    df = pd.read_csv(fname)
    df = df[df['Training Type'] == 'Strength']
    logger.debug(df)
    lifts = get_lifts(df)

    alistparent = []
    for i,row in df.iterrows():
        ts = row['Timestamp']
        logger.debug('looking at row for workout on %s', ts)

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
                reps = df[df['Timestamp'] == ts][str_reps].values
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
    df.to_csv('df_liftimize.csv')
