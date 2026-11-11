"""Read-only bridge: consumes Quantower-exported completed-minute CSV; never places orders."""
import argparse,json,time
from datetime import datetime,timezone
from pathlib import Path
from .core import load_candles,analyze,freshness

def snapshot(csv_path):
    bars=load_candles(csv_path)
    status=freshness(bars,datetime.now(timezone.utc))
    result=analyze(bars)
    if status!='FRESH':
        return {'feed_status':status,'research_status':'BLOCKED','signals':[], 'last_bar':bars[-1]['time'].isoformat()}
    return {'feed_status':status,**result}

def main():
    p=argparse.ArgumentParser(description='Read-only Quantower completed-minute CSV bridge')
    p.add_argument('--csv',required=True);p.add_argument('--output',default='bridge_status.json');p.add_argument('--watch',action='store_true');p.add_argument('--interval',type=float,default=5)
    args=p.parse_args()
    if args.interval<1:p.error('--interval must be >=1')
    while True:
        try: result=snapshot(args.csv)
        except (OSError,ValueError) as e: result={'feed_status':'BLOCKED_INVALID_INPUT','research_status':'BLOCKED','signals':[],'error':str(e)}
        dest=Path(args.output);tmp=dest.with_suffix(dest.suffix+'.tmp')
        tmp.write_text(json.dumps(result,indent=2),encoding='utf-8');tmp.replace(dest)
        print(json.dumps(result),flush=True)
        if not args.watch:break
        time.sleep(args.interval)
if __name__=='__main__':main()
