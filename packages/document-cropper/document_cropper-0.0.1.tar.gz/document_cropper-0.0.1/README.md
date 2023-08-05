<div id="top"></div>

<!-- PROJECT LOGO -->
<br />
<div align="center">

  <h3 align="center">Document-Cropper</h3>

  <p align="center">
    Python document cropper which can be applied to images.
    <br />
    <br />
  </p>
</div>



<!-- ABOUT THE PROJECT -->
## About The Project

There are a several articles and GitHub repos dedicated to document segmentation; however, I didn't find one that worked right out of the box, so I created this one. It can be used for preprocessing document images for further text recognition on them or for saving them in proper format.




### Built With

* [NumPy](https://numpy.org/)
* [SciPy](https://scipy.org/)
* [scikit-image](https://scikit-image.org/)
* [Matplotlib](https://matplotlib.org/)




<!-- GETTING STARTED -->
## Installation

This project can be easily installed via pip

  ```sh
  pip install document-cropper
  ```




<!-- USAGE EXAMPLES -->
## Usage

```Python
import document_cropper as dc
```

To crop image you should use:
```Python
dc.crop_image("path_to_example.jpg", "name_for_the_result.jpg")
```

If you want to see all stages of processing you can use:
```Python
# Save the stages as image
dc.crop_image_pipeline("path_to_example.jpg", "name_for_the_result.jpg")

# Show the stages as matplotlib figure
dc.crop_image_pipeline("path_to_example.jpg")
```

_For more examples, please refer to the [Documentation](https://github.com/KKroliKK/document-cropper)_

<p align="right">(<a href="#top">back to top</a>)</p>