import argparse, sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal

# Figure out the `cheby2()` stopband edge from the passband edge.
# Thanks to Google Gemini.
def get_cheby2_stopband_edge(target_wp, order, rs, gpass):
    """
    Calculates the Wn needed to make the passband end at target_wp.
    `gpass` is loss at passband in dB.
    """
    # Pre-calculate the shift factor based on Chebyshev math
    arg = np.sqrt((10**(rs/10) - 1) / (10**(gpass/10) - 1))
    factor = np.cosh(1/order * np.acosh(arg))
    
    # Calculate Wn (Stopband Edge)
    wn = target_wp * factor
    assert wn < 0.99 # Ensure it stays below Nyquist
    return wn

ap = argparse.ArgumentParser()
ap.add_argument("--order", type=int)
ap.add_argument("--cutoff", type=float)
ap.add_argument("--transition", type=float)
ap.add_argument("--stop-db", type=float)
ap.add_argument("--pass-db", type=float, default = 6)
ap.add_argument("--algorithm", choices=["ma", "firwin", "remez", "cheby2"])
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
elif args.algorithm == "remez":
    tstart = args.cutoff - args.transition / 2
    tend = args.cutoff + args.transition / 2
    a = signal.remez(args.order, [0, tstart / 2, tend / 2, 0.5], [1, 0])
elif args.algorithm == "cheby2":
    assert args.cascade == 1
    tend = get_cheby2_stopband_edge(
        args.cutoff,
        args.order,
        args.stop_db,
        gpass = args.pass_db,
    )
    sos = signal.cheby2(args.order, args.stop_db, tend, output='sos')
else:
    assert False, "unknown algorithm"

if args.plot:
    if args.algorithm == "cheby2":
        w, mag = signal.sosfreqz(sos)
    else:
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

if args.algorithm == "cheby2":
    y = signal.sosfilt(sos, x)
else:
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
