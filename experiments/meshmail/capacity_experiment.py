"""Demonstrate the difference between logical quotas and physical bytes using zlib.

No disks are modified. Uses a one-megabyte in-memory sample for safe benchmarking.
"""
import os
import zlib


def main():
    samples = {'repetitive text': b'A' * 1_048_576,
               'random bytes': os.urandom(1_048_576)}
    print('SLICKK storage efficiency experiment (1 MiB samples)')
    for name, raw in samples.items():
        packed = zlib.compress(raw, level=9)
        assert zlib.decompress(packed) == raw
        print(f'{name}: original={len(raw):,} bytes, compressed={len(packed):,} bytes, '
              f'saved={100*(1-len(packed)/len(raw)):.2f}%, verified lossless')
    print('Conclusion: quotas and encodings are changeable software rules; actual '
          'capacity and compressibility depend on physical media and the data.')


if __name__ == '__main__':main()
