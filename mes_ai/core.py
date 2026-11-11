import csv
from datetime import datetime, timedelta
from pathlib import Path

REQUIRED = ('timestamp','open','high','low','close','volume','complete')

def load_candles(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not set(REQUIRED).issubset(reader.fieldnames):
            raise ValueError('Missing required CSV columns: '+', '.join(REQUIRED))
        out=[]
        for line,row in enumerate(reader,2):
            if row['complete'].strip().lower() not in ('true','1','yes'):
                raise ValueError(f'Row {line}: incomplete candle; bridge fails closed')
            t=datetime.fromisoformat(row['timestamp'].replace('Z','+00:00'))
            if t.tzinfo is None or t.utcoffset() is None:
                raise ValueError(f'Row {line}: timezone offset required')
            o,h,l,c,v=(float(row[k]) for k in ('open','high','low','close','volume'))
            if min(o,h,l,c)<=0 or v<0 or h<max(o,c,l) or l>min(o,c,h):
                raise ValueError(f'Row {line}: invalid OHLCV')
            if out and t<=out[-1]['time']:
                raise ValueError(f'Row {line}: duplicate/out-of-order timestamp')
            out.append({'time':t,'open':o,'high':h,'low':l,'close':c,'volume':v})
    if not out: raise ValueError('No completed candles')
    return out

def analyze(candles):
    """Transparent educational EMA-cross research signal; NOT any frozen 41 detector."""
    if len(candles)<30: return {'status':'BLOCKED','reason':'Need at least 30 completed candles','signals':[]}
    ema_fast=ema_slow=candles[0]['close']; previous=None; signals=[]
    for i,bar in enumerate(candles):
        ema_fast=(2/10)*bar['close']+(1-2/10)*ema_fast
        ema_slow=(2/22)*bar['close']+(1-2/22)*ema_slow
        spread=ema_fast-ema_slow
        if i>=30 and previous is not None:
            side='LONG' if previous<=0<spread else 'SHORT' if previous>=0>spread else None
            if side: signals.append({'timestamp':bar['time'].isoformat(),'side':side,'close':bar['close'],'type':'EDUCATIONAL_EMA_CROSS'})
        previous=spread
    return {'status':'RESEARCH_ONLY','bars':len(candles),'last_bar':candles[-1]['time'].isoformat(),'signals':signals,'latest_signal':signals[-1] if signals else None}

def freshness(candles,now,max_age_minutes=5):
    last=candles[-1]['time']
    if now.tzinfo is None: raise ValueError('now must be timezone-aware')
    age=(now-last).total_seconds()/60
    if age<0: return 'BLOCKED_FUTURE_TIMESTAMP'
    if age>max_age_minutes: return 'BLOCKED_STALE_FEED'
    if len(candles)>=2 and (candles[-1]['time']-candles[-2]['time'])!=timedelta(minutes=1):
        return 'BLOCKED_RECENT_GAP'
    return 'FRESH'
