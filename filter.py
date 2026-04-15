import sys
import numpy as np
import scipy.io.wavfile as wav

name = sys.argv[1]

# Read the file into x yielding frame rate fr (samples/sec).
(fr, x) = wav.read(name)
# Convert to float samples, single channel, scaled to -1..1.
x = np.mean(x.astype(np.float32), axis=1) / 32768.0

# Do the convolution explicitly this way. Very slow.
# y = np.array([1.0 * x[i] - 0.5 * x[i-1] for i in range(1, len(x))], dtype=np.float32)

# Do the convolution with numpy. Much faster.
a = np.array([0.5, 0.5])
y = np.convolve(x, a)

# Convert the output to signed 16-bit integers.
y = (y * 32767.0).astype(np.int16)
wav.write(f"filtered-{name}", fr, y)
