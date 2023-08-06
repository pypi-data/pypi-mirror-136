# TF Hub Wrapper
<a href="https://github.com/alex-parisi/tfhub-styletransfer-wrapper/releases/tag/v1.1.0">
  <img alt="Latest Release" src="https://img.shields.io/github/v/release/alex-parisi/tfhub-styletransfer-wrapper">
</a>
<a href=#>
  <img alt="License" src="https://img.shields.io/github/license/alex-parisi/tfhub-styletransfer-wrapper">
</a>
<br>
This package contains functions to properly load and process images for input to Google's TensorFlow
Hub v2 model for fast arbitrary image style transfer and obtain a style-transferred output image.

<a href=#>
  <img alt="Example Output" src="https://drive.google.com/uc?id=1QhZpl_Uw6qvejbI4ALRz8ZLALR_vAvG2">
</a>

### Usage:
First, install the package with pip:
```
pip install tfhub-styletransfer-wrapper
```
Then import the package:
```
import tfhub-styletransfer-wrapper
```
And call the hub evaluation function:
```
stylehub = StyleHub('CPU')
stylehub.load_content(content_image_filename, 512)
stylehub.load_style(style_image_filename, 256)
stylized_image = stylehub.evaluate(True)
```
This will "re-draw" the input image specified by "input_image.jpg" in a style similar to that found in the image 
specified by "style_image.jpg".<br><br>Note that while different style sizes can be used, the TensorFlow Hub v2 model
was trained on 256x256 images, so increasing the style_size parameter any higher than 256 is not recommended.
<br><br>

### More examples
<a href=#>
  <img alt="Example Output" src="https://drive.google.com/uc?id=1_QpNmSEA49sN3H3mz9ypTpS9-HMXhLSP">
</a>
<a href=#>
  <img alt="Example Output" src="https://drive.google.com/uc?id=1XaOF502G5z1HEEGiQturTBFkZLPvBJLk">
</a>
