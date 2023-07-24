# Examples

* Produce a pdf visualization of the account graph specified in `mat_honan.txt`

   `agtool -i mat_honan.txt -o mat_honan.pdf`

* ... and highlight the vertex Amazon in the graph,

   `agtool -i mat_honan.txt -o mat_honan.pdf -t 'akv(color,"#FFFF55FF",Amazon)'`

   The value `#FFFF55FF` is the RGBA value for yellow, fully opaque.

* ... and remove type information from all vertices in the graph.

   `agtool -i mat_honan.txt -o mat_honan.pdf -t 'akv(_type,none,vertices())' -t 'akv(color,"#FFFF55FF",Amazon)'`


* Print all vertices

  `agtool -i mat_honan.txt -c vertices`

* Print the access base for Amazon

  `agtool -i mat_honan.txt -c "access_base(Amazon)"`

* Print what Amazon gives access to

  `agtool -i mat_honan.txt -c "gives_access_to(Amazon)"`

* Highlight in the pdf what Amazon gives access to

  `agtool -i mat_honan.txt -o mat_honan.pdf -t 'akv(color,"#FFFF55FF",gives_access_to(Amazon))'`

* Highlight in the pdf what Apple_Support, Amazon_Support, and billing_addr give access to

  `agtool -i mat_honan.txt -o mat_honan.pdf -t 'akv(color,"#FFFF55FF",gives_access_to(Apple_Support,Amazon_Support,billing_addr))'`