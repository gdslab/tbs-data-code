![Multispectral Orthomosaic](./images/ms_img.png)
<br><br>
This GitHub repository provides custom code for globally registering adjacent UAS (Uncrewed Aerial System) LiDAR-derived point clouds and generating CHMs (Canopy Height Models) from the point clouds. All code in this repository was developed to support the creation of high-quality, comprehensive UAS datasets of the Amazon rainforest, collected, processed, and publicly published by Purdue GDSLab (https://gdsl.org) and its collaborators. A detailed description of the code and the data is available **[HERE](URL_after_publication)** (_will linked after online publication_).

### Citation
- For DATA: You can download the data from a Data-to-Science (D2S) central STAC repository: [TBS STAC Catalog](https://stac.d2s.org/collections/20290e7b-cdb1-4f5e-bda3-fc9929169fb3)
  > Jung, M., Chang, A., Jung, J., Cannon, C., Rivas-Torres, G.  (2025). Comprehensive high-quality UAS data for Amazon rainforest: Tiputini Biodiversity Station. _Purdue Unversity Research Repository_. https://doi.org/10.4231/FV2H-VR18
- For METHOD
  > Jung, M., Chang, A., Cannon, C., Rivas-Torres, G., Jung, J. (_in press_). Comprehensive uncrewed aerial system data for Amazon rainforest at Tiputini Biodiversity Station, Ecuador, _Scientific Journal_

<br><br>
# PREPARATION
## System Environment Setup
Please set up a Conda environment or an equivalent system environment capable of running the released code. For those who prefer a containerized environment, the provided Dockerfile can be used to build a consistent runtime for these scripts. _Note that this code was initially developed and tested on **Linux Ubuntu 22.04.5 LTS.**_

## Data
- To run the **CHM generation code**, a point cloud file (_.las_ or _.laz_) is required. This point cloud **must** include normalized height information as an additional `HeightAboveGround` attribute. If you wish to use our data ([TBS dataset](https://stac.d2s.org/collections/20290e7b-cdb1-4f5e-bda3-fc9929169fb3)), please note that the dataset is voluminous due to its large spatial extent covering multiple biomes in the Amazon rainforest. Therefore, we recommend using cloud-optimized technologies, as our published data products are provided in cloud-optimized formats (COG and COPC), which are supported by most popular geospatial libraries. For convenience, we provide a **sample point cloud.las** `sample_for_chm_gen.las` to allow users to test the code.

- To run the **global registration** code, three types of data products are required: *point clouds, DTMs, and CHMs*, specifically from two adjacent areas with spatial overlap. Please refer to our [data description](URL_after_publication) (_will linked after online publication_) to understand the required data formats and the overall workflow. The DTMs and CHMs from the two adjacent regions **must** share the same spatial resolution.

- The provided codes are optimized for the coordinate reference system EPSG:32718, which is used at the Tiputini Biodiversity Station in the Ecuadorian Amazon. If your data use a different coordinate system, code modifications may be required.

<br><br>

# CODE EXECUTION
## CHM Generation Code
1. Prepare a point cloud (_see the **DATA** section_).
2. Copy (or download) `gen_chm.py` to your working directory.
3. Define the file paths and set the parameters in the code according to your requirements.

## Global Registration Code
This code is released with the intention of providing an alternative solution to address practical limitations that may be encountered by research groups with objectives similar to ours, namely conducting seamless large-area surveys using UAS.

To run the provided Global Registration code smoothly, users are expected to have an understanding of the methodological background underlying this approach, LiDAR products, geospatial data registration, and prior experience in developing and executing related code.
<br><br>
1. Prepare the data products (_see the **DATA** section_)

2. Copy (or download) all codes under the `global_registration` folder to your working directory.

3. Apply the `estimate_horizontal_shift` function to two adjacent CHMs. This function will estimate the global shifts (in the X and Y directions) between two UAS flights. _You **must** run the `mutual_information_2d` function together._

4. Apply the `transform_image_horizontal` function to the sensed CHM and the corresponding DTM using the estimated shifts.
   - The shifted CHM will be the aligned CHM with the reference CHM.

6. Apply the `estimate_vertical_shift` function to the reference DTM and the sensed, horizontally shifted DTM.

7. Apply the `transform_image_vertical` function to the sensed, horizontally shifted DTM.
   - The shifted DTM will be the final aligned DTM with the reference DTM.

9. Edit `point_cloud_shift.json` using all estimated shifts (from Steps **3** and **5**).

10. Run the PDAL pipeline using `point_cloud_shift.json`.
    - The shifted point cloud will be globally aligned with the reference point cloud.
```bash
pdal pipeline config.json
```
    
