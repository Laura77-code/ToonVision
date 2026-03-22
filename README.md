# ToonVision

ToonVision is a computer vision project built with OpenCV that converts ordinary images into cartoon-style renderings using classical image processing techniques. The pipeline combines edge extraction, noise reduction, and color smoothing to simplify visual details and create a cartoon-like effect while preserving the main structure of the original image. This project was developed to explore non-deep-learning approaches for image stylization through traditional computer vision methods.

---

## **Technical Breakdown: How Parameters Affect the Image**

To achieve these different styles, the algorithm manipulates four key stages of the Computer Vision pipeline:

### **1. Mathematical Intuition: Contrast & Brightness**
The core of image transformation can be expressed as:
**$g(x,y) = \alpha \cdot f(x,y) + \beta$**

- **$\alpha$ (Gain/Contrast)**: Multiplies the pixel values. $\alpha > 1$ increases contrast, making edges easier for the `adaptiveThreshold` to find.
- **$\beta$ (Bias/Brightness)**: Adds a constant value. In our code, the `--adaptive-c` parameter acts as a bias that shifts the threshold, helping to clean noise in dark areas.

```text
Contrast (α) Effect:           Brightness (β) Shift:
      ^                              ^
      |     / (α > 1)                |    / (Original)
      |    /                         |   /  
      |   / (Original)               |  /--- (Shifted β)
      +-----------> Source           +-----------> Source
```

### **2. Pre-processing (Noise Reduction)**
- **`--median-ksize`**: This uses a **Median Filter**. It is the first line of defense against "salt-and-pepper" noise.
  - *Small (3-5)*: Keeps fine details but might leave some noise.
  - *Large (7+)*: Aggressively cleans the image, which is essential for low-light photos (Kitten).

### **3. Edge Extraction (Adaptive Thresholding)**
- **`--adaptive-block-size`**: Determines the neighborhood area for the threshold.
  - *Small (3-5)*: Captures micro-details like whiskers.
  - *Large (11+)*: Creates bolder, thicker outlines.
- **`--adaptive-c`**: Acts as the $\beta$ bias in our thresholding math.

### **4. Pipeline Logic Flow**
```text
[ Input Image ] 
      |
      v
[ Grayscale + Median Blur ]  <-- Removes noise (Step 1)
      |
      v
[ Adaptive Thresholding ]    <-- Creates Edge Mask (Step 2)
      |
      +--------------------------+
      |                          |
      v                          v
[ Bilateral Filter ]       [ Color Quantization ] <-- Smooths & Simplifies (Step 3 & 4)
      |                          |
      +------------+-------------+
                   |
                   v
        [ Bitwise AND Masking ]    <-- Combines Edges + Colors
                   |
                   v
           [ Final Cartoon ]
```

---

## **Style Recipes & Commands**

To reproduce the results shown above, you can use the following "recipes" by adjusting the command-line parameters.

### **1. Default Style**
*Balanced settings for standard photos.*
```bash
python cartoon_stylizer.py Inputs/ --output-dir outputs_default
```

### **2. Bold Comic Style**
*Thick outlines and flat, vibrant colors (Great for Harry Potter/Superman).*
```bash
python cartoon_stylizer.py Inputs/ \
  --output-dir outputs_bold_comic \
  --adaptive-block-size 11 \
  --adaptive-c 7 \
  --bilateral-sigma-color 220 \
  --color-levels 6
```

### **3. Ultra-Sensitive Style**
*Forces edge detection on dark or low-contrast images (Used for the Kitten).*
```bash
python cartoon_stylizer.py Inputs/ \
  --output-dir outputs_ultra_sensitive \
  --median-ksize 3 \
  --adaptive-block-size 3 \
  --adaptive-c -1 \
  --bilateral-d 15 \
  --bilateral-sigma-color 150 \
  --color-levels 12
```

### **4. Painterly Smooth (Masterpiece)**
*Aggressive noise reduction for an artistic, hand-painted look (Best for noisy photos).*
```bash
python cartoon_stylizer.py Inputs/ \
  --output-dir outputs_painterly_smooth \
  --median-ksize 7 \
  --adaptive-block-size 9 \
  --adaptive-c 1 \
  --bilateral-sigma-color 300 \
  --color-levels 7
```

---

## Repository name suggestion

**ToonVision**

This name is specific and cleaner than generic names such as `hw2`, `cv_homework2`, or `cartoon_hw`, which the slides explicitly discourage. The slides also require a repository description. Example: **"OpenCV cartoon rendering for turning photos into simple cartoon-style images."** fileciteturn0file0

---

## What this program does

The program takes an input image and applies a cartoon-style rendering pipeline:

1. Convert the image to grayscale.
2. Apply median blur to reduce small noise.
3. Extract strong edges using adaptive thresholding.
4. Smooth colors using bilateral filtering.
5. Reduce color complexity with simple color quantization.
6. Combine the simplified colors with the edge mask.


---

## Project structure

