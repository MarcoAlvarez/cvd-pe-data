# Important

D3 and GEOJSon do not get along very friendly.  While some other parsers are OK with winding orderings (CCW or CW), D3 seems to prefer the way Mapshaper used to output GeoJSON: CW rings, CCW holes, and bbox arrays that are always [xmin, ymin, xmax, ymax].  Default GeoJSON output now complies with RFC 7946 with respect to polygon winding order and antimeridian-crossing bounding boxes.  This means that space-enclosing rings are CCW and holes are CW.  This is the opposite of how mapshaper used to output polygon rings without the rfc7946 flag.

Using [mapshaper](https://mapshaper.org), we can transform the files using the following commmand:
```bash
# clean fixes geometry issues, simplify retains a percentage
# gj2008 sets the older ordering, precision sets the number of decimals,
# and format indicates the output file format
> mapshaper -clean rewind -simplify 10% -o gj2008 precision -0.0001 format geojson a.json
```