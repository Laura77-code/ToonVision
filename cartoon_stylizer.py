import argparse
from pathlib import Path

import cv2
import numpy as np


def cartoonize_image(
    image: np.ndarray,
    median_ksize: int = 5,
    adaptive_block_size: int = 9,
    adaptive_c: int = 9,
    bilateral_d: int = 9,
    bilateral_sigma_color: int = 250,
    bilateral_sigma_space: int = 250,
    color_levels: int = 8,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert an image into a cartoon-like rendering using classical OpenCV operations.

    Steps:
    1) Smooth the image while preserving major edges.
    2) Detect bold edges from a grayscale version.
    3) Reduce the number of colors (posterization effect).
    4) Combine simplified colors with the edge mask.

    Returns:
        cartoon: final cartoon-style image
        edges: binary edge map
        quantized: color-simplified image before edge combination
    """
    if image is None:
        raise ValueError("Input image is None. Check the file path.")

    # 1. Grayscale + median blur for more stable edge extraction.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, median_ksize)

    # 2. Adaptive threshold gives bold black/white edges.
    # Block size must be odd and greater than 1.
    if adaptive_block_size % 2 == 0:
        adaptive_block_size += 1
    adaptive_block_size = max(3, adaptive_block_size)

    edges = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        adaptive_block_size,
        adaptive_c,
    )

    # 3. Bilateral filtering smooths colors without destroying strong edges.
    smooth = cv2.bilateralFilter(
        image,
        bilateral_d,
        bilateral_sigma_color,
        bilateral_sigma_space,
    )

    # 4. Color quantization: reduce the number of available intensity values.
    # This creates flatter cartoon-like color regions.
    divisor = max(1, 256 // max(2, color_levels))
    quantized = (smooth // divisor) * divisor + divisor // 2
    quantized = np.clip(quantized, 0, 255).astype(np.uint8)

    # 5. Apply the edge mask to keep bold outlines.
    cartoon = cv2.bitwise_and(quantized, quantized, mask=edges)

    return cartoon, edges, quantized


def make_comparison_canvas(
    original: np.ndarray,
    quantized: np.ndarray,
    edges: np.ndarray,
    cartoon: np.ndarray,
) -> np.ndarray:
    """Create a 2x2 comparison panel for README screenshots or debugging."""
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    def add_label(img: np.ndarray, text: str) -> np.ndarray:
        out = img.copy()
        cv2.rectangle(out, (0, 0), (260, 42), (255, 255, 255), -1)
        cv2.putText(
            out,
            text,
            (10, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
        return out

    tl = add_label(original, "Original")
    tr = add_label(quantized, "Color Simplified")
    bl = add_label(edges_bgr, "Detected Edges")
    br = add_label(cartoon, "Final Cartoon")

    top = np.hstack([tl, tr])
    bottom = np.hstack([bl, br])
    return np.vstack([top, bottom])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert all images in a directory into cartoon-like renderings using OpenCV."
    )
    parser.add_argument(
        "input_dir", type=str, help="Directory containing input images"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Directory where results will be saved",
    )
    parser.add_argument(
        "--median-ksize", type=int, default=5, help="Median blur kernel size"
    )
    parser.add_argument(
        "--adaptive-block-size",
        type=int,
        default=9,
        help="Adaptive threshold block size (odd number)",
    )
    parser.add_argument(
        "--adaptive-c",
        type=int,
        default=9,
        help="Adaptive threshold constant C",
    )
    parser.add_argument(
        "--bilateral-d",
        type=int,
        default=9,
        help="Neighborhood diameter for bilateral filter",
    )
    parser.add_argument(
        "--bilateral-sigma-color",
        type=int,
        default=250,
        help="Sigma color for bilateral filter",
    )
    parser.add_argument(
        "--bilateral-sigma-space",
        type=int,
        default=250,
        help="Sigma space for bilateral filter",
    )
    parser.add_argument(
        "--color-levels",
        type=int,
        default=8,
        help="Approximate number of discrete color levels",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display original/result windows before exiting",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found or is not a directory: {input_dir}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Supported image extensions
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    
    # Process each image in the input directory
    image_files = [f for f in input_dir.iterdir() if f.suffix.lower() in valid_extensions]
    
    if not image_files:
        print(f"No images found in {input_dir}")
        return

    print(f"Found {len(image_files)} images. Starting processing...")

    for input_path in image_files:
        print(f"\nProcessing: {input_path.name}")
        image = cv2.imread(str(input_path))
        if image is None:
            print(f"Skipping {input_path.name}: Could not read image.")
            continue

        cartoon, edges, quantized = cartoonize_image(
            image=image,
            median_ksize=args.median_ksize,
            adaptive_block_size=args.adaptive_block_size,
            adaptive_c=args.adaptive_c,
            bilateral_d=args.bilateral_d,
            bilateral_sigma_color=args.bilateral_sigma_color,
            bilateral_sigma_space=args.bilateral_sigma_space,
            color_levels=args.color_levels,
        )

        base_name = input_path.stem
        ext = ".png"

        cartoon_path = output_dir / f"{base_name}_cartoon{ext}"
        edges_path = output_dir / f"{base_name}_edges{ext}"
        quantized_path = output_dir / f"{base_name}_simplified{ext}"
        comparison_path = output_dir / f"{base_name}_comparison{ext}"

        cv2.imwrite(str(cartoon_path), cartoon)
        cv2.imwrite(str(edges_path), edges)
        cv2.imwrite(str(quantized_path), quantized)
        comparison = make_comparison_canvas(image, quantized, edges, cartoon)
        cv2.imwrite(str(comparison_path), comparison)

        print(f"Saved results for {input_path.name}")

    if args.show and len(image_files) > 0:
        print("\nDisplaying the last processed image. Press any key to close.")
        cv2.imshow("Original", image)
        cv2.imshow("Cartoon", cartoon)
        cv2.imshow("Edges", edges)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
