*Singularity instance based on [flywheel-apps/bxh-xcede-tools-qa](https://github.com/flywheel-apps/bxh-xcede-tools-qa)*

**DESCRIPTION**

Uses the [NITRC BXH/XCEDE Tools](https://www.nitrc.org/projects/bxh_xcede_tools/) to gather QA data, both  fmriqa_phantomqa.pl and fmriqa_generate.pl show an HTML page with images, graphs, and other data.

fmriqa_phantomqa.pl is used for the BIRN stability phantom and is the default use for this container

fmriqa_generate.pl can be used for human fMRI data

**INPUTS**

A directory of DICOM images.

**OUTPUT**

An HTML file, an XML Summary, and graphs/images. The HTML file contains the relevant information.

**OPTIONS**

Options are found in manifest.json. Includes whether to use phantom or human fMRI and the various choices for outputs.