import tempfile,unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
from mes_ai.core import load_candles,analyze,freshness
class CoreTests(unittest.TestCase):
    def test_sample(self):
        b=load_candles('sample_data/synthetic_mes_1m.csv');self.assertGreaterEqual(len(b),30);self.assertEqual(analyze(b)['status'],'RESEARCH_ONLY')
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv';p.write_text('timestamp,open,high,low,close,volume,complete\n2026-01-01T12:00:00+00:00,10,11,9,10,1,true\n2026-01-01T12:00:00+00:00,10,11,9,10,1,true\n');
            with self.assertRaises(ValueError):load_candles(p)
    def test_incomplete_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv';p.write_text('timestamp,open,high,low,close,volume,complete\n2026-01-01T12:00:00+00:00,10,11,9,10,1,false\n')
            with self.assertRaises(ValueError):load_candles(p)
    def test_stale(self):
        b=load_candles('sample_data/synthetic_mes_1m.csv');self.assertEqual(freshness(b,datetime.now(timezone.utc)),'BLOCKED_STALE_FEED')
if __name__=='__main__':unittest.main()