```text
ToonVision/
├── cartoon_stylizer.py
├── requirements.txt
├── .gitignore
├── README.md
├── Inputs/
│   ├── gato.jpeg
│   ├── harry.webp
│   ├── input.jpeg
│   └── superman.webp
└── outputs_default/
```

---

## Requirements

- Python 3.10+
- OpenCV
- NumPy

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## How to run

The program now processes all images within a specified directory.

Basic example (processes all images in `Inputs/`):

```bash
python cartoon_stylizer.py Inputs/ --output-dir outputs
```

Show windows for the last processed image:

```bash
python cartoon_stylizer.py Inputs/ --output-dir outputs --show
```

Try stronger / different effects:

```bash
python cartoon_stylizer.py Inputs/ \
  --output-dir outputs \
  --adaptive-block-size 11 \
  --adaptive-c 7 \
  --bilateral-sigma-color 220 \
  --bilateral-sigma-space 220 \
  --color-levels 6
```

---

## Output files

For each input image in the directory (e.g., `gato.jpeg`), the program saves:

- `outputs/cat_cartoon.png` → final cartoon result
- `outputs/cat_edges.png` → detected edge map
- `outputs/cat_simplified.png` → color-simplified image
- `outputs/cat_comparison.png` → 2x2 comparison panel for presentation 

---

## Advanced Customization: Default vs. Strong Effects

The algorithm's appearance can be drastically changed by adjusting the command-line arguments. This section explains how these parameters affect the computer vision pipeline.

### **Parameter Breakdown**
- `--color-levels`: Controls the "Posterization" effect. Lower values (e.g., 6) result in fewer, flatter color regions, giving a more hand-drawn look.
- `--adaptive-block-size`: Controls the thickness of the outlines. A larger block size (e.g., 11) creates bolder, more dramatic edges.
- `--bilateral-sigma-*`: Controls how much the colors are smoothed while preserving edges. Higher values remove more fine-grain texture noise.

### **Side-by-Side Comparison**

| Subject | Default Results | Bold Comic Effects (Bolder & Flatter) |
| :--- | :--- | :--- |
| **Harry Potter** | ![Default](outputs_default/harry_comparison.png) | ![Strong](outputs_bold_comic/harry_comparison.png) |
| **Superman** | ![Default](outputs_default/superman_comparison.png) | ![Strong](outputs_bold_comic/superman_comparison.png) |
| **Busy Landscape**| ![Default](outputs_default/input_comparison.png) | ![Strong](outputs_bold_comic/input_comparison.png) |
| **Kitten (Low Light)**| ![Default](outputs_default/cat_comparison.png) | ![Strong](outputs_bold_comic/cat_comparison.png) |

### **Analysis of Bold Comic Effects**
Using the command below, we can achieve a much more stylized "comic book" aesthetic:

```bash
python cartoon_stylizer.py Inputs/ \
  --output-dir outputs_bold_comic \
  --adaptive-block-size 11 \
  --adaptive-c 7 \
  --bilateral-sigma-color 220 \
  --bilateral-sigma-space 220 \
  --color-levels 6
```

- **Why it looks "better" for portraits**: In the Harry Potter and Superman examples, the **bolder edges** (`block-size 11`) help define the silhouette against the background, and the **reduced colors** (`levels 6`) hide subtle skin gradients, making it look like a drawing rather than a filtered photo.

### **Case Study: Evolution of the "Kitten" (Low-Contrast Challenge)**

The image of the kitten is our most difficult case due to low light and noise. Here is how different CV strategies impact the final result:

| Strategy | Result | Analysis |
| :--- | :--- | :--- |
| **1. Default** | ![Default](outputs_default/cat_comparison.png) | **Failure**: The contrast is too low for default settings. The edge map is blank. |
| **2. Ultra-Sensitive** | ![Ultra](outputs_ultra_sensitive/cat_comparison.png) | **Improvement**: Forces detection of whiskers and eyes using negative `adaptive-c`. |
| **3. Painterly Smooth** | ![Painterly](outputs_painterly_smooth/cat_comparison.png) | **Best for Kitten**: Heavy cleaning of noise creates a clean, artistic illustration. |

#### **The Parameter Trade-off (Visual Comparison)**
It is important to note that **there is no "one-size-fits-all" command**. A configuration that fixes a noisy image might degrade a high-quality one.

| Subject | Default (Ideal) | Painterly Smooth (Over-smoothed) |
| :--- | :--- | :--- |
| **Harry Potter** | ![Default](outputs_default/harry_comparison.png) | ![Masterpiece](outputs_painterly_smooth/harry_comparison.png) |
| **Analysis** | Sharp edges, clear facial details, and balanced colors. | **Issue**: The high `median-ksize (7)` and `bilateral-sigma (300)` blur out the fine details of the face and wand. |

- **Conclusion**: Classical Computer Vision requires parameter tuning based on the specific characteristics (lighting, noise, detail) of the input image. Low-light photos (Kitten) need heavy smoothing, while high-quality portraits (Harry) need sharper edge detection.

---