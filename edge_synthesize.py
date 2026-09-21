import sys
import argparse
import asyncio
import edge_tts
import time

async def run_synthesis(text: str, voice: str, out_path: str, rate: str = None, pitch: str = None):
    kwargs = {}
    if rate and rate != "+0%":
        kwargs["rate"] = rate
    if pitch and pitch != "+0Hz":
        kwargs["pitch"] = pitch

    retries = 3
    for attempt in range(retries):
        try:
            communicate = edge_tts.Communicate(text, voice, **kwargs)
            await communicate.save(out_path)
            return True
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
            else:
                raise e

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--voice", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--rate", default=None)
    parser.add_argument("--pitch", default=None)
    args = parser.parse_args()

    asyncio.run(run_synthesis(args.text, args.voice, args.out, rate=args.rate, pitch=args.pitch))

if __name__ == "__main__":
    main()
