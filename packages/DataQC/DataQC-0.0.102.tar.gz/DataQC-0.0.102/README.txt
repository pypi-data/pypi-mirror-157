This package does summary analysis when data accepted from the client and compares the structure with the reference file. In many practical data science project we had to feed same structure data in the analysis process in regular interval. This package could be helpful for users to check the data structure before feed into the production process or somewhere else. 

## How to use:

import DataQC
from DataQC import Quick_QC
Quick_QC(INPUT_LOCATION,OUTPUT_LOCATION,REF_LOCATION,SEP)

## Inputs parameters

INPUT_LOCATION = Local folder where data saved.

OUTPUT_LOCATION = Local folder where the output will be saved.

REF_LOCATION = Local folder where reference files saved.

SEP = The separator between data columns.

## Outputs

In the output folder there will be several word files. Among them "Data QC summary" is the merged report using
all the word files availabe there.



