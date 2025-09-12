# CHM generation from high-quality UAS lidar data for Amazon
Purdue GDSLab (https://gdsl.org) and the collaborators collected, processed, and published high-quality, comprehensive UAS (Uncrewed Aerial System) data for the Amazon rainforest. This Git Hub repository provides an exemplary Python code to generate a CHM (Canopy Height Model) from the published lidar data (point cloud and DTM; Digital Terrain Model) based on a user-defined percentile value and spatial resolution.


## Code Implementation
**(1) Preparation**: Please download the point cloud from the [TBS STAC](https://stac.d2s.org/collections/20290e7b-cdb1-4f5e-bda3-fc9929169fb3) repository. We recommend checking *d2spy* if you are not interested in the entire TBS region. You can download the data only for your ROI (region of interest). Please check the guide at https://py.d2s.org.

**(2) Copy (or download) the `chm_generation.py`** to your workplace.

**(3) Set the parameters in the code** as you wish.


## Brief Data Description
We provide high-quality UAS data over **700-ha of Tiputini Biodiversity Station** (TBS, https://www.tiputini.com) in the Ecuadorian Amazon.
The dataset consists of:
- *Multispectral* orthomosaics (three RGB and four multispectral bands)  
- *Multispectral*-derived DSMs (Digital Surface Model)  
- *LiDAR* point clouds  
- *LiDAR*-derived DEMs (Digital Elevation Model; i.e., DTM, DSM, and CHMs)

**Data Repository**:
You can download the data from a Data-to-Science (D2S) central STAC repository: [TBS STAC Catalog](https://stac.d2s.org/collections/20290e7b-cdb1-4f5e-bda3-fc9929169fb3)

Please cite the information following when you use the data.
> Jung, M., Chang, A., Jung, J., Cannon, C., Rivas-Torres, G.  (2025). Comprehensive high-quality UAS data for Amazon rainforest: Tiputini Biodiversity Station. Purdue Unversity Research Repository. https://doi.org/10.4231/FV2H-VR18

