import argparse, sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal

ap = argparse.ArgumentParser()
ap.add_argument("--order", type=int, default=2)
ap.add_argument("--cutoff", type=float, default=0.5)
ap.add_argument("--algorithm", choices=["ma", "firwin"], default="firwin")
ap.add_argument("--cascade", type=int, default=1)
ap.add_argument("--plot", action="store_true")
ap.add_argument("--downsample", action="store_true")
ap.add_argument("--upsample", action="store_true")
ap.add_argument("wav", nargs="?")
args = ap.parse_args()

if args.downsample or args.upsample:
    assert args.algorithm == "firwin"
    args.order = 256

if args.algorithm == "ma":
    order = args.order
    a = [1.0/order] * order
elif args.algorithm == "firwin":
    a = signal.firwin(args.order, cutoff=args.cutoff)
else:
    assert False, "unknown algorithm"

if args.plot:
    # "Apply" the filter.
    ax = a
    for _ in range(args.cascade - 1):
        a = np.convolve(ax, a)

    # Plot magnitude response
    w, mag = signal.freqz(a)
    plt.plot(w/np.pi, 20 * np.log10(np.abs(mag)))
    plt.show(block=True)

    exit(0)

# Read the file into x yielding frame rate fr (samples/sec).
(fr, x) = wav.read(args.wav)
# Check for format, for simplicity.
assert x.dtype == np.int16, "requires 16-bit signed samples"
# Convert to float samples, single channel, scaled to -1..1.
if x.ndim > 1:
    x = np.mean(x.astype(np.float32), axis=1) / 32768.0
else:
    x = x.astype(np.float32) / 32768.0

if args.upsample:
    y = np.zeros(len(x) * 2, dtype=np.float32)
    y[::2] = x
    x = y
    fr *= 2

# Do the convolution with numpy. Much faster.
for _ in range(args.cascade):
    y = np.convolve(x, a)
    x = y

if args.downsample:
    y = y[::2]
    fr //= 2

# Convert the output to signed 16-bit integers.
y = (y * 32767.0).astype(np.int16)
wav.write(f"filtered-{args.wav}", fr, y)
