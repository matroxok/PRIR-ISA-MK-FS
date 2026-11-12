from __future__ import annotations

import argparse
import multiprocessing as mp
from typing import List, Sequence, Tuple

import numpy as np
from PIL import Image


FragmentTask = Tuple[int, np.ndarray, int, int]
FragmentResult = Tuple[int, np.ndarray]


def to_grayscale(image_array: np.ndarray) -> np.ndarray:
    """Konwersja RGB/RGBA do skali szarosci (uint8)."""
    if image_array.ndim == 2:
        return image_array.astype(np.uint8, copy=False)

    rgb = image_array[..., :3].astype(np.float32)
    # Standardowa luminancja: Y = 0.299R + 0.587G + 0.114B
    gray = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    return np.clip(gray, 0, 255).astype(np.uint8)


def edge_filter(fragment: np.ndarray) -> np.ndarray:
    """Wlasna implementacja filtru Sobela oparta o NumPy."""
    gray = to_grayscale(fragment)
    h, w = gray.shape

    gx_kernel = np.array(
        [[-1, 0, 1],
         [-2, 0, 2],
         [-1, 0, 1]],
        dtype=np.float32,
    )
    gy_kernel = np.array(
        [[1, 2, 1],
         [0, 0, 0],
         [-1, -2, -1]],
        dtype=np.float32,
    )

    padded = np.pad(gray, pad_width=1, mode="edge").astype(np.float32)
    gx = np.zeros((h, w), dtype=np.float32)
    gy = np.zeros((h, w), dtype=np.float32)

    for ky in range(3):
        for kx in range(3):
            window = padded[ky:ky + h, kx:kx + w]
            gx += gx_kernel[ky, kx] * window
            gy += gy_kernel[ky, kx] * window

    magnitude = np.hypot(gx, gy)
    max_val = float(magnitude.max())
    if max_val > 0:
        magnitude = (magnitude / max_val) * 255.0

    return np.clip(magnitude, 0, 255).astype(np.uint8)


def split_image(image_array: np.ndarray, n_fragments: int, overlap: int = 1) -> List[FragmentTask]:
    """Dzieli obraz na poziome pasy z nakladaniem (halo) 1 px dla poprawnych krawedzi."""
    if n_fragments < 1:
        raise ValueError("Liczba fragmentow musi byc >= 1")

    h = image_array.shape[0]
    n_fragments = min(n_fragments, h)

    base = h // n_fragments
    remainder = h % n_fragments

    tasks: List[FragmentTask] = []
    start = 0

    for idx in range(n_fragments):
        chunk = base + (1 if idx < remainder else 0)
        end = start + chunk

        ext_start = max(0, start - overlap)
        ext_end = min(h, end + overlap)

        crop_top = start - ext_start
        crop_bottom = crop_top + chunk

        fragment = image_array[ext_start:ext_end, :]
        tasks.append((idx, fragment, crop_top, crop_bottom))
        start = end

    return tasks


def process_fragment(task: FragmentTask) -> FragmentResult:
    idx, fragment, crop_top, crop_bottom = task
    filtered = edge_filter(fragment)
    core = filtered[crop_top:crop_bottom, :]
    return idx, core


def merge_fragments(results: Sequence[FragmentResult]) -> np.ndarray:
    ordered = [arr for _, arr in sorted(results, key=lambda x: x[0])]
    return np.vstack(ordered)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rownolegle przetwarzanie obrazu (Sobel + multiprocessing.Pool)."
    )
    parser.add_argument("input", help="Sciezka do obrazu wejsciowego")
    parser.add_argument("output", help="Sciezka do obrazu wyjsciowego")
    parser.add_argument(
        "--workers",
        type=int,
        default=mp.cpu_count(),
        help="Liczba procesow w puli (domyslnie: liczba rdzeni CPU)",
    )
    parser.add_argument(
        "--fragments",
        type=int,
        default=0,
        help="Liczba fragmentow obrazu (0 = tyle co workers)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    workers = max(1, args.workers)

    image = Image.open(args.input)
    image_array = np.array(image)

    n_fragments = args.fragments if args.fragments > 0 else workers
    tasks = split_image(image_array, n_fragments=n_fragments, overlap=1)

    with mp.Pool(processes=workers) as pool:
        results = pool.map(process_fragment, tasks)

    merged = merge_fragments(results)
    output_image = Image.fromarray(merged, mode="L")
    output_image.save(args.output)

    print(f"Zakonczono. Zapisano wynik do: {args.output}")


if __name__ == "__main__":
    main()
