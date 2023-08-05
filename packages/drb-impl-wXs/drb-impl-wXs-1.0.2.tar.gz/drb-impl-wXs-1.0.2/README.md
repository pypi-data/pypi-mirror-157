# WXS implementation
This drb-impl-wXs module implements the OWS services (WFS, WMS, WCS, ...). 
For more information about OWS Service see https://www.ogc.org/ or/and
https://www.ogc.org/standards/wms
OGC catalog, this implementation is abstract, it means that to have a usable 
OWS service implementation, we have to create an implementation for this service 
dependent on this abstract implementation.
Sot have a signature, its derived implementations will have to define one

# Nodes
### WXSServiceNode
Abstract, have to be derived.
Represents the WXS service (like WMS, WCS, ...). This node has no attribute and
has as children request (like GetMap) WXsOperationNode and other children that
define the Service as XmlNode

### WXSNodeOperation
Represents an operation than can be used on the service.


# Installation
```
pip install drb-impl-wxs
```
# Usages

To implement an OWS Web Service, we have to create a class based on  WXSServiceNode
and define at least the read_capabilities method.

```python
class WmsServiceNode(WXSServiceNode):
    ...
    def read_capabilities(self, node_capabilities):
        ....
    
```


After we can use this node like other DRB Node
The operation of service are available across the children of the node service,
See drb_impl_wms or drb_impl_wcs for more information.

Example with a drb_impl_wms impl


```python

url_wms='https+wms://wms.fr/geoserver/demo/wms?'

# The service use a special
service_wms = WmsServiceNode(url_wms)

dict_request = {'layers': 'mgrs_region', 
                'format': 'image/png', 
                'height': 256, 
                'width': 256, 
                'crs': 'EPSG:3857', 
                'bbox': '7514065.628545968,7514065.628545967,10018754.171394622,10018754.171394628'}

get_map = service_wms['GetMap'][dict_request]

print('----------------------------------------')
print('GetMap : with parameter return image')
print(get_map)
# => return an drb image 

# url of request
# https://wms.fr/geoserver/demo/wms?
# &service=WMS&
# request=GetMap&
# layers=mgrs_region&
# format=image%2Fpng&
# crs=EPSG%3A3857&
# bbox=7514065.628545968,7514065.628545967,10018754.171394622,10018754.171394628

```

Example with a drb_impl_wcs impl

```python

url_wcs='https+wcs://wcs/mapserv'

# The service use a special
service_wcs = WcsServiceNode(url_wcs, auth=None, map='/map/nitrogen.map')


# SUBSET is use twice with two values, we use a list to in dict 
dict_request = {'COVERAGEID': 'nitrogen_5-15cm_Q0.5',
                'VERSION': '2.0.1',
                'SUBSET': ['X(-1784000,-1140000)', 'Y(1356000,1863000)'],
                'FORMAT': 'GEOTIFF_INT16',
                'SUBSETTINGCRS': 'http://www.opengis.net/def/crs/EPSG/0/152160',
                'OUTPUTCRS': 'http://www.opengis.net/def/crs/EPSG/0/152160'
                }

get_map = service_wcs['GetCoverage'][dict_request]
# url of request
# https://wcs/mapserv?
# map=%2Fmap%2Fnitrogen.map&
# SERVICE=WCS&VERSION=2.0.1&
# REQUEST=GetCoverage&
# COVERAGEID=nitrogen_5-15cm_Q0.5&
# FORMAT=GEOTIFF_INT16&
# SUBSET=X(-1784000%2C-1140000)&SUBSET=Y(1356000%2C1863000)&
# SUBSETTINGCRS=http%3A%2F%2Fwww.opengis.net%2Fdef%2Fcrs%2FEPSG%2F0%2F152160&
# OUTPUTCRS=http%3A%2F%2Fwww.opengis.net%2Fdef%2Fcrs%2FEPSG%2F0%2F152160
# => return the image

```






