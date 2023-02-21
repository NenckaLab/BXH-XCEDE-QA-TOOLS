#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Generate file metadata (file.info) from STATS json file, as output
# from the BXH tool. Also sets the classification (file.measurements) from the
# input config.json file, as provided by Flywheel.
#
# @LMPERRY, 6/2018
#

import os
import re
import json
import logging
import datetime
logging.basicConfig()
log = logging.getLogger('metadata')


# Generate metadata
def metadata_gen(config_file, qa_stats_file):
    """Generate file metadata.

    Builds file.info from QA json file, as output from bxhtools code.
    Also sets the classification (file.measurements) from the input
    config.json file, as provided by Flywheel, and file.type from the ext.

    Args:
        config_file:      Path to config.json file.
        qa_stats_file:    Path to qa stats file.


    Returns:
        metadata_file: Path to .metadata.json file.

    """
    outbase = '/flywheel/v0/output'
    output_files = os.listdir(outbase)
    files = []
    if len(output_files) > 0:

        # Read the config
        (config, modality, classification) = ([], None, [])
        if config_file.endswith('config.json'):
            with open(config_file) as config_f:
                config = json.load(config_f, strict=False)
            try:
                classification = config['inputs']['fmri_input']['object']['classification']
            except:
                log.info('  Cannot determine classification from config.json.')
            try:
                modality = config['inputs']['fmri_input']['object']['modality']
            except:
                log.info('  Cannot determine modality from config.json.')
        else:
            log.info('  No config file was found. Classification will not be set for outputs!')

        for f in output_files:
            if os.path.isfile(os.path.join(outbase, f)):
                fdict = {}
                fdict['name'] = f
                fdict['classification'] = classification

                # Get the QA info associated with this file
                if qa_stats_file and os.path.isfile(qa_stats_file):
                    with open(qa_stats_file) as qa_f:
                        qa_info = json.load(qa_f, strict=False)

                    # Add qa_info to info key
                    fdict['info'] = qa_info

                # Append this file dict to the list
                files.append(fdict)

        # Collate the metadata and write to file
        metadata = {}
        metadata['acquisition'] = {}
        metadata['acquisition']['files'] = files
        metadata_file = os.path.join(outbase, '.metadata.json')
        with open(metadata_file, 'w') as metafile:
            json.dump(metadata, metafile)

    return metadata_file


if __name__ == '__main__':
    """
    Generate file metadata (file.info), type (file.type), name (file.name) and
    classification (file.measurements) for each file in <outdir>.
    """

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('config_file', help='Full path to config_file')
    ap.add_argument('qa_stats_file', nargs='?', help='root path to qa file ')
    args = ap.parse_args()

    logging.getLogger('metadata').setLevel(logging.INFO)
    log.info('  job start: %s' % datetime.datetime.utcnow())

    # Generate metadata
    metadata_file = metadata_gen(args.config_file, args.qa_stats_file)

    log.info('  job stop: %s' % datetime.datetime.utcnow())

    if metadata_file:
        log.info('  generated %s' % metadata_file)
    else:
        log.info('  Failed.')
