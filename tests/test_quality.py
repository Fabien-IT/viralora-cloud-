import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class QueueQualityTests(unittest.TestCase):
    def test_current_queue_passes(self):
        subprocess.run([sys.executable,"agents/quality.py","--queue","content/queue.json"],cwd=ROOT,check=True)

    def test_missing_language_fails(self):
        data=json.loads((ROOT/"content/queue.json").read_text(encoding="utf-8"))
        data["videos"]=data["videos"][:1]
        with tempfile.NamedTemporaryFile("w",encoding="utf-8",suffix=".json",delete=False) as f:
            json.dump(data,f); name=f.name
        try:
            result=subprocess.run([sys.executable,"agents/quality.py","--queue",name],cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
        finally:
            Path(name).unlink(missing_ok=True)

if __name__=="__main__": unittest.main()
